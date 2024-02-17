import click
from databricks import sql
import json
import hashlib
import hmac
import base64
import requests
from datetime import datetime
import pytz
from typing import List, Tuple
import os
from airflow.hooks.base_hook import BaseHook
import logging
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

@click.command()
@click.option('--env', default='databricks')
@click.option('--dwhcid', default='databricks_connection')
@click.option('--azmonitorcid', default='azure_monitor')
def dbtlog(env,dwhcid,azmonitorcid):
   
   az_conn = BaseHook.get_connection(str(azmonitorcid))
   azure_monitor_extras_dict = json.loads(az_conn.get_extra())
   client_secret = str(az_conn.password)
   client_id = str(az_conn.login)
   
   workspace_id = str(azure_monitor_extras_dict['workspace_id'])
   primary_key = str(azure_monitor_extras_dict['primary_key'])
   tenant_id = str(azure_monitor_extras_dict['tenant_id'])
   

   if(env == "databricks"):
        conn = BaseHook.get_connection(str(dwhcid))
        databricks_extras_dict = json.loads(conn.get_extra())
        connection_string = str(conn.host)
        token = str(conn.password)
        http_path = str(databricks_extras_dict["http_path"])
        schema = str(conn.schema)

        connection = sql.connect(
                           server_hostname = connection_string,
                           http_path = http_path,
                           access_token = token)
        cursor = connection.cursor()
        table_prefix = schema


   if(env == "snowflake"):
        snowflake_conn = BaseHook.get_connection(str(dwhcid))
        e1xtras_dict = json.loads(snowflake_conn.get_extra())
        engine = create_engine(URL(
            account = str(e1xtras_dict['account']),
            user = str(snowflake_conn.login),
            password = str(snowflake_conn.password),
            database = str(e1xtras_dict['database']),
            schema = str(snowflake_conn.schema),
            warehouse = str(e1xtras_dict['warehouse']),
            role= str(e1xtras_dict['role']),
        ))

        table_prefix=str(e1xtras_dict['database'])+"."+str(snowflake_conn.schema)
        cursor = engine.connect()
        

   auth_token = get_auth_toke_azure_monitor(tenant_id, client_id, client_secret)
   last_triggered_time = get_query_result(workspace_id, auth_token)
   print(last_triggered_time)
   if(last_triggered_time != "null"):
    cursor.execute(f"select command_invocation_id from {table_prefix}.invocations where run_started_at > '{last_triggered_time}'")
    invocation_id = json.dumps(cursor.fetchall())
    json_obj = json.loads(invocation_id)
    flatten_ids = [item[0] for item in json_obj]
    flatten_ids_str = ', '.join([f"'{val}'" for val in flatten_ids])
   else:
    cursor.execute(f"select command_invocation_id from {table_prefix}.invocations")
    invocation_id = json.dumps(cursor.fetchall())
    json_obj = json.loads(invocation_id)
    flatten_ids = [item[0] for item in json_obj]
    flatten_ids_str = ', '.join([f"'{val}'" for val in flatten_ids])
   print(flatten_ids_str)
   if(len(flatten_ids_str)==0):
        cursor.close()
        connection.close()
        print("No Records found to insert")
        return 
   results = []

#    print(f"select * from `model_executions` WHERE node_id NOT LIKE 'model.dbt_artifacts%' and run_started_at > '{execution_start_date}'") 
   cursor.execute(f"select * from {table_prefix}.model_executions WHERE node_id NOT LIKE 'model.dbt_artifacts%' and command_invocation_id in ({flatten_ids_str})")
   results.append(list_to_dict(cursor.fetchall(),cursor.description))

   cursor.execute(f"select * from {table_prefix}.seed_executions WHERE node_id NOT LIKE 'model.dbt_artifacts%' and command_invocation_id in ({flatten_ids_str})")
   results.append(list_to_dict(cursor.fetchall(),cursor.description))

   cursor.execute(f"select * from {table_prefix}.test_executions WHERE node_id NOT LIKE 'model.dbt_artifacts%' and command_invocation_id in ({flatten_ids_str})")
   results.append(list_to_dict(cursor.fetchall(),cursor.description))

   cursor.execute(f"select * from {table_prefix}.snapshot_executions WHERE node_id NOT LIKE 'model.dbt_artifacts%' and command_invocation_id in ({flatten_ids_str})")
   results.append(list_to_dict(cursor.fetchall(),cursor.description))

   flattened_list = [item for sublist in results for item in sublist]

   results_json = json.dumps(flattened_list, indent=2)

   invocation_result = []
   cursor.execute(f"select * from {table_prefix}.invocations where command_invocation_id in ({flatten_ids_str})")
   invocation_result.append(list_to_dict(cursor.fetchall(),cursor.description))
   flattened_list_invocation = [item for sublist in invocation_result for item in sublist]
   invocation_results_json = json.dumps(flattened_list_invocation, indent=2)
   cursor.close()
   connection.close()

   send_custom_data("dbtlogs",results_json,workspace_id,primary_key)
   send_custom_data("invocationlogs1",invocation_results_json,workspace_id,primary_key)

def list_to_dict(list, description: List[Tuple]):
    result = []
    for row in list:
      result_dict = {}
      for i, column in enumerate(description):
         result_dict[column[0]] = str(row[i])
      result.append(result_dict)
    return result

def get_last_logged_time(workspace_id,primary_key):
    server_time_string = get_server_time()
    signature = get_request_signature(server_time_string,"",workspace_id,"bsQgCl3L//hNfHJHYi5Eurqx1OcHfkGYbbj3X6UBgD5AFXSkNT6EsQ/MZsy/VAqM6sW7fzkf9rdO5nY13kT3nA==")
    url = f"https://{workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"

def send_custom_data(log_name, data,workspace_id,primary_key):
    json_request_data = data
    server_time_string = get_server_time()
    signature = get_request_signature(server_time_string, json_request_data,workspace_id,primary_key)
    url = f"https://{workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
    headers = {
        "Authorization": signature,
        "Content-Type": "application/json",
        "Log-Type": log_name,
        "x-ms-date": get_x_ms_date(),
        "time-generated-field": "LogGeneratedTime",
    }
    try:
        response = requests.post(url, headers=headers, data=json_request_data)
        status_code = response.status_code
        print(status_code)
        if status_code != 200:
            raise RuntimeError("Unable to send custom log data to Azure Monitor")
    except Exception as e:
        raise e
    

def get_request_signature(server_time_string, request_data,workspace_id,primary_key):
    http_method = "POST"
    content_type = "application/json"
    xms_date = f"x-ms-date:{server_time_string}"
    resource = "/api/logs"
    string_to_hash = "\n".join([http_method, str(len(request_data.encode("utf-8"))), content_type, xms_date, resource])
    hashed_string = get_hmac256(string_to_hash, primary_key)
    return f"SharedKey {workspace_id}:{hashed_string}"


def get_server_time():
    now = datetime.utcnow()
    return now.strftime("%a, %d %b %Y %H:%M:%S GMT")

def get_hmac256(input_string, key):
    sha256_hmac = hmac.new(base64.b64decode(key.encode("utf-8")), input_string.encode("utf-8"), hashlib.sha256)
    return base64.b64encode(sha256_hmac.digest()).decode("utf-8")


def get_x_ms_date():
    utc_now = datetime.now(pytz.timezone('UTC'))
    formatted_date = utc_now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return formatted_date

def get_auth_toke_azure_monitor(tenant_id, client_id, client_secret):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Payload for the POST request
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "resource": "https://api.loganalytics.io",
        "client_secret": client_secret
    }   

    # Sending the POST request
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        # Parse the JSON response
        response_data = json.loads(response.text)

        # Extract and print the access_token
        access_token = response_data.get("access_token")
        if access_token:
            return access_token
        else:
            print("Access Token not found in the response.")        
    else:
        return response.text
    
def get_query_result(workspace_id, access_token):
    url = f"https://api.loganalytics.azure.com/v1/workspaces/{workspace_id}/query?query=invocationlogs1_CL | top 1 by run_started_at_s desc&timestamp=P7D"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response_data = json.loads(response.text)
        status_code = response.status_code
        primary_result_table = response_data.get('tables', [])[0]
        if primary_result_table:    
            rows = primary_result_table.get('rows', [])[0]
            print(rows)
            if(len(rows) > 0):
                return rows[10]
            else:
                return "null"

        if status_code != 200:
            raise RuntimeError("Unable to send custom log data to Azure Monitor")
    except Exception as e:
        raise e

if __name__ == '__main__':
   dbtlog()