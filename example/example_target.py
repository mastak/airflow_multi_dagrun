from datetime import datetime

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

args = {
    'start_date': datetime.utcnow(),
    'owner': 'airflow',
}


dag = DAG(
    dag_id='example_target_dag',
    default_args=args,
    schedule_interval=None
)


def run_this_func(dag_run, **kwargs):
    print("Chunk received: {}".format(dag_run.conf['chunk']))


chunk_handler = PythonOperator(
    task_id='chunk_handler',
    provide_context=True,
    python_callable=run_this_func,
    dag=dag
)
