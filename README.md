# Multi dag run

This plugin contains operators for triggering a DAG run multiple times
and you can dynamically specify how many DAG run instances create.

It can be useful when you have to handle a big data and you want to split it
into chunks and run multiple instances of the same task in parallel.

When you see a lot launched target DAGs you can set up more workers.
So this makes it pretty easy to scale.

## Example

Code for scheduling dags

```python
import datetime as dt
from airflow import DAG
from airflow.operators import TriggerMultiDagRunOperator
from airflow.operators.dagrun_operator import DagRunOrder


def generate_dag_run(ds, **kwargs):
    print(ds)  # access context properties, e.g. ds
    for i in range(100):
        yield DagRunOrder(payload={'index': i})


default_args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2015, 6, 1),
}


dag = DAG('reindex_scheduler', schedule_interval=None, default_args=default_args)


ran_dags = TriggerMultiDagRunOperator(
    task_id='gen_target_dag_run',
    dag=dag,
    trigger_dag_id='example_target_dag',
    python_callable=generate_dag_run,
    pass_context=True
)
```

This code will schedule dag with id `example_target_dag` 100 times and pass payload to it.


Example of triggered dag:

 ```python
dag = DAG(
    dag_id='example_target_dag',
    schedule_interval=None,
    default_args={'start_date': datetime.utcnow(), 'owner': 'airflow'},
)


def run_this_func(dag_run, **kwargs):
    print("Chunk received: {}".format(dag_run.conf['index']))


chunk_handler = PythonOperator(
    task_id='chunk_handler',
    provide_context=True,
    python_callable=run_this_func,
    dag=dag
)
```

## Run example
There is docker-compose config, so it requires docker to be installed: `docker`, `docker-compose`
1. `docker-compose up/stop` - start/stop docker containers
2. `docker-compose down` - destroy docker containers

## Contributions
If you have found a bug or have some idea for improvement feel free to create an issue
or pull request.

## License
Apache 2.0
