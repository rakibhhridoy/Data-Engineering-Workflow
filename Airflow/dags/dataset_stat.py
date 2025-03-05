from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd

# Define default arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime.now(),
    'retries': 1,
}

# Path to the CSV file
CSV_FILE_PATH = '/Users/rakibhhridoy/DE/Airflow/dags/data/data.csv'  # Update this path
OUTPUT_FILE_PATH = '/Users/rakibhhridoy/DE/Airflow/dags/data/dstat.csv'  # Update this path

def import_csv():
    df = pd.read_csv(CSV_FILE_PATH)
    print("CSV file imported successfully!")
    return df

def check_null_and_schema(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='import_csv')  # Get data from Task 1
    print("Checking for null values...")
    print(df.isnull().sum())  # Print count of null values per column
    print("\nSchema of the data:")
    print(df.dtypes)  # Print data types of columns

def generate_statistics(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='import_csv')  # Get data from Task 1
    print("Generating descriptive statistics...")
    stats = df.describe()  # Generate descriptive statistics
    stats.to_csv(OUTPUT_FILE_PATH)  # Save statistics to CSV
    print(f"Statistics saved to {OUTPUT_FILE_PATH}")

with DAG(
    'data_lookup',
    default_args=default_args,
    description='A DAG to process a CSV file',
    schedule_interval="@daily",  # Manual trigger only
) as dag:

    import_csv_task = PythonOperator(
        task_id='import_csv',
        python_callable=import_csv,
    )

    check_null_and_schema_task = PythonOperator(
        task_id='check_null_and_schema',
        python_callable=check_null_and_schema,
        provide_context=True,
    )

    generate_statistics_task = PythonOperator(
        task_id='generate_statistics',
        python_callable=generate_statistics,
        provide_context=True,
    )

# Set task dependencies
import_csv_task >> check_null_and_schema_task >> generate_statistics_task