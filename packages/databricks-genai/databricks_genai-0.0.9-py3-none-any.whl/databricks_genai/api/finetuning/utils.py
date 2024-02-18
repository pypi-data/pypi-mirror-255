"""Utils for finetuning API"""
import json
import os
import re
from typing import Optional

from databricks.sdk import WorkspaceClient
from datasets import get_dataset_split_names
from mcli.api.exceptions import ValidationError
from mlflow import MlflowClient
from packaging import version

_UC_VOLUME_LIST_API_ENDPOINT = '/api/2.0/fs/list'
MIN_DBR_VERSION = version.parse('12.2')
DB_CONNECT_DBR_VERSION = version.parse('14.1')
SAVE_FOLDER_PATH = 'dbfs:/databricks/mlflow-tracking/{mlflow_experiment_id}/{mlflow_run_id}/artifacts'


def validate_register_to(path: str) -> None:
    split_path = path.split('.')
    if len(split_path) == 2:
        catalog, schema_name = split_path
    elif len(split_path) == 3:
        catalog, schema_name, _ = split_path
    else:
        raise ValidationError(f'register_to must be in the format '
                              f'catalog.schema or catalog.schema.model_name, but got {path}')
    for component in split_path:
        if len(component) == 0:
            raise ValidationError(f'register_to must be in the format '
                                  f'catalog.schema or catalog.schema.model_name, but got {path}')
    validate_catalog_schema(catalog, schema_name, "register_to")


def validate_delta_table(path: str, input_type: str) -> None:
    split_path = path.split('.')
    if len(split_path) != 3:
        raise ValidationError(f'Delta table input to {input_type} must be in the format '
                              f'catalog.schema.table, but got {path}.')
    for component in split_path:
        if len(component) == 0:
            raise ValidationError(f'Delta table input to {input_type} must be in the format '
                                  f'catalog.schema.table, but got {path}.')
    catalog, schema, _ = split_path
    validate_catalog_schema(catalog, schema, input_type)


def validate_catalog_schema(catalog: str, schema_name: str, input_type: str) -> None:
    w = WorkspaceClient()
    try:
        schemas = w.schemas.list(catalog)
        if schema_name not in [schema.name for schema in schemas]:
            raise ValidationError(f'Failed to find schema "{schema_name}" in catalog "{catalog}". Please make sure '
                                  f'your {input_type} is valid and exists in the Unity Catalog.')
    except Exception as e:
        raise ValidationError(f'Failed to get schemas for catalog "{catalog}". Please make sure your '
                              f'{input_type} is valid and exists in the Unity Catalog.') from e


def validate_experiment_path(experiment_path: str) -> None:
    try:
        client = MlflowClient(tracking_uri='databricks')
        experiment = client.get_experiment_by_name(experiment_path)
        if not experiment:
            client.create_experiment(experiment_path)
    except Exception as e:
        raise ValidationError(f'Failed to get or create MLflow experiment {experiment_path}. Please make sure '
                              'your experiment name is valid.') from e


def find_a_txt_file(object_path: str) -> bool:
    # comes from Composer UCObjectStore
    client = WorkspaceClient()

    try:
        resp = client.api_client.do(method='GET',
                                    path=_UC_VOLUME_LIST_API_ENDPOINT,
                                    data=json.dumps({'path': object_path}),
                                    headers={'Source': 'mosaicml/finetuning'})
    except Exception as exc:
        raise ValidationError(
            f'Failed to access Unity Catalog path {object_path}. Ensure continued pretrain input is a Unity '
            'Catalog volume path to a folder.') from exc

    # repeat GET on original path to avoid duplicate code
    stack = [object_path]

    while len(stack) > 0:
        current_path = stack.pop()

        # Note: Databricks SDK handles HTTP errors and retries.
        # See https://github.com/databricks/databricks-sdk-py/blob/v0.18.0/databricks/sdk/core.py#L125 and
        # https://github.com/databricks/databricks-sdk-py/blob/v0.18.0/databricks/sdk/retries.py#L33 .
        resp = client.api_client.do(method='GET',
                                    path=_UC_VOLUME_LIST_API_ENDPOINT,
                                    data=json.dumps({'path': current_path}),
                                    headers={'Source': 'mosaicml/finetuning'})

        assert isinstance(resp, dict), 'Response is not a dictionary'

        for f in resp.get('files', []):
            fpath = f['path']
            if f['is_dir']:
                stack.append(fpath)
            else:
                if f['path'].endswith('.txt'):
                    return True
    return False


def validate_uc_path(uc_path: str, task_type: str) -> None:
    """
    Validates the user's read access to a Unity Catalog path. If `task_type==INSTRUCTION_FINETUNE`, ensures 
    that the path ends with a jsonl file. Else, ensures that the path is a folder that contains a txt file.
    """
    if not uc_path.startswith("dbfs:/Volumes"):
        raise ValidationError('Databricks Unity Catalog Volumes paths should start with "dbfs:/Volumes".')
    path = os.path.normpath(uc_path[len("dbfs:/"):])
    dirs = path.split(os.sep)
    if len(dirs) < 4:
        raise ValidationError(f'Databricks Unity Catalog Volumes path expected to start with ' \
            f'`dbfs:/Volumes/<catalog-name>/<schema-name>/<volume-name>`. Found path={uc_path}')
    object_path = "/" + path
    if task_type == "INSTRUCTION_FINETUNE":
        if not object_path.endswith(".jsonl"):
            raise ValidationError(f"Unity Catalog input for instruction finetuning must be a jsonl file. Got {uc_path}")
        try:
            client = WorkspaceClient()
            client.files.get_status(object_path)
        except Exception as e:
            raise ValidationError(f"Failed to access Unity Catalog path {uc_path}.") from e
    else:
        if not find_a_txt_file(object_path):
            raise ValidationError(
                f"Could not find a .txt file in Unity Catalog path {uc_path}. Continued pretrain input must be a "
                "folder containing a .txt file.")


def validate_hf_dataset(dataset_name_with_split: str) -> None:
    print(f"Assuming {dataset_name_with_split} is a Hugging Face dataset (not in format `dbfs:/Volumes` or "
          "`/Volumes`). Validating...")
    split_dataset_name = dataset_name_with_split.split('/')
    if len(split_dataset_name) < 2:
        raise ValidationError(
            f"Hugging Face dataset {dataset_name_with_split} must be in the format <dataset>/<split> or "
            "<entity>/<dataset>/<split>.")
    dataset_name, split = '/'.join(split_dataset_name[0:-1]), split_dataset_name[-1]
    try:
        splits = get_dataset_split_names(dataset_name)
    except Exception as e:
        raise ValidationError(
            f"Failed to access Hugging Face dataset {dataset_name_with_split}. Please make sure that the split "
            "is valid and that your dataset does not have subsets.") from e
    if split not in splits:
        raise ValidationError(f"Failed to access Hugging Face dataset {dataset_name_with_split}. Split not found.")
    print("Hugging Face dataset validation successful.")


def validate_data_prep(data_prep_cluster: Optional[str] = None):
    if data_prep_cluster is None:
        raise ValidationError(
            "Providing a delta table for train data or eval data requires specifying a data_prep_cluster.")
    user_has_access_to_cluster(data_prep_cluster)


def validate_custom_weights_path(custom_weights_path: str):
    mlflow_dbfs_path_prefix = 'dbfs:/databricks/mlflow-tracking/'
    # dbfs will be prepended before this if the user input `/databricks`
    mlflow_custom_weights_regex = (r"^dbfs:\/databricks\/mlflow-tracking"
                                   r"\/[0-9]+\/[0-9a-z]+\/artifacts($|\/[\/a-zA-Z0-9 ()_\\\-.]*$)")
    if not re.match(mlflow_custom_weights_regex, custom_weights_path):
        raise ValidationError("Custom weights path must be in the format [dbfs:]/databricks/mlflow-tracking/"
                              "<experiment_id>/<run_id>/artifacts/<path>. "
                              f"Found {custom_weights_path}")
    if not custom_weights_path.endswith('.pt'):
        raise ValidationError("Custom weights path must be a valid pytorch checkpoint file ending with '.pt'")
    subpath = custom_weights_path[len(mlflow_dbfs_path_prefix):]
    _, run_id, _, artifact_path = subpath.split('/', maxsplit=3)
    artifact_dir = os.path.dirname(artifact_path)
    client = MlflowClient(tracking_uri='databricks')
    for artifact in client.list_artifacts(run_id, artifact_dir):
        if not artifact.is_dir and artifact.path == artifact_path:
            return
    raise ValidationError(f"Could not find file for custom_weights_path {custom_weights_path}")


def user_has_access_to_cluster(cluster_id: str):
    if cluster_id == 'serverless':
        return  # TODO can PrPr users access this?
    w = WorkspaceClient()
    try:
        w.clusters.get(cluster_id=cluster_id)
    except Exception as e:
        raise ValidationError(
            f'You do not have access to the cluster you provided: {cluster_id}. Please try again with another cluster.'
        ) from e


def is_cluster_sql(cluster_id: str) -> bool:
    # Returns True if DBR version < 14.1 and requires SqlConnect
    # Returns False if DBR version >= 14.1 and can use DBConnect
    if cluster_id == 'serverless':
        return False
    w = WorkspaceClient()
    cluster = w.clusters.get(cluster_id=cluster_id)
    stripped_runtime = re.sub(r'[a-zA-Z]', '', cluster.spark_version.split('-scala')[0].replace('x-snapshot', ''))
    runtime_version = re.sub(r'[.-]*$', '', stripped_runtime)
    if version.parse(runtime_version) < MIN_DBR_VERSION:
        raise ValidationError(
            'The cluster you provided is not compatible: please use a cluster with a DBR version > {MIN_DBR_VERSION}')
    if version.parse(runtime_version) < DB_CONNECT_DBR_VERSION:
        return True
    return False


def validate_create_finetuning_run_inputs(train_data_path: str,
                                          register_to: Optional[str] = None,
                                          experiment_path: Optional[str] = None,
                                          eval_data_path: Optional[str] = None,
                                          data_prep_cluster: Optional[str] = None,
                                          custom_weights_path: Optional[str] = None,
                                          task_type: str = "INSTRUCTION_FINETUNE") -> None:
    delta_table_used = False
    if task_type == "INSTRUCTION_FINETUNE":
        if train_data_path.startswith('dbfs:/'):
            validate_uc_path(train_data_path, task_type)
        elif "/" in train_data_path:  # assume HF dataset TODO state this assumption in docs
            validate_hf_dataset(train_data_path)
        else:
            delta_table_used = True
            validate_delta_table(train_data_path, "train_data_path")
    else:  # task type == "CONTINUED_PRETRAIN"
        validate_uc_path(train_data_path, task_type)
    if register_to:
        validate_register_to(register_to)
    if experiment_path:
        validate_experiment_path(experiment_path)
    if eval_data_path is None:
        pass
    elif task_type == "INSTRUCTION_FINETUNE":
        if eval_data_path.startswith('dbfs:/'):
            validate_uc_path(eval_data_path, task_type)
        elif "/" in eval_data_path:  # assume HF
            validate_hf_dataset(eval_data_path)
        else:
            delta_table_used = True
            validate_delta_table(eval_data_path, "eval_data_path")
    else:  # task type == "CONTINUED_PRETRAIN"
        validate_uc_path(eval_data_path, task_type)
    if delta_table_used:
        validate_data_prep(data_prep_cluster)
    if custom_weights_path:
        validate_custom_weights_path(custom_weights_path)


def format_path(path: str) -> str:
    """
    Prepends `dbfs:` in front of paths that start with `/Volumes` or `/databricks`.
    """
    if isinstance(path, str) and (path.startswith('/Volumes') or path.startswith('/databricks')):
        return f'dbfs:{path}'
    else:
        return path
