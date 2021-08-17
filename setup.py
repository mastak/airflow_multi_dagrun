from setuptools import setup

from airflow_multi_dagrun import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='airflow_multi_dagrun',
    version=version,
    description='MultiDagRunPlugin for airflow',
    python_requires='>=3.6.0',
    author='Ihor Liubymov',
    author_email='infunt@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/mastak/airflow_multi_dagrun',
    packages=['airflow_multi_dagrun'],
    entry_points={
        'airflow.plugins': [
            'airflow_multi_dagrun = airflow_multi_dagrun:MultiDagRunPlugin'
        ]
    }
)
