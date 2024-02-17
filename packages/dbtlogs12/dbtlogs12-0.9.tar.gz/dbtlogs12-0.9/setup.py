from setuptools import setup, find_packages

setup(
    name='dbtlogs12',
    version='0.9',
    packages=find_packages(),
    install_requires=[
        'click',
        'databricks-sql-connector',
        'requests',
        'pytz',
        'typing',
        'datetime',
        'apache-airflow',
        'snowflake-sqlalchemy',
        'snowflake-connector-python'
    ],
    entry_points={
        'console_scripts': [
            'dbtlog = dbtlogs.main:dbtlog',
        ],
    },
)
