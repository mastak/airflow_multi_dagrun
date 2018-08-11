from __future__ import division, absolute_import, print_function

from airflow.plugins_manager import AirflowPlugin

from . import operators


class MultiDagRunPlugin(AirflowPlugin):
    name = "multi_dagrun"
    operators = [
        operators.TriggerMultiDagRunOperator,
        operators.ExternalDagsSensor,
        operators.MultiDagRunSensor,
    ]
