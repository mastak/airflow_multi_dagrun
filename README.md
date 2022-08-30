[![Build Status](https://travis-ci.com/mastak/airflow_multi_dagrun.svg?branch=master)](https://travis-ci.com/mastak/airflow_multi_dagrun) [![Support Ukraine Badge](https://bit.ly/support-ukraine-now)](https://github.com/support-ukraine/support-ukraine)


## ======== Help Ukraine
```
Russo-Ukrainian War which started in Feb 2014 and escalated since 8 years into 
a full-scale war against Ukraine on 24th of February, 
became a top cause in the international main stream nowadays.
```
[Save Life](https://savelife.in.ua/donate/) – NGO that crowdfunds non-lethal military equipment, such as thermal vision scopes & supplies it to the front lines. It also provides training for Ukrainian soldiers, as well as researching troops’ needs and social reintegration of veterans.

[Hospitallers](https://www.facebook.com/hospitallers/) – a medical battalion that unites volunteer paramedics and doctors to save the lives of soldiers on the frontline. They crowdfund their vehicle repairs, fuel, and medical equipment.
## ========


# Multi dag run

This plugin contains operators for triggering a DAG run multiple times
and you can dynamically specify how many DAG run instances create.

It can be useful when you have to handle a big data and you want to split it
into chunks and run multiple instances of the same task in parallel.

When you see a lot launched target DAGs you can set up more workers.
So this makes it pretty easy to scale.

## Install

```bash
pip install airflow_multi_dagrun
```

## Example

Code for scheduling dags

```python
import datetime as dt
from airflow import DAG

from airflow_multi_dagrun.operators import TriggerMultiDagRunOperator


def generate_dag_run():
    for i in range(100):
        yield {'index': i}


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
1. `make init` - create db
2. `make add-admin` - create `admin` user (is asks a password)
3. `make web` - start docker containers, run airflow webserver
4. `make scheduler` - start docker containers, run airflow scheduler

`make down` will stop and remove docker containers 

## Contributions
If you have found a bug or have some idea for improvement feel free to create an issue
or pull request.

## License
Apache 2.0
