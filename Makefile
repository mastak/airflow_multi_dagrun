.PHONY: init run test down

init:
	docker-compose up -d postgres
	docker-compose run --rm webserver airflow db init

web: init
	docker-compose up webserver

scheduler:
	docker-compose up scheduler

test: init
	docker-compose run --rm webserver airflow tasks test tutorial
	docker-compose run --rm webserver airflow tasks test simple_trigger gen_target_dag_run 20000101
	docker-compose run --rm webserver airflow tasks test simple_trigger_returning_dagrun gen_target_dag_run 20000101
	docker-compose run --rm webserver airflow tasks test simple_trigger_with_context gen_target_dag_run 20000101
	docker-compose run --rm webserver airflow tasks test trigger_with_multi_dagrun_sensor gen_target_dag_run 20000101

down:
	docker-compose down

clean_wheels:
	rm -rf ./dist/*

build_wheels: clean_wheels
	python3 setup.py bdist_wheel

add-admin: init
	docker-compose run --rm webserver airflow users create \
          --username admin \
          --firstname FIRST_NAME \
          --lastname LAST_NAME \
          --role Admin \
          --email admin@example.org

release: build_wheels
	pip install twine
	python setup.py sdist
	twine upload dist/*
