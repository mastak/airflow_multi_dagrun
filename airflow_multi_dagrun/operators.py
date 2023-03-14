import time
import typing as t

from airflow.api.common.experimental.trigger_dag import trigger_dag
from airflow.exceptions import AirflowException
from airflow.models import DagRun
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils import timezone
from airflow.utils.operator_helpers import determine_kwargs
from airflow.utils.session import provide_session
from airflow.utils.types import DagRunType

from airflow_multi_dagrun.utils import get_multi_dag_run_xcom_key


class TriggerMultiDagRunOperator(TriggerDagRunOperator):
    def __init__(self, op_args=None, op_kwargs=None, python_callable=None, *args, **kwargs):
        super(TriggerMultiDagRunOperator, self).__init__(*args, **kwargs)
        self.op_args = op_args or []
        self.op_kwargs = op_kwargs or {}
        self.python_callable = python_callable

    @staticmethod
    def get_multi_dag_run_xcom_key(execution_date) -> str:
        return f"created_dagrun_key_{execution_date}"

    def execute(self, context: Context):
        context.update(self.op_kwargs)
        self.op_kwargs = determine_kwargs(self.python_callable, self.op_args, context)

        created_dr_ids = []
        created_drs = []
        for conf in self.python_callable(*self.op_args, **self.op_kwargs):
            if not conf:
                break

            execution_date = timezone.utcnow()

            run_id = conf.get("run_id")
            if not run_id:
                run_id = DagRun.generate_run_id(DagRunType.MANUAL, execution_date)

            dag_run = DagRun.find(dag_id=self.trigger_dag_id, run_id=run_id)
            if not dag_run:
                dag_run = trigger_dag(
                    dag_id=self.trigger_dag_id,
                    run_id=run_id,
                    conf=conf,
                    execution_date=execution_date,
                    replace_microseconds=False,
                )
                self.log.info("Created DagRun %s, %s - %s", dag_run, self.trigger_dag_id, run_id)
            else:
                dag_run = dag_run[0]
                self.log.warning(
                    "Fetched existed DagRun %s, %s - %s", dag_run, self.trigger_dag_id, run_id
                )

            created_dr_ids.append(dag_run.id)
            created_drs.append(dag_run)

        if created_dr_ids:
            xcom_key = self.get_multi_dag_run_xcom_key(context["execution_date"])
            context["ti"].xcom_push(xcom_key, created_dr_ids)
            self.log.info("Pushed %s DagRun's ids with key %s", len(created_dr_ids), xcom_key)

            if self.wait_for_completion:
                failed_dags = {}

                # Hold on while we still have running DAGs...
                while created_drs:
                    self.log.info(
                        "Waiting for DAGs triggered by %s to complete...", self.trigger_dag_id
                    )
                    time.sleep(self.poke_interval)

                    # Check every running DAG.
                    for dag_run in created_drs:
                        dag_run.refresh_from_db()
                        state = dag_run.state

                        if state in self.failed_states:
                            # If the DAG has failed, mark it as such and remove it from list.
                            failed_dags[self.trigger_dag_id] = state
                            created_drs.remove(dag_run)
                        elif state in self.allowed_states:
                            # If the DAG succeeded, log in the successful event and remove it too.
                            self.log.info(
                                "%s finished with allowed state %s", self.trigger_dag_id, state
                            )
                            created_drs.remove(dag_run)

                if failed_dags:
                    # Raise an Airflow exception if any of the DAGs failed.
                    failures = "; ".join(f"{key}: {value}" for key, value in failed_dags.items())
                    raise AirflowException(f"Failed DAGs: {failures}")
        else:
            self.log.info("No DagRuns created")

