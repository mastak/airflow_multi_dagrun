from airflow.models import DAG
from airflow.operators.dagrun_operator import DagRunOrder
from airflow.operators.multi_dagrun import (TriggerMultiDagRunOperator,
                                            ExternalDagsSensor)
from airflow.utils.dates import days_ago


def generate_dag_run():
    return [DagRunOrder(payload={'timeout': i}) for i in range(10)]


args = {
    'start_date': days_ago(1),
    'owner': 'airflow',
}


dag = DAG(
    dag_id='trigger_with_external_sensor',
    max_active_runs=1,
    schedule_interval='@hourly',
    default_args=args,
)


# Wait until there is no running instance of target DAG
wait_target_dag = ExternalDagsSensor(
    task_id='wait_target_dag',
    instances_limit=3,
    external_dag_id='common_target',
    dag=dag
)


gen_target_dag_run = TriggerMultiDagRunOperator(
    task_id='gen_target_dag_run',
    dag=dag,
    trigger_dag_id='common_target',
    python_callable=generate_dag_run,
)
gen_target_dag_run.set_upstream(wait_target_dag)
