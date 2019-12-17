from setuptools import setup


setup(
    name='airflow_multi_dagrun',
    version='1.0',
    description='MultiDagRunPlugin for airflow',
    python_requires='>=3.6.0',
    author='Ihor Liubymov',
    author_email='infunt@gmail.com',
    url='https://github.com/mastak/airflow_multi_dagrun',
    entry_points={
        'airflow.plugins': [
            'airflow_multi_dagrun = airflow_multi_dagrun:MultiDagRunPlugin'
        ]
    }
)
