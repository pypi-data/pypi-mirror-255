import logging
import sys
from argh import ArghParser
from scale_egp.cli.collections import (
    CollectionCRUDCommandsForImmutable,
    EGPClientFactory,
    FineTuningJobCommands,
    ModelDeploymentCommands,
    ModelInstanceCommands,
    ModelTemplateCommands,
    TrainingDatasetCommands,
    UserCommands,
    ModelGroupCommands,
)
from scale_egp.cli.formatter import AVAILABLE_FORMATTERS
from scale_egp.cli.parser import get_parser, dispatch


def add_commands_to_parser(parser: ArghParser, commands: CollectionCRUDCommandsForImmutable):
    parser.add_commands(
        [
            getattr(commands, key)
            for key in dir(commands)
            if not key.startswith("_") and callable(getattr(commands, key))
        ],
        group_name=commands.command_group_name,
        group_kwargs={
            "title": getattr(commands, "command_group_title", None),
            "help": getattr(commands, "__doc__", None),
        },
    )


def exec_cli():
    client_factory = EGPClientFactory()

    parser = get_parser()
    parser.add_argument("--log-curl-commands", action="store_true", default=False)
    parser.add_argument("-k", "--api-key", type=str, default=None, metavar="EGP_API_KEY")
    parser.add_argument(
        "-i",
        "--account-id",
        type=str,
        default=None,
        help="Optional EGP account_id to use. The default account_id will be used if not set.",
        metavar="EGP_ACCOUNT_ID",
    )
    parser.add_argument("-e", "--endpoint-url", type=str, default=None, metavar="EGP_ENDPOINT_URL")
    parser.add_argument(
        "-f", "--format", type=str, choices=[*AVAILABLE_FORMATTERS.keys()], default="rich"
    )
    add_commands_to_parser(parser, ModelGroupCommands(client_factory))
    add_commands_to_parser(parser, ModelInstanceCommands(client_factory))
    add_commands_to_parser(parser, ModelDeploymentCommands(client_factory))
    add_commands_to_parser(parser, ModelTemplateCommands(client_factory))
    add_commands_to_parser(parser, UserCommands(client_factory))
    add_commands_to_parser(parser, FineTuningJobCommands(client_factory))
    add_commands_to_parser(parser, TrainingDatasetCommands(client_factory))
    args = parser.parse_args()
    try:
        client_factory.set_client_kwargs(
            api_key=args.api_key,
            endpoint_url=args.endpoint_url,
            account_id=args.account_id,
            log_curl_commands=args.log_curl_commands,
        )
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)
    if args.log_curl_commands:
        logging.basicConfig(level=logging.INFO)
    dispatch(parser, args)
