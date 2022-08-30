from airflow.models import DAG
from airflow.utils.dates import days_ago

from airflow_multi_dagrun.operators import TriggerMultiDagRunOperator


def generate_dag_run(**context):
    """Callable can depend on the context"""
    for i in range(10):
        yield {
            'timeout': i,
            'ds': context["ds"],
        }


args = {
    'start_date': days_ago(1),
    'owner': 'airflow',
}

dag = DAG(
    dag_id='trigger_with_context',
    max_active_runs=1,
    schedule_interval='@hourly',
    default_args=args,
)

gen_target_dag_run = TriggerMultiDagRunOperator(
    task_id='gen_target_dag_run',
    dag=dag,
    trigger_dag_id='common_target',
    python_callable=generate_dag_run,
)
