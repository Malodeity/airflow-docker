from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner' : 'malo',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}


with DAG (
    
    dag_id='our_first_dagV2',
    default_args=default_args,
    description='This is the first dag',
    start_date=datetime(2021, 7, 29, 2),
    schedule_interval='@daily'
    
    ) as dag:



    
    task1 = BashOperator( #Extract
        task_id='first_task',
        bash_command="echo hello word we are here now"
    ) 
    
    
    task2 = BashOperator( #
        task_id='second_task',
        bash_command="echo hello world task 2"
    ) 
    
    task3 = BashOperator( #Load
        task_id='third_task',
        bash_command="echo hello world task 3"
    ) 
    
    #task1.set_downstream(task2)
    #task1.set_downstream(task3)
    
    task1 >>[task2, task3]