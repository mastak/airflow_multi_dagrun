from itertools import chain

from airflow.models import DagRun
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.session import provide_session
from airflow.utils.state import State

from airflow_multi_dagrun.utils import get_multi_dag_run_xcom_key


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

    def __init__(self, external_dag_id, instances_limit=0, *args, **kwargs):
        super(ExternalDagsSensor, self).__init__(*args, **kwargs)
        self._waited_states = [State.RUNNING]
        self.external_dag_id = external_dag_id
        self._instances_limit = instances_limit

    @provide_session
    def poke(self, context, session=None):
        self.log.info('Poking for {self.external_dag_id}'.format(**locals()))
        count = session.query(DagRun).filter(
            DagRun.dag_id == self.external_dag_id,
            DagRun.state.in_(self._waited_states),
        ).count()
        return count <= self._instances_limit


class MultiDagRunSensor(BaseSensorOperator):
    """
    Used with TriggerMultiDagRunOperator.
    Waits until all DAGs created by TriggerMultiDagRunOperator(in current execution)
    will be finished.
    """

    def __init__(self, dagrun_finished_states=None, *args, **kwargs):
        super(MultiDagRunSensor, self).__init__(*args, **kwargs)
        if dagrun_finished_states is None:
            dagrun_finished_states = [State.SUCCESS, State.FAILED]
        self._dagrun_finished_states = dagrun_finished_states

    @provide_session
    def poke(self, context, session=None):
        xcom_key = get_multi_dag_run_xcom_key(context['execution_date'])
        dagrun_ids = context['ti'].xcom_pull(task_ids=context["task"].upstream_task_ids,
                                             key=xcom_key)
        dagrun_ids = list(chain.from_iterable(dagrun_ids))

        self.log.info("Loaded dagrun ids: %s, for task: %s", dagrun_ids, xcom_key)
        if not dagrun_ids:
            return True

        finished_count = session.query(DagRun).filter(
            DagRun.id.in_(dagrun_ids),
            DagRun.state.in_(self._dagrun_finished_states),
        ).count()
        total_count = len(dagrun_ids)
        self.log.info('Poking for dagruns, finished %s / %s', finished_count, total_count)
        return finished_count >= total_count
