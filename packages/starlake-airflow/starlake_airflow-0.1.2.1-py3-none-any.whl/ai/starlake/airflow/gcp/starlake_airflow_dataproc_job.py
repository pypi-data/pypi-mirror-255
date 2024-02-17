import uuid

from typing import Union

from ai.starlake.common import TODAY

from ai.starlake.gcp import StarlakeDataprocClusterConfig, StarlakeDataprocMasterConfig, StarlakeDataprocWorkerConfig

from ai.starlake.job import StarlakePreLoadStrategy, StarlakeSparkConfig

from ai.starlake.airflow import StarlakeAirflowJob, StarlakeAirflowOptions

from airflow.models.baseoperator import BaseOperator

from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocDeleteClusterOperator,
)

from airflow.utils.trigger_rule import TriggerRule

class StarlakeAirflowDataprocMasterConfig(StarlakeDataprocMasterConfig, StarlakeAirflowOptions):
    def __init__(self, machine_type: str, disk_type: str, disk_size: int, options: dict, **kwargs):
        super().__init__(
            machine_type=machine_type,
            disk_type=disk_type,
            disk_size=disk_size,
            options=options,
            **kwargs
        )

class StarlakeAirflowDataprocWorkerConfig(StarlakeDataprocWorkerConfig, StarlakeAirflowOptions):
    def __init__(self, num_instances: int, machine_type: str, disk_type: str, disk_size: int, options: dict, **kwargs):
        super().__init__(
            num_instances=num_instances,
            machine_type=machine_type,
            disk_type=disk_type,
            disk_size=disk_size,
            options=options,
            **kwargs
        )

class StarlakeAirflowDataprocClusterConfig(StarlakeDataprocClusterConfig, StarlakeAirflowOptions):
    def __init__(self, cluster_id:str, dataproc_name:str, master_config: StarlakeAirflowDataprocMasterConfig, worker_config: StarlakeAirflowDataprocWorkerConfig, secondary_worker_config: StarlakeAirflowDataprocWorkerConfig, idle_delete_ttl: int, single_node: bool, options: dict, **kwargs):
        super().__init__(
            cluster_id=cluster_id,
            dataproc_name=dataproc_name,
            master_config=master_config,
            worker_config=worker_config,
            secondary_worker_config=secondary_worker_config,
            idle_delete_ttl=idle_delete_ttl,
            single_node=single_node,
            options=options,
            **kwargs
        )

class StarlakeAirflowDataprocCluster(StarlakeAirflowOptions):
    def __init__(self, cluster_config: StarlakeAirflowDataprocClusterConfig, options: dict, pool:str, **kwargs):
        super().__init__()

        self.options = {} if not options else options

        self.cluster_config = StarlakeAirflowDataprocClusterConfig(
            cluster_id=None,
            dataproc_name=None,
            master_config=None, 
            worker_config=None, 
            secondary_worker_config=None, 
            idle_delete_ttl=None, 
            single_node=None, 
            options=self.options,
            **kwargs
        ) if not cluster_config else cluster_config

        self.pool = pool

    def create_dataproc_cluster(
        self,
        cluster_id: str=None,
        task_id: str=None,
        cluster_name: str=None,
        **kwargs) -> BaseOperator:
        """
        Create the Cloud Dataproc cluster.
        This operator will be flagged a success if the cluster by this name already exists.
        """
        cluster_id = self.cluster_config.cluster_id if not cluster_id else cluster_id
        cluster_name = f"{self.cluster_config.dataproc_name}-{cluster_id.replace('_', '-')}-{TODAY}" if not cluster_name else cluster_name
        task_id = f"create_{cluster_id.replace('-', '_')}_cluster" if not task_id else task_id

        kwargs.update({
            'pool': kwargs.get('pool', self.pool),
            'trigger_rule': kwargs.get('trigger_rule', TriggerRule.ALL_SUCCESS)
        })

        spark_events_bucket = f'dataproc-{self.cluster_config.project_id}'

        return DataprocCreateClusterOperator(
            task_id=task_id,
            project_id=self.cluster_config.project_id,
            cluster_name=cluster_name,
            cluster_config=self.cluster_config.__config__(**{
                    "dataproc:job.history.to-gcs.enabled": "true",
                    "spark:spark.history.fs.logDirectory": f"gs://{spark_events_bucket}/tmp/spark-events/{{{{ds}}}}",
                    "spark:spark.eventLog.dir": f"gs://{spark_events_bucket}/tmp/spark-events/{{{{ds}}}}",
            }),
            region=self.cluster_config.region,
            **kwargs
        )

    def delete_dataproc_cluster(
        self,
        cluster_id: str=None,
        task_id: str=None,
        cluster_name: str=None,
        **kwargs) -> BaseOperator:
        """Tears down the cluster even if there are failures in upstream tasks."""
        cluster_id = self.cluster_config.cluster_id if not cluster_id else cluster_id
        cluster_name = f"{self.cluster_config.dataproc_name}-{cluster_id.replace('_', '-')}-{TODAY}" if not cluster_name else cluster_name
        task_id = f"delete_{cluster_id.replace('-', '_')}_cluster" if not task_id else task_id
        kwargs.update({
            'pool': kwargs.get('pool', self.pool),
            'trigger_rule': kwargs.get('trigger_rule', TriggerRule.NONE_SKIPPED)
        })
        return DataprocDeleteClusterOperator(
            task_id=task_id,
            project_id=self.cluster_config.project_id,
            cluster_name=cluster_name,
            region=self.cluster_config.region,
            **kwargs
        )

    def submit_starlake_job(
        self,
        cluster_id: str=None,
        task_id: str=None,
        cluster_name: str=None,
        spark_config: StarlakeSparkConfig=None,
        jar_list: list=None,
        main_class: str=None,
        arguments: list=None,
        **kwargs) -> BaseOperator:
        """Create a dataproc job on the specified cluster"""
        cluster_id = self.cluster_config.cluster_id if not cluster_id else cluster_id
        cluster_name = f"{self.cluster_config.dataproc_name}-{cluster_id.replace('_', '-')}-{TODAY}" if not cluster_name else cluster_name
        task_id = f"{cluster_id}_submit" if not task_id else task_id
        arguments = [] if not arguments else arguments
        jar_list = __class__.get_context_var(var_name="spark_jar_list", options=self.options).split(",") if not jar_list else jar_list
        main_class = __class__.get_context_var("spark_job_main_class", "ai.starlake.job.Main", self.options) if not main_class else main_class

        sparkBucket = __class__.get_context_var(var_name="spark_bucket", options=self.options)
        spark_properties = {
            "spark.hadoop.fs.defaultFS": f"gs://{sparkBucket}",
            "spark.eventLog.enabled": "true",
            "spark.sql.sources.partitionOverwriteMode": "DYNAMIC",
            "spark.sql.legacy.parquet.int96RebaseModeInWrite": "CORRECTED",
            "spark.sql.catalogImplementation": "in-memory",
            "spark.datasource.bigquery.temporaryGcsBucket": sparkBucket,
            "spark.datasource.bigquery.allowFieldAddition": "true",
            "spark.datasource.bigquery.allowFieldRelaxation": "true",
            "spark.dynamicAllocation.enabled": "false",
            "spark.shuffle.service.enabled": "false"
        }
        spark_config = StarlakeSparkConfig(memory=None, cores=None, instances=None, cls_options=self, options=self.options, **spark_properties) if not spark_config else StarlakeSparkConfig(memory=spark_config.memory, cores=spark_config.cores, instances=spark_config.instances, cls_options=self, options=self.options, **dict(spark_properties, **spark_config.spark_properties))

        kwargs.update({
            'pool': kwargs.get('pool', self.pool),
            'trigger_rule': kwargs.get('trigger_rule', TriggerRule.ALL_SUCCESS)
        })

        job_id = task_id + "_" + str(uuid.uuid4())[:8]

        return DataprocSubmitJobOperator(
            task_id=task_id,
            project_id=self.cluster_config.project_id,
            region=self.cluster_config.region,
            job={
                "reference": {
                    "project_id": self.cluster_config.project_id,
                    "job_id": job_id
                },
                "placement": {
                    "cluster_name": cluster_name
                },
                "spark_job": {
                    "jar_file_uris": jar_list,
                    "main_class": main_class,
                    "args": arguments,
                    "properties": {
                        **spark_config.__config__()
                    }
                }
            },
            **kwargs
        )

class StarlakeAirflowDataprocJob(StarlakeAirflowJob):
    """Airflow Starlake Dataproc Job."""
    def __init__(self, pre_load_strategy: Union[StarlakePreLoadStrategy, str, None]=None, cluster: StarlakeAirflowDataprocCluster=None, options: dict=None, **kwargs):
        super().__init__(pre_load_strategy=pre_load_strategy, options=options, **kwargs)
        self.cluster = StarlakeAirflowDataprocCluster(cluster_config=None, options=self.options, pool=self.pool) if not cluster else cluster

    def sl_job(self, task_id: str, arguments: list, spark_config: StarlakeSparkConfig=None, **kwargs) -> BaseOperator:
        """Overrides StarlakeAirflowJob.sl_job()
        Generate the Airflow task that will run the starlake command.
        
        Args:
            task_id (str): The required task id.
            arguments (list): The required arguments of the starlake command to run.
        
        Returns:
            BaseOperator: The Airflow task.
        """
        return self.cluster.submit_starlake_job(
            task_id=task_id,
            arguments=arguments,
            spark_config=spark_config,
            **kwargs
        )

    def pre_tasks(self, *args, **kwargs) -> Union[BaseOperator, None]:
        """Overrides StarlakeAirflowJob.pre_tasks()"""
        return self.cluster.create_dataproc_cluster(
            *args,
            **kwargs
        )

    def post_tasks(self, *args, **kwargs) -> Union[BaseOperator, None]:
        """Overrides StarlakeAirflowJob.post_tasks()"""
        return self.cluster.delete_dataproc_cluster(
            *args,
            **kwargs
        )
