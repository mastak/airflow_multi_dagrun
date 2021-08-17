from airflow.models import DAG
from airflow.utils import timezone
from airflow.utils.dates import days_ago

from airflow_multi_dagrun.operators import TriggerMultiDagRunOperator


def generate_dag_run(**context):
    """Callable can depend on the context"""
    for i in range(2):
        yield {
            'run_id': f"custom_trigger_id___{timezone.utcnow().isoformat()}",
            'timeout': i,
            'ds': context["ds"],
        }


args = {
    'start_date': days_ago(1),
    'owner': 'airflow',
}

dag = DAG(
    dag_id='simple_trigger_with_custom_run_id',
    max_active_runs=1,
    schedule_interval='@hourly',
    default_args=args,
)

gen_target_dag_run = TriggerMultiDagRunOperator(
    task_id='gen_target_dag_run',
    dag=dag,
    trigger_dag_id='common_target_custom_run_id',
    python_callable=generate_dag_run,
)
