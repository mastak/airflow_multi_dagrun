from airflow import settings
from airflow.models import DagRun
from airflow.utils.state import State
from airflow.utils.decorators import apply_defaults
from airflow.operators.sensors import BaseSensorOperator


class ExternalDagSensor(BaseSensorOperator):
    """
    Wait until there are no active DAGs

    :param external_dag_id: The dag_id that contains the task you want to
        wait for
    :type external_dag_id: string
    """
    ui_color = '#19647e'

    @apply_defaults
    def __init__(self, external_dag_id, *args, **kwargs):
        super(ExternalDagSensor, self).__init__(*args, **kwargs)
        self._waited_states = [State.RUNNING]
        self.external_dag_id = external_dag_id

    def poke(self, context):
        self.log.info('Poking for {self.external_dag_id}'.format(**locals()))
        session = settings.Session()
        count = session.query(DagRun).filter(
            DagRun.dag_id == self.external_dag_id,
            DagRun.state.in_(self._waited_states),
        ).count()
        session.commit()
        session.close()
        return count == 0
