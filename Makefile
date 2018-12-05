.PHONY: run test resetdb

run:
	docker-compose up -d

test:
	docker-compose up -d
	docker-compose run --rm webserver airflow initdb
	docker-compose run --rm webserver airflow test simple_trigger gen_target_dag_run 20000101

resetdb:
	docker-compose down
