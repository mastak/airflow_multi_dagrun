import typing as t

from airflow.api.common.experimental.trigger_dag import trigger_dag
from airflow.models import DagRun
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils import timezone
from airflow.utils.operator_helpers import determine_kwargs
from airflow.utils.session import provide_session
from airflow.utils.types import DagRunType


class TriggerMultiDagRunOperator(TriggerDagRunOperator):
    CREATED_DAGRUN_KEY = 'created_dagrun_key'

    def __init__(
        self, op_args=None, op_kwargs=None, python_callable=None, dagrun_key=None, *args, **kwargs
    ):
        super(TriggerMultiDagRunOperator, self).__init__(*args, **kwargs)
        self.op_args = op_args or []
        self.op_kwargs = op_kwargs or {}
        self.python_callable = python_callable
        if dagrun_key is None:
            self.dagrun_key = self.CREATED_DAGRUN_KEY
        else:
            self.dagrun_key = dagrun_key

    @provide_session
    def execute(self, context: t.Dict, session=None):
        context.update(self.op_kwargs)
        self.op_kwargs = determine_kwargs(self.python_callable, self.op_args, context)

        created_dr_ids = []
        for conf in self.python_callable(*self.op_args, **self.op_kwargs):
            if not conf:
                break

            execution_date = timezone.utcnow()

            run_id = conf.get('run_id')
            if not run_id:
                run_id = DagRun.generate_run_id(DagRunType.MANUAL, execution_date)

            dag_run = trigger_dag(
                dag_id=self.trigger_dag_id,
                run_id=run_id,
                conf=conf,
                execution_date=execution_date,
                replace_microseconds=False,
            )

            created_dr_ids.append(dag_run.id)
            self.log.info("Created DagRun %s, %s - %s", dag_run, self.trigger_dag_id, run_id)

        self.log.debug("DagRun xcom key: %s", self.dagrun_key)

        if created_dr_ids:
            context['ti'].xcom_push(self.dagrun_key, created_dr_ids)
        else:
            self.log.info("No DagRuns created")
