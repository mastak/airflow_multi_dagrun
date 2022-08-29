import logging

from airflow.models import DAG
from airflow.utils.dates import days_ago

from airflow_multi_dagrun.operators import TriggerMultiDagRunOperator

log = logging.getLogger(__name__)


def generate_dag_run(**context):
    """Callable can depend on the context"""
    log.info('!!!!!!!! =========== TRY NUMBER %s', context['ti'].try_number)
    for i in range(2):
        if i > 0 and context['ti'].try_number < 2:
            raise Exception('First try failed')

        yield {
            'run_id': f"custom_trigger_id___{context['ts']}_{i}",
            'timeout': i,
            'ds': context["ds"],
        }


args = {
    'start_date': days_ago(1),
    'owner': 'airflow',
}

with DAG(dag_id='trigger_with_retries', max_active_runs=1, default_args=args) as dag:
    TriggerMultiDagRunOperator(
        task_id='gen_target_dag_run',
        dag=dag,
        trigger_dag_id='common_target_custom_run_id',
        python_callable=generate_dag_run,
        retries=3,
        retry_delay=0,
    )
