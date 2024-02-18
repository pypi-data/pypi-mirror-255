"""Finetuning API"""
from __future__ import annotations

from concurrent.futures import Future
from typing import Dict, List, Optional, Union, overload

from typing_extensions import Literal

from mcli.api.engine.engine import get_return_response, run_singular_mapi_request
from mcli.api.model.finetune import Finetune
from mcli.models.finetune_config import FinetuneConfig
from mcli.utils.utils_config import ExperimentTrackerConfig

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


@overload
def create_finetuning_run(
    model: str,
    train_data_path: str,
    save_folder: str,
    *,
    task_type: Optional[str] = "INSTRUCTION_FINETUNE",
    eval_data_path: Optional[str] = None,
    eval_prompts: Optional[List[str]] = None,
    custom_weights_path: Optional[str] = None,
    training_duration: Optional[str] = None,
    learning_rate: Optional[float] = None,
    context_length: Optional[int] = None,
    experiment_tracker: Optional[ExperimentTrackerConfig] = None,
    disable_credentials_check: Optional[bool] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Finetune:
    ...


@overload
def create_finetuning_run(
    model: str,
    train_data_path: str,
    save_folder: str,
    *,
    task_type: Optional[str] = "INSTRUCTION_FINETUNE",
    eval_data_path: Optional[str] = None,
    eval_prompts: Optional[List[str]] = None,
    custom_weights_path: Optional[str] = None,
    training_duration: Optional[str] = None,
    learning_rate: Optional[float] = None,
    context_length: Optional[int] = None,
    experiment_tracker: Optional[ExperimentTrackerConfig] = None,
    disable_credentials_check: Optional[bool] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Future[Finetune]:
    ...


def create_finetuning_run(
    model: str,
    train_data_path: str,
    save_folder: str,
    *,
    task_type: Optional[str] = "INSTRUCTION_FINETUNE",
    eval_data_path: Optional[str] = None,
    eval_prompts: Optional[List[str]] = None,
    custom_weights_path: Optional[str] = None,
    training_duration: Optional[str] = None,
    learning_rate: Optional[float] = None,
    context_length: Optional[int] = None,
    experiment_tracker: Optional[ExperimentTrackerConfig] = None,
    disable_credentials_check: Optional[bool] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Union[Finetune, Future[Finetune]]:
    """Finetunes a model on a finetuning dataset and converts the final composer checkpoint to a
    Hugging Face formatted checkpoint for inference.

    Args:
        model: The name of the Hugging Face model to use.
        train_data_path: The full remote location of your training data (eg 's3://my-bucket/my-data.jsonl'). For
            ``INSTRUCTION_FINETUNE``, another option is to provide the name of a Hugging Face dataset that includes the
            train split, like 'mosaicml/dolly_hhrlhf/test'. The data should be formatted with each row containing a
            'prompt' and 'response' field for ``INSTRUCTION_FINETUNE``, or in raw data format for
            ``CONTINUED_PRETRAIN``.
        save_folder: The remote location to save the finetuned checkpoints. For example,
            if your ``save_folder`` is ``s3://my-bucket/my-checkpoints``, the finetuned Composer checkpoints
            will be saved to ``s3://my-bucket/my-checkpoints/<run-name>/checkpoints``, and Hugging Face formatted
            checkpoints will be saved to ``s3://my-bucket/my-checkpoints/<run-name>/hf_checkpoints``. The supported
            cloud provider prefixes are ``s3://``, ``gs://``, and ``oci://``.
        task_type: The type of finetuning task to run. Current available options are ``INSTRUCTION_FINETUNE``
            and ``CONTINUED_PRETRAIN``, defaults to ``INSTRUCTION_FINETUNE``.
        eval_data_path: The remote location of your evaluation data (e.g. ``s3://my-bucket/my-data.jsonl``). For
            ``INSTRUCTION_FINETUNE``, the name of a Hugging Face dataset with the test split
            (e.g. ``mosaicml/dolly_hhrlhf/test``) can also be given. The evaluation data should be formatted with each
            row containing a ``prompt`` and ``response`` field, for ``INSTRUCTION_FINETUNE`` and raw data for
            ``CONTINUED_PRETRAIN``. Default is ``None``.
        eval_prompts: A list of prompt strings to generate during training. Results will be logged to the experiment
            tracker(s) you've configured. Generations will occur at every model checkpoint with the following
            generation parameters:
                - max_new_tokens: 100
                - temperature: 1
                - top_k: 50
                - top_p: 0.95
                - do_sample: true
            Default is ``None`` (do not generate prompts).
        custom_weights_path: The remote location of a custom model checkpoint to use for finetuning. If provided,
            these weights will be used instead of the original pretrained weights of the model. This must be a Composer
            checkpoint. Default is ``None``.
        training_duration: The total duration of your finetuning run. This can be specified in batches
            (e.g. ``100ba``), epochs (e.g. ``10ep``), or tokens (e.g. ``1_000_000tok``). Default is ``1ep``.
        learning_rate: The peak learning rate to use for finetuning. Default is ``5e-7``. The optimizer used
            is DecoupledLionW with betas of 0.99 and 0.95 and no weight decay, and the learning rate scheduler used is
            LinearWithWarmupSchedule with a warmup of 2% of the total training duration and a final learning rate 
            multiplier of 0.
        context_length: The maximum sequence length to use. This will be used to truncate any data that is too long. 
            The default is the default for the provided Hugging Face model. We do not support extending the context
            length beyond each model's default.
        experiment_tracker: The configuration for an experiment tracker. For example, to add Weights and Biases
            tracking, you can pass in ``{"wandb": {"project": "my-project", "entity": "my-entity"}}``. To add in mlflow
            tracking, you can pass in ``{"mlflow": {"experiment_path": "my-experiment", "model_registry_path: 
            "catalog.schema.model_name"}}``.
        disable_credentials_check: Flag to disable checking credentials (S3, Databricks, etc.).
            If the credentials check is enabled (False), a preflight check will be ran on finetune submission, running
            a few tests to ensure that the credentials provided are valid for the resources you are attemption to
            access (S3 buckets, Databricks experiments, etc.). If the credential check fails, your finetune run will
            be stopped.
        timeout: Time, in seconds, in which the call should complete. If the run creation
            takes too long, a TimeoutError will be raised. If ``future`` is ``True``, this
            value will be ignored.
        future: Return the output as a :class:`~concurrent.futures.Future`. If True, the
            call to `finetune` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the :type Finetune: output, use ``return_value.result()``
            with an optional ``timeout`` argument.

    Returns:
        A :type Finetune: object containing the finetuning run information.
    """
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
        'disable_credentials_check': disable_credentials_check
    })
    finetune_config = config.to_create_finetune_api_input()
    variables = {
        VARIABLE_DATA_NAME: finetune_config,
    }

    response = run_singular_mapi_request(
        query=QUERY,
        query_function=QUERY_FUNCTION,
        return_model_type=Finetune,
        variables=variables,
    )
    return get_return_response(response, future=future, timeout=timeout)


def _db_create_finetuning_run(
    model: str,
    train_data_path: str,
    save_folder: str,
    *,
    task_type: Optional[str] = "INSTRUCTION_FINETUNE",
    eval_data_path: Optional[str] = None,
    eval_prompts: Optional[List[str]] = None,
    custom_weights_path: Optional[str] = None,
    training_duration: Optional[str] = None,
    learning_rate: Optional[float] = None,
    context_length: Optional[int] = None,
    data_prep_config: Optional[Dict[str, str]] = None,
    experiment_tracker: Optional[ExperimentTrackerConfig] = None,
    disable_credentials_check: Optional[bool] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Union[Finetune, Future[Finetune]]:
    """
    Internal API for databricks_genai because we are adding data_prep_config
    which is only used in the db gen ai sdk. We will clean this up by copying
    code over to the GenAI sdk so we can remove MCLI as a dependency, since this
    complicates our dev workflow and release cycle. I need to unblock the bug bash
    1/12, so I'm adding this private function for now.
    """
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
        'disable_credentials_check': disable_credentials_check
    })
    finetune_config = config.to_create_finetune_api_input()
    variables = {
        VARIABLE_DATA_NAME: finetune_config,
    }

    response = run_singular_mapi_request(
        query=QUERY,
        query_function=QUERY_FUNCTION,
        return_model_type=Finetune,
        variables=variables,
    )
    return get_return_response(response, future=future, timeout=timeout)


# TODO: deprecate in favor of create_finetuning_run
# Backwards compatibility
@overload
def finetune(
    model: str,
    train_data_path: str,
    save_folder: str,
    *,
    task_type: Optional[str] = "INSTRUCTION_FINETUNE",
    eval_data_path: Optional[str] = None,
    eval_prompts: Optional[List[str]] = None,
    custom_weights_path: Optional[str] = None,
    training_duration: Optional[str] = None,
    learning_rate: Optional[float] = None,
    context_length: Optional[int] = None,
    experiment_tracker: Optional[ExperimentTrackerConfig] = None,
    disable_credentials_check: Optional[bool] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Finetune:
    ...


@overload
def finetune(
    model: str,
    train_data_path: str,
    save_folder: str,
    *,
    task_type: Optional[str] = "INSTRUCTION_FINETUNE",
    eval_data_path: Optional[str] = None,
    eval_prompts: Optional[List[str]] = None,
    custom_weights_path: Optional[str] = None,
    training_duration: Optional[str] = None,
    learning_rate: Optional[float] = None,
    context_length: Optional[int] = None,
    experiment_tracker: Optional[ExperimentTrackerConfig] = None,
    disable_credentials_check: Optional[bool] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Future[Finetune]:
    ...


def finetune(
    model: str,
    train_data_path: str,
    save_folder: str,
    *,
    task_type: Optional[str] = "INSTRUCTION_FINETUNE",
    eval_data_path: Optional[str] = None,
    eval_prompts: Optional[List[str]] = None,
    custom_weights_path: Optional[str] = None,
    training_duration: Optional[str] = None,
    learning_rate: Optional[float] = None,
    context_length: Optional[int] = None,
    experiment_tracker: Optional[ExperimentTrackerConfig] = None,
    disable_credentials_check: Optional[bool] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Union[Finetune, Future[Finetune]]:
    return create_finetuning_run(
        model=model,
        train_data_path=train_data_path,
        save_folder=save_folder,
        task_type=task_type,
        eval_data_path=eval_data_path,
        eval_prompts=eval_prompts,
        custom_weights_path=custom_weights_path,
        training_duration=training_duration,
        learning_rate=learning_rate,
        context_length=context_length,
        experiment_tracker=experiment_tracker,
        disable_credentials_check=disable_credentials_check,
        timeout=timeout,
        future=future,
    )
