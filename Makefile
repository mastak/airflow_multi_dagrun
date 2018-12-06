.PHONY: init run test down

init:
	docker-compose up -d postgres
	docker-compose run --rm webserver airflow initdb

run: init
	docker-compose up webserver

test: init
	docker-compose run --rm webserver airflow test simple_trigger gen_target_dag_run 20000101
	docker-compose run --rm webserver airflow test simple_trigger_returning_dagrun gen_target_dag_run 20000101
	docker-compose run --rm webserver airflow test simple_trigger_with_context gen_target_dag_run 20000101

down:
	docker-compose down
