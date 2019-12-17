from airflow.models import DAG
from airflow.operators.dagrun_operator import DagRunOrder
from airflow.operators.multi_dagrun import (TriggerMultiDagRunOperator,
                                            MultiDagRunSensor)
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def generate_dag_run():
    return [DagRunOrder(payload={'timeout': i}) for i in range(10)]


def after_dags_handler():
    print("All target DAGs are finished")


args = {
    'start_date': days_ago(1),
    'owner': 'airflow',
}


dag = DAG(
    dag_id='trigger_with_multi_dagrun_sensor',
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


# Wait until there is no running instance of target DAG
wait_target_dag = MultiDagRunSensor(
    task_id='wait_target_dag',
    dag=dag
)
wait_target_dag.set_upstream(gen_target_dag_run)


after_dags_handler_op = PythonOperator(
    task_id='after_dags_handler',
    python_callable=after_dags_handler,
    dag=dag
)
after_dags_handler_op.set_upstream(wait_target_dag)
