from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


def upload_to_s3(filename, key, bucket_name):
    hook = S3Hook('s3_conn')
    hook.load_file(filename=filename, key=key, bucket_name=bucket_name)


with DAG(
        dag_id='s3_dag',
        schedule_interval='@daily',
        start_date=datetime(2023, 1, 31),
        catchup=False
) as dag:
    upload_file_to_s3 = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3,
        op_kwargs={
            'filename': 'dags/AutoSleep Data/data.csv',
            'key': 'data.csv',
            'bucket_name': 'etl-airflow-autosleep'
        }

    )
