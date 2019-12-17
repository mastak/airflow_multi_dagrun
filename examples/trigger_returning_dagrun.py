from airflow.models import DAG
from airflow.operators.dagrun_operator import DagRunOrder
from airflow.operators.multi_dagrun import TriggerMultiDagRunOperator
from airflow.utils.dates import days_ago


def generate_dag_run():
    """Callable can return explicit DagRuns"""
    for i in range(10):
        yield DagRunOrder(payload={'timeout': i})


args = {
    'start_date': days_ago(1),
    'owner': 'airflow',
}


dag = DAG(
    dag_id='simple_trigger_returning_dagrun',
    max_active_runs=1,
    schedule_interval='@hourly',
    default_args=args,
)


gen_target_dag_run = TriggerMultiDagRunOperator(
    task_id='gen_target_dag_run',
    dag=dag,
    trigger_dag_id='common_target',
    python_callable=generate_dag_run
)
