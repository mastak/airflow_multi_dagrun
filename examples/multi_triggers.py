from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.state import State

from airflow_multi_dagrun.operators import TriggerMultiDagRunOperator
from airflow_multi_dagrun.sensors import MultiDagRunSensor

args = {
    'owner': 'airflow',
}


def generate_dag_run(raise_error=None):
    return [{'timeout': i, 'raise_error': raise_error} for i in range(3)]


def after_dags_handler():
    print("All target DAGs are finished")


def create_test_pipeline(suffix, gen_target_dag_run_, dag_):
    op_kwargs = None
    if suffix == '1':
        dagrun_finished_states = [State.SUCCESS]
    elif suffix == '2':
        dagrun_finished_states = [State.FAILED]
        op_kwargs = {'raise_error': True}
    else:
        dagrun_finished_states = None

    gen_target_dag_run_a = TriggerMultiDagRunOperator(
        task_id=f'gen_target_dag_run_{suffix}_a',
        dag=dag_,
        trigger_dag_id='common_target',
        op_kwargs=op_kwargs,
        python_callable=generate_dag_run,
    )
    gen_target_dag_run_b = TriggerMultiDagRunOperator(
        task_id=f'gen_target_dag_run_{suffix}_b',
        dag=dag_,
        trigger_dag_id='common_target',
        op_kwargs=op_kwargs,
        python_callable=generate_dag_run,
    )
    wait_target_dag = MultiDagRunSensor(
        dagrun_finished_states=dagrun_finished_states,
        task_id=f'wait_target_dag_{suffix}',
        dag=dag_
    )

    after_dags_handler_op = PythonOperator(
        task_id=f'after_dags_handler_{suffix}',
        python_callable=after_dags_handler,
        dag=dag
    )
    gen_target_dag_run_ >> gen_target_dag_run_a
    gen_target_dag_run_ >> gen_target_dag_run_b
    gen_target_dag_run_a >> wait_target_dag
    gen_target_dag_run_b >> wait_target_dag
    wait_target_dag >> after_dags_handler_op


with DAG(dag_id='multi_triggers', default_args=args, start_date=days_ago(2)) as dag:
    gen_target_dag_run = DummyOperator(task_id='gen_target_dag_run', dag=dag)
    create_test_pipeline('1', gen_target_dag_run, dag)
    create_test_pipeline('2', gen_target_dag_run, dag)
    create_test_pipeline('3', gen_target_dag_run, dag)
