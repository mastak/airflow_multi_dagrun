from airflow import settings
from airflow.api.common.experimental.trigger_dag import trigger_dag
from airflow.models import DagRun
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.utils import timezone
from airflow.utils.decorators import apply_defaults
from airflow.utils.types import DagRunType


class TriggerMultiDagRunOperator(TriggerDagRunOperator):
    CREATED_DAGRUN_KEY = 'created_dagrun_key'

    @apply_defaults
    def __init__(self, op_args=None, op_kwargs=None, provide_context=False, python_callable=None,
                 *args, **kwargs):
        super(TriggerMultiDagRunOperator, self).__init__(*args, **kwargs)
        self.op_args = op_args or []
        self.op_kwargs = op_kwargs or {}
        self.provide_context = provide_context
        self.python_callable = python_callable

    def execute(self, context):
        if self.provide_context:
            context.update(self.op_kwargs)
            self.op_kwargs = context

        session = settings.Session()
        created_dr_ids = []
        for conf in self.python_callable(*self.op_args, **self.op_kwargs):
            if not conf:
                break

            execution_date = timezone.utcnow()
            run_id = DagRun.generate_run_id(DagRunType.MANUAL, execution_date)

            dr = trigger_dag(
                dag_id=self.trigger_dag_id,
                run_id=run_id,
                conf=conf,
                execution_date=execution_date,
                replace_microseconds=False,
            )

            created_dr_ids.append(dr.id)
            self.log.info("Created DagRun %s, %s - %s", dr, self.trigger_dag_id, run_id)

        if created_dr_ids:
            session.commit()
            context['ti'].xcom_push(self.CREATED_DAGRUN_KEY, created_dr_ids)
        else:
            self.log.info("No DagRun created")
        session.close()
