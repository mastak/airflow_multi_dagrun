from .operators import TriggerMultiDagRunOperator
from .sensors import MultiDagRunSensor

version = '2.2.0'


class MultiDagRunPlugin:
    name = 'MultiDagRunPlugin'


class MultiDagRunOperatorSensorPairGenerator():
    """
    Convience class to generate Multi DAG run operator/sensor pair that
    utilize the same xcom key.
    """
    def __init__(self, dagrun_key):
        self._dagrun_key = 'created_dagrun_key_{}'.format(dagrun_key)

    def setOperatorInitParams(self, **kwargs):
        """
        Set TriggerMultiDagRunOperator initialization parameters.
        """
        if "dagrun_key" in kwargs:
            raise ValueError(
                "Setting dagrun_key for operator when using {} is not allowed.".format(
                    self.__class__
                )
            )
        else:
            kwargs["dagrun_key"] = self._dagrun_key
        self.operator_params = kwargs

    def setSensorInitParams(self, **kwargs):
        """
        Set MultiDagRunSensor initialization parameters.
        """
        if "dagrun_key" in kwargs:
            raise ValueError(
                "Setting dagrun_key for sensor when using {} is not allowed.".format(
                    self.__class__
                )
            )
        else:
            kwargs["dagrun_key"] = self._dagrun_key
        self.sensor_params = kwargs

    def __call__(self):
        """
        Get operator/sensor pair.
        """
        return (
            TriggerMultiDagRunOperator(**self.operator_params),
            MultiDagRunSensor(**self.sensor_params),
        )
