from airflow import settings
from airflow.models import DagRun
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.state import State


class ExternalDagsSensor(BaseSensorOperator):
    """
    Wait until the number of running instances is equal to or less than limit

    :param external_dag_id: The dag_id that contains the task you want to
                            wait for
    :type external_dag_id: string
    :param instances_limit: Max number of running instances of DAG
                            with dag_id `external_dag_id`
    :type instances_limit: int
    """
    ui_color = '#19647e'

    @apply_defaults
    def __init__(self, external_dag_id, instances_limit=0, *args, **kwargs):
        super(ExternalDagsSensor, self).__init__(*args, **kwargs)
        self._waited_states = [State.RUNNING]
        self.external_dag_id = external_dag_id
        self._instances_limit = instances_limit

    def poke(self, context):
        self.log.info('Poking for {self.external_dag_id}'.format(**locals()))
        session = settings.Session()
        count = session.query(DagRun).filter(
            DagRun.dag_id == self.external_dag_id,
            DagRun.state.in_(self._waited_states),
        ).count()
        session.rollback()
        session.close()
        return count <= self._instances_limit


class MultiDagRunSensor(BaseSensorOperator):
    """
    Used with TriggerMultiDagRunOperator.
    Waits until all DAGs created by TriggerMultiDagRunOperator(in current execution)
    will be finished.
    """
    CREATED_DAGRUN_KEY = 'created_dagrun_key'

    @apply_defaults
    def __init__(self, dagrun_finished_states=None, *args, **kwargs):
        super(MultiDagRunSensor, self).__init__(*args, **kwargs)
        if dagrun_finished_states is None:
            dagrun_finished_states = [State.SUCCESS, State.FAILED]
        self._dagrun_finished_states = dagrun_finished_states

    def poke(self, context):
        xcom_key = self.CREATED_DAGRUN_KEY
        dagrun_ids = context['ti'].xcom_pull(task_ids=None, key=xcom_key)
        if not dagrun_ids:
            return True

        session = settings.Session()
        finished_count = session.query(DagRun).filter(
            DagRun.id.in_(dagrun_ids),
            DagRun.state.in_(self._dagrun_finished_states),
        ).count()
        session.rollback()
        session.close()
        total_count = len(dagrun_ids)
        self.log.info('Poking for dagruns, finished {} / {}'.format(total_count,
                                                                    finished_count))
        return finished_count >= total_count
