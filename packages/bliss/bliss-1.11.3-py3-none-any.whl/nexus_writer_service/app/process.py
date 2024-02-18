import sys
from nexus_writer_service.subscribers.session_writer import all_cli_saveoptions
from nexus_writer_service.subscribers.session_writer import logger
from nexus_writer_service.subscribers.session_writer import start_session_writer
from nexus_writer_service.utils import logging_utils
from nexus_writer_service.app.utils import config_root_logger


def main(argv=None):
    import argparse

    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description="Start python a process for saving Bliss data in HDF5"
    )
    parser.add_argument("session_name", type=str, help="Session name")
    cli_saveoptions = all_cli_saveoptions()
    for attr, okwargs in cli_saveoptions.items():
        parser.add_argument("--" + attr, **okwargs)
    logging_utils.add_cli_args(parser)

    # Parse CLI arguments
    args, _ = parser.parse_known_args(argv[1:])
    config_root_logger()
    kwargs = {}
    cli_saveoptions = all_cli_saveoptions(configurable=args.configurable)
    for attr, okwargs in cli_saveoptions.items():
        option = okwargs["dest"]
        try:
            kwargs[option] = getattr(args, option)
        except AttributeError:
            continue

    # Launch the session writer
    logid = "Session writer " + repr(args.session_name)
    processlogger = logging_utils.CustomLogger(logger, logid)
    processlogger.info("process started")
    writer = start_session_writer(args.session_name, **kwargs)
    writer.join()
    processlogger.info("process exits")


if __name__ == "__main__":
    sys.exit(main())
