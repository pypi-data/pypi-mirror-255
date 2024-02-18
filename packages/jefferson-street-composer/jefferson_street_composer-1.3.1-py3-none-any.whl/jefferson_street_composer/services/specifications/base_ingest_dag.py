from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Any

from airflow.operators.bash import BashOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow import DAG

@dataclass
class DagDefaultArgs():
    owner: str =  'Jefferson Street Technologies'
    description: str =  "Ingest DAG for Jefferson Street Technologies"
    start_date: datetime = datetime(year=2023, month=1, day=1)
    retries: int =  5
    retries_delay: timedelta = timedelta(minutes=2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "owner": self.owner,
            "description": self.description,
            "start_date": self.start_date,
            "retries": self.retries,
            "retries_delay": self.retries_delay,
        }

class JeffersonStreetBaseIngestDag():
    def __init__(
        self,
        task_id: str = "",
        name: str = "",
        image_name: str = "",
        env_vars: Dict[str, str] = {},
        namespace: str = "airflow",
        schedule_interval: str = "0 0 * * 0"
    ):
        self.task_id = task_id
        self.name = name
        self.image_name = image_name
        self.env_vars = env_vars
        self.namespace = namespace
        self.schedule_interval = schedule_interval

        self.run()

    @property
    def image(self) -> str:
        return f"gcr.io/jefferson-street-cloud/ingests/{self.image_name}"

    def run(self):
        dag_default_args = DagDefaultArgs()

        with DAG(self.name, default_args=dag_default_args.to_dict(), schedule_interval=self.schedule_interval, catchup=False) as dag:
            t1 = BashOperator(task_id='print_start', bash_command='echo "start"')

            t2 = KubernetesPodOperator(
                task_id=self.task_id,
                name=self.name,
                image=self.image,
                namespace=self.namespace,
                env_vars=self.env_vars,
            )

            t3 = BashOperator(task_id='print_finish', bash_command='echo "finish"')

            t1 >> t2 >> t3