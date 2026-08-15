"""ML pipeline DAG — orchestrates the feature-store workflow.

feast_apply -> feast_materialize -> train -> evaluate -> register

Demonstrates: task dependencies, retries with backoff, scheduling, backfill via
date templating, idempotent tasks. Train/evaluate/register are stubbed now and
wired to the Ray + MLflow components later.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


# Task defaults: retries + backoff apply to every task in the DAG.
default_args = {
    "retries": 2,                          # a flaky task gets 2 more attempts
    "retry_delay": timedelta(minutes=1),   # wait between attempts (backoff)
}

with DAG(
    dag_id="ml_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",                     # run once a day
    catchup=False,                         # set True to backfill from start_date
    tags=["ml-platform"],
) as dag:

    feast_apply = BashOperator(
        task_id="feast_apply",
        bash_command="cd /opt/feature_store && feast apply",
    )

    feast_materialize = BashOperator(
        task_id="feast_materialize",
        bash_command="cd /opt/feature_store && feast materialize-incremental {{ ds }}",
    )

    # Stubs for the downstream steps — real Ray/MLflow wiring comes later.
    def _train(**ctx):
        print(f"training model for run date {ctx['ds']}")

    def _evaluate(**ctx):
        print("evaluating model (will reuse Lane B eval harness)")

    def _register(**ctx):
        print("registering model (will use MLflow)")

    train = PythonOperator(task_id="train", python_callable=_train)
    evaluate = PythonOperator(task_id="evaluate", python_callable=_evaluate)
    register = PythonOperator(task_id="register", python_callable=_register)

    # TODO: define the dependency chain with >> operators:
    #   feast_apply >> feast_materialize >> train >> evaluate >> register
    # (you'll need to create feast_apply and feast_materialize above first)
    feast_apply >> feast_materialize >> train >> evaluate >> register
