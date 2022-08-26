import pendulum


def get_multi_dag_run_xcom_key(execution_date: pendulum.DateTime) -> str:
    return f'created_dagrun_key_{execution_date}'
