import random

from airflow.models import DAG
from airflow.operators import TriggerMultiDagRunOperator, ExternalDagSensor
from airflow.operators.dagrun_operator import DagRunOrder
from airflow.utils.dates import days_ago

CHUNK_SIZE = 3000


def fetch_data():
    count = random.randint(25000, 50000)
    return range(count)


def generate_dag_run(context):
    chunk = []
    for i in fetch_data():
        chunk.append(i)
        if len(chunk) == CHUNK_SIZE:
            yield DagRunOrder(payload=dict(chunk=chunk))
            chunk = []
    if chunk:
        yield DagRunOrder(payload=dict(chunk=chunk))


args = {
    'start_date': days_ago(1),
    'owner': 'airflow',
}


dag = DAG(
    dag_id='example_trigger_dag',
    max_active_runs=1,
    schedule_interval='@hourly',
    default_args=args,
)


wait_target_dag = ExternalDagSensor(
    task_id='wait_target_dag',
    external_dag_id='example_target_dag',
    dag=dag
)


gen_target_dag_run = TriggerMultiDagRunOperator(
    task_id='gen_target_dag_run',
    dag=dag,
    trigger_dag_id='example_target_dag',
    python_callable=generate_dag_run,
)

gen_target_dag_run.set_upstream(wait_target_dag)
