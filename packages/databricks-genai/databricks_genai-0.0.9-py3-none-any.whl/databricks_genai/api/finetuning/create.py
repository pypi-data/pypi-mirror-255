"""Create a finetuning run"""

from typing import Dict, List, Optional, Union

from mcli.api.engine.engine import get_return_response, run_singular_mapi_request

from databricks_genai.api.config import configure_request, get_me
from databricks_genai.api.finetuning.utils import (SAVE_FOLDER_PATH, format_path, is_cluster_sql,
                                                   validate_create_finetuning_run_inputs)
from databricks_genai.types.finetuning import FinetuningRun
from databricks_genai.types.finetuning.finetune_config import FinetuneConfig

QUERY_FUNCTION = 'createFinetune'
VARIABLE_DATA_NAME = 'createFinetuneData'
# This returns the same data that the create_run function returns
# for consistency when rendering the describe output
QUERY = f"""
mutation CreateFinetune(${VARIABLE_DATA_NAME}: CreateFinetuneInput!) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}) {{
    id
    name
    status
    createdById
    createdByEmail
    createdAt
    updatedAt
    startedAt
    completedAt
    reason
    isDeleted
    details {{
        model
        taskType
        trainDataPath
        saveFolder
        evalDataPath
        evalPrompts
        trainingDuration
        learningRate
        contextLength
        dataPrepConfig
        experimentTracker
        customWeightsPath
    }}
  }}
}}"""


@configure_request
def create(
    model: str,
    train_data_path: str,
    register_to: str,
    *,
    experiment_path: Optional[str] = "{}",
    task_type: Optional[str] = "INSTRUCTION_FINETUNE",
    eval_data_path: Optional[str] = None,
    eval_prompts: Optional[List[str]] = None,
    custom_weights_path: Optional[str] = None,
    training_duration: Optional[str] = None,
    learning_rate: Optional[float] = None,
    context_length: Optional[int] = None,
    validate_inputs: Optional[bool] = True,
    data_prep_cluster_id: Optional[str] = None,
) -> FinetuningRun:
    """Create a finetuning run

    Args:
        model (str): The name of the Hugging Face model to use.
        train_data_path (str): The full remote location of your training data.
            The format of this data depends on the task type:
            - ``INSTRUCTION_FINETUNE``:  JSONL format, where each line is a 
                prompt and response JSON object, for example:
                {"prompt": "What is the capital of France?", "response": "Paris"}
            - ``CONTINUED_PRETRAIN``: A text file containing raw text data.
        register_to (str): A Unity Catalog location where the model will
            be registered after training for easy deployment. Specify a location
            as either ``<catalog_name>.<schema_name>`` or
            ``<catalog_name>.<schema_name>.<model_name>``. The former will create
            a model with the same name as the finetuning run.
        experiment_path (str, optional): The path to the MLflow experiment where
            the final model checkpoint will be saved. Defaults to the run name
        task_type (str, optional): The type of task to train for. Options:
            - ``INSTRUCTION_FINETUNE`` (default): Finetune a model with instructions
                relative to a specific task.
            - ``CONTINUED_PRETRAIN``: Continue pretraining a model using additional
                raw text data.
        eval_data_path (str, optional): The remote location of your evaluation data
            (if any). Defaults to no evaluation. Must follow the same format as
            ``train_data_path``.
        eval_prompts (List[str], optional): A list of prompt strings to generate 
            during evaluation. Results will be logged to the experiment every tim
            the model is checkpointed. Default is ``None`` (do not generate prompts).
        custom_weights_path (str, None) The remote location of a custom model checkpoint 
            to use for finetuning. If provided, these weights will be used instead of 
            the original pretrained weights of the model. This must be a Composer 
            checkpoint. Default is ``None``.
        training_duration: The total duration of your finetuning run. 
            This can be specified:
            - In batches (e.g. ``100ba``)
            - In epochs (e.g. ``10ep``)
            - In tokens (e.g. ``1_000_000tok``)
            Default is ``1ep``.
        learning_rate: The peak learning rate to use for finetuning. Default is ``5e-7``. 
        context_length: The maximum sequence length to use. This will be used to truncate
            any data that is too long. The default is the default for the provided Hugging 
            Face model. We do not support extending the context length beyond each model's
            default.
        validate_inputs: Whether to validate the access to input paths before submitting 
            the finetuning job. Default is ``True``.
        data_prep_cluster_id: Cluster id for Spark data processing.
            This is required to support Delta table as an input for the finetuning API
            because we need to concatenate underlying Delta data files into a single location 
            and then convert to JSONL for IFT, and MDS for CPT.

    Returns:
        FinetuningRun: The finetuning run object that was created
    """
    databricks_username = get_me()
    experiment_tracker = {
        'mlflow': {
            'experiment_path': f'/Users/{databricks_username}/{experiment_path}',
            'model_registry_path': register_to,
        }
    }

    train_data_path = format_path(train_data_path)
    if eval_data_path is not None:
        eval_data_path = format_path(eval_data_path)
    if custom_weights_path is not None:
        custom_weights_path = format_path(custom_weights_path)
    save_folder = SAVE_FOLDER_PATH
    if validate_inputs:
        # don't validate experiment path if it's the default
        # TODO: create FinetuneConfig object for this SDK, so we can pass in object
        # instead of a list of params in the next line
        experiment_path_to_validate = experiment_tracker['mlflow'][
            'experiment_path'] if experiment_path != "{}" else None
        validate_create_finetuning_run_inputs(train_data_path, register_to, experiment_path_to_validate, eval_data_path,
                                              data_prep_cluster_id, custom_weights_path)
    data_prep_config: Optional[Dict[str, Union[str, bool]]] = None
    # TODO: add translations for snake to camel case
    if data_prep_cluster_id is not None:
        data_prep_config = {'clusterId': data_prep_cluster_id}
        if is_cluster_sql(data_prep_cluster_id):
            data_prep_config['useSql'] = True

    config = FinetuneConfig.from_dict({
        'model': model,
        'task_type': task_type,
        'train_data_path': train_data_path,
        'save_folder': save_folder,
        'eval_data_path': eval_data_path,
        'eval_prompts': eval_prompts,
        'training_duration': training_duration,
        'experiment_tracker': experiment_tracker,
        'learning_rate': learning_rate,
        'context_length': context_length,
        'custom_weights_path': custom_weights_path,
        'data_prep_config': data_prep_config,
        'disable_credentials_check': not validate_inputs,
    })
    finetune_config = config.to_create_finetune_api_input()
    variables = {
        VARIABLE_DATA_NAME: finetune_config,
    }

    response = run_singular_mapi_request(
        query=QUERY,
        query_function=QUERY_FUNCTION,
        return_model_type=FinetuningRun,
        variables=variables,
    )
    return get_return_response(response)
