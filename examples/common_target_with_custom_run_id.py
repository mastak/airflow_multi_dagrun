import logging
import time

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

logger = logging.getLogger(__name__)

args = {
    'start_date': days_ago(1),
    'owner': 'airflow',
}

dag = DAG(
    dag_id='common_target_custom_run_id',
    default_args=args,
    schedule_interval=None
)


def custom_run_id_handler(dag_run, **kwargs):
    if not dag_run.run_id.startswith('custom_trigger_id___'):
        raise ValueError('Incorrect run_id, it has to be run with custom run_id')

    timeout = dag_run.conf['timeout']
    logger.info(f"Task received: timeout={timeout}, run_id={dag_run.run_id}")
    time.sleep(timeout)


chunk_handler = PythonOperator(
    task_id='custom_run_id_handler',
    python_callable=custom_run_id_handler,
    dag=dag
)
