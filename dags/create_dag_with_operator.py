from airflow import DAG
from datetime import datetime, timedelta 
from airflow.operators.python import PythonOperator
import pandas as pd
import subprocess
from sqlalchemy import create_engine
from airflow.providers.postgres.operators.postgres import PostgresOperator



 
default_args = {
    'owner' : 'malo',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

dataframe = pd.DataFrame()

def read_exel():
    print('Begin Projedct')
    subprocess.run(['pip', 'install', 'openpyxl'])
    dataframe = pd.read_excel(
    '/opt/airflow/data/organizations-500000.xlsx')
    dataframe.rename(columns = {'Index':'index', 'Organization Id':'orgid','Name':'name','Name':'name','Website':'website','Country':'country','Description':'description', 'Founded':'founded', 'Industry':'industry', 'Number of employees':'noemployee' }, inplace = True)
    print(dataframe.columns)
    
    
    try:
        connectionstring = 'postgresql+psycopg2://airflow:airflow@postgres:5432'
        db = create_engine(connectionstring)
        conn =db.connect()
        print('connected')
        
        try:
            dataframe.to_sql('companies',connectionstring,if_exists='replace')
            print('inserted to database')
        
        except:
            print('not inserted to the database')
    except:
        print('Did not connect')
    
    
    
def numberofemployeesindustry():
    try:
        connectionstring = 'postgresql+psycopg2://airflow:airflow@postgres:5432'
        db = create_engine(connectionstring)
        conn =db.connect()
        print('connected')
        dataframe = pd.read_sql("select country, industry, sum(noemployee) totalemployees from companies group by country,industry;", conn)
        print(dataframe)
        try:
            dataframe.to_sql('industryemployees',connectionstring,if_exists='replace')
            print('inserted to database')
        
        except:
            print('not inserted to the database')
    except:
        print('Did not connect')
        
        
        
        
        
def foundedcompanies():
    try:
        connectionstring = 'postgresql+psycopg2://airflow:airflow@postgres:5432'
        db = create_engine(connectionstring)
        conn =db.connect()
        print('connected')
        dataframe = pd.read_sql("select founded, count(name) totalcompanies from companies group by founded;", conn)
        print(dataframe)
        try:
            dataframe.to_sql('foundedcompanies',connectionstring,if_exists='replace')
            print('inserted to database')
        
        except:
            print('not inserted to the database')
    except:
        print('Did not connect')
        
        
        
def companiespercountry():
    try:
        connectionstring = 'postgresql+psycopg2://airflow:airflow@postgres:5432'
        db = create_engine(connectionstring)
        conn =db.connect()
        print('connected')
        dataframe = pd.read_sql("select country, count(name) totalcompanies from companies group by country;", conn)
        print(dataframe)
        try:
            dataframe.to_sql('countrycompanies',connectionstring,if_exists='replace')
            print('inserted to database')
        
        except:
            print('not inserted to the database')
    except:
        print('Did not connect')
        
        
def cleantables():
    
    tablelist = ['companies','foundedcompanies','industryemployees','countrycompanies','countrymostemployees']

    subprocess.run(['pip', 'install', 'pycountry'])
    try:
        connectionstring = 'postgresql+psycopg2://airflow:airflow@postgres:5432'
        db = create_engine(connectionstring)
        conn =db.connect()
        print('connected')
        for tbl in tablelist:
        
            try:
                conn.execute("truncate table "+ tbl +";")
                #dataframe = pd.read_sql("truncate table companies;", conn)
                print('table is truncated :' + tbl)
            except Exception as e:
                print(e)
                print('table not truncated')
                
    except:
        print('Did not connect')
    #create table industryemployees(country varchar(255), industry varchar(255), totalemployees init);
    
    #select founded, count(name) from companies group by founded;
    #create table foundedcompanies(founded vachar(255), totalcompanies int);
    
    #select country, count(name) from companies group by country;
    #create table countrymostemployees(country varchar(255),industry varchar(255), totalemployees int);
    
def countrymostemployees():
    try:
        connectionstring = 'postgresql+psycopg2://airflow:airflow@postgres:5432'
        db = create_engine(connectionstring)
        conn =db.connect()
        print('connected')
        dataframe = pd.read_sql("select final.country,prefinal.industry, final.totalemployees from (select country, max(sumemployees) totalemployees from (select country, industry, sum(noemployee) sumemployees from companies group by country, industry) final group by country) final inner join (select country, industry, sum(noemployee) sumemployees from companies group by country, industry) prefinal on final.country = prefinal.country and final.totalemployees = prefinal.sumemployees;", conn)
        print(dataframe)
        try:
            dataframe.to_sql('countrymostemployees',connectionstring,if_exists='replace')
            print('inserted to database')
        
        except:
            print('not inserted to the database')
    except:
        print('Did not connect')


with DAG (
    
    dag_id='pc_data_dag',
    default_args=default_args,
    description='PC Engineering POC Dag',
    start_date=datetime(2023, 1, 15),
    schedule_interval='@daily'
    
    ) as dag:
    
      task1 = PythonOperator(
        task_id='read_excel_file',
        python_callable=read_exel,
    ) 
      task2 = PythonOperator(
        task_id='insert_numberofemployeesindustry',
        python_callable=numberofemployeesindustry
        
        #postgres_conn_id='posgres',
        #sql="""select sum(noemployee),country, industry from companies group by country,industry;"""
    ) 
      
      task3 = PythonOperator(
        task_id='insert_foundedcompanies',
        python_callable=foundedcompanies
    ) 
      
      task4 = PythonOperator(
        task_id='insert_companiespercountry',
        python_callable=companiespercountry
    ) 
      
      task5 = PythonOperator(
        task_id='clean_tables',
        python_callable=cleantables
    ) 
       
      task6 = PythonOperator(
        task_id='most_countryemployees',
        python_callable=countrymostemployees
    ) 
      

task5 >> task1 >> [task2,task3,task4,task6]