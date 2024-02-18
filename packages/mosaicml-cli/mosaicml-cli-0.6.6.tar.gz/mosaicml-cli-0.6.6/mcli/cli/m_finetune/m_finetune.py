""" mcli finetune Entrypoint """
import argparse
import logging
import textwrap
from http import HTTPStatus
from typing import Optional

from mcli.api.exceptions import MAPIException, cli_error_handler
from mcli.api.finetuning_runs import Finetune, create_finetuning_run
from mcli.models.finetune_config import FinetuneConfig
from mcli.utils.utils_logging import OK
from mcli.utils.utils_spinner import console_status
from mcli.utils.utils_yaml import load_yaml

logger = logging.getLogger(__name__)


def print_help(**kwargs) -> int:
    del kwargs
    mock_parser = argparse.ArgumentParser()
    _configure_parser(mock_parser)
    mock_parser.print_help()
    return 1


@cli_error_handler('mcli finetune')
# pylint: disable-next=too-many-statements
def finetune_entrypoint(
    file: Optional[str] = None,
    override_model: Optional[str] = None,
    override_task_type: Optional[str] = None,
    override_train_data_path: Optional[str] = None,
    override_training_duration: Optional[str] = None,
    override_save_folder: Optional[str] = None,
    override_eval_data_path: Optional[str] = None,
    override_learning_rate: Optional[float] = None,
    override_context_length: Optional[int] = None,
    override_custom_weights_path: Optional[str] = None,
    override_disable_credentials_check: Optional[bool] = None,
    **kwargs,
) -> int:
    del kwargs

    if not file:
        print_help()
        raise MAPIException(HTTPStatus.BAD_REQUEST, "Must specify a file to load arguments from")

    config_dict = load_yaml(file)
    # command line overrides
    # only supports basic format for now and not structured params
    if override_model is not None:
        config_dict['model'] = override_model

    if override_task_type is not None:
        config_dict['task_type'] = override_task_type

    if override_train_data_path is not None:
        config_dict['train_data_path'] = override_train_data_path

    if override_save_folder is not None:
        config_dict['save_folder'] = override_save_folder

    if override_eval_data_path is not None:
        config_dict['eval_data_path'] = override_eval_data_path

    if override_training_duration is not None:
        config_dict['training_duration'] = override_training_duration

    if override_learning_rate is not None:
        config_dict['learning_rate'] = override_learning_rate

    if override_context_length is not None:
        config_dict['context_length'] = override_context_length

    if override_custom_weights_path is not None:
        config_dict['custom_weights_path'] = override_custom_weights_path

    if override_disable_credentials_check is not None:
        config_dict['disable_credentials_check'] = override_disable_credentials_check

    with console_status('Submitting run...'):
        config_dict = FinetuneConfig.validate_dict(dict_to_use=config_dict)
        run = create_finetuning_run(**config_dict)
    return finish_finetune(run)


def finish_finetune(submitted_finetune: Finetune) -> int:
    log_cmd = f'mcli describe ft {submitted_finetune.name}'
    message = f"""
    {OK} Finetune [cyan]{submitted_finetune.name}[/] submitted.

    To see the finetune\'s status, use:

    [bold]mcli get ft[/]

    To see the finetune\'s events, use:

    [bold]{log_cmd}[/ ]
    """
    logger.info(textwrap.dedent(message).strip())
    return 0


def add_finetune_argparser(subparser: argparse._SubParsersAction) -> None:
    finetune_parser: argparse.ArgumentParser = subparser.add_parser(
        'finetune',
        aliases=['ft'],
        help='Launch a run in the MosaicML platform',
    )
    finetune_parser.set_defaults(func=finetune_entrypoint)
    _configure_parser(finetune_parser)


def _configure_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        '-f',
        '--file',
        dest='file',
        help='File from which to load arguments.',
    )

    parser.add_argument(
        '--model',
        dest='override_model',
        help='Optional override for model',
    )

    parser.add_argument(
        '--task-type',
        dest='override_task_type',
        help='Optional override for task_type',
    )

    parser.add_argument(
        '--train-data-path',
        dest='override_train_data_path',
        help='Optional override for training data path',
    )

    parser.add_argument(
        '--save-folder',
        dest='override_save_folder',
        help='Optional override for checkpoint save folder',
    )

    parser.add_argument(
        '--eval-data-path',
        dest='override_eval_data_path',
        help='Optional override for eval_data_path',
    )

    parser.add_argument(
        '--training-duration',
        dest='override_training_duration',
        help='Optional override for training duration',
    )

    parser.add_argument(
        '--learning-rate',
        type=float,
        dest='override_learning_rate',
        help='Optional override for learning rate (float)',
    )

    parser.add_argument(
        '--context-length',
        type=int,
        dest='override_context_length',
        help='Optional override for context length',
    )

    parser.add_argument(
        '--custom-weights-path',
        type=str,
        dest='override_custom_weights_path',
        help='Optional override for custom weights path',
    )

    parser.add_argument(
        '--disable-credentials-check',
        dest='override_disable_credentials_check',
        help='Optional override for disable credentials check',
        action='store_true',
        default=None,
    )
