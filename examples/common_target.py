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
    dag_id='common_target',
    default_args=args,
    schedule_interval=None
)


def run_this_func(dag_run, **kwargs):
    timeout = dag_run.conf['timeout']
    logger.info("Chunk received: {}".format(timeout))
    time.sleep(timeout)


chunk_handler = PythonOperator(
    task_id='chunk_handler',
    python_callable=run_this_func,
    dag=dag
)
