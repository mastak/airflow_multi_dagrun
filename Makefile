.PHONY: webserver worker scheduler initdb
.EXPORT_ALL_VARIABLES:

AIRFLOW_HOME=$(CURDIR)/data/airflow
AIRFLOW__CORE__DAGS_FOLDER=$(CURDIR)/examples
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@127.0.0.1:5432/airflow
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__CORE__PLUGINS_FOLDER=$(CURDIR)/multi_dagrun
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__FERNET_KEY=hZkztR7zQ6j3l19124n9LybVvwFMO9MsMyN0vQwhc_0=
AIRFLOW__CELERY__BROKER_URL=amqp://127.0.0.1:5672//
AIRFLOW__CELERY__CELERY_RESULT_BACKEND=db+postgresql://airflow:airflow@127.0.0.1:5432/airflow
AIRFLOW__SCHEDULER__CATCHUP_BY_DEFAULT=False
AIRFLOW__WEBSERVER__WORKERS=1

# https://blog.phusion.nl/2017/10/13/why-ruby-app-servers-break-on-macos-high-sierra-and-what-can-be-done-about-it/
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

run_containers:
	docker-compose up -d

webserver: run_containers
	airflow webserver

worker: run_containers
	airflow worker

scheduler: run_containers
	airflow scheduler

initdb: run_containers
	docker-compose run --rm db sh -c 'createdb -h db $$POSTGRES_DB'
	airflow initdb

resetdb: run_containers
	docker-compose run --rm db sh -c \
		'dropdb -h db --if-exists $$POSTGRES_DB && \
		 createdb -h db $$POSTGRES_DB'
	airflow initdb
