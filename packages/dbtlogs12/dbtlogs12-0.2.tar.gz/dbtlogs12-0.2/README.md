## Python Package - to send dbt artifact to azure monitor
We've developed a Python package to streamline the process of sending dbt audit logs (dbt artifacts) to Azure Monitor. This package enables you to store these logs in a custom table named dbtlogs_CL within your Log Analytics workspace in Azure. Additionally, our solution intelligently captures audit logs based on the execution start date of the currently running Airflow DAG. It specifically focuses on capturing logs from four key tables: model_execution, seed_execution, test_execution, and seed_execution and one invocations table it used to track env variable, other variables.

Detailed Wiki to use - https://corpinfollc.atlassian.net/wiki/spaces/APS/pages/119139037872172/How-to+dbt+Audit+Logs+to+Azure+Monitor+and+alerts
