import sys
from nexus_writer_service.tango.servers import NexusWriter
from nexus_writer_service.utils.logging_utils import add_cli_args
from nexus_writer_service.utils.log_levels import tango_cli_slog_level
from nexus_writer_service.utils.log_levels import add_tango_cli_args
from nexus_writer_service.app.utils import config_root_logger


def run(server, instance, log_level):
    """
    :param str server: device server name
    :param str instance: device server instance name
    :param str log_level:
    :returns Util:
    """
    verbose = tango_cli_slog_level.get(log_level, 0)
    if verbose:
        verbose = "-v{:d}".format(verbose)
        serverargs = [server, instance, verbose]
    else:
        serverargs = [server, instance]
    return NexusWriter.main(args=serverargs)


def main(argv=None):
    import argparse

    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description="Start a Tango server for saving Bliss data in HDF5"
    )
    parser.add_argument(
        "instance",
        type=str,
        default="nexuswriters",
        help="Server instance name ('nexuswriters' by default)",
    )
    parser.add_argument(
        "--server",
        type=str,
        default="nexuswriter",
        help="Server name ('nexuswriter' by default)",
    )
    add_tango_cli_args(parser)
    add_cli_args(parser)
    args, _ = parser.parse_known_args(argv[1:])
    config_root_logger()
    run(args.server, args.instance, args.log_tango)


if __name__ == "__main__":
    sys.exit(main())
