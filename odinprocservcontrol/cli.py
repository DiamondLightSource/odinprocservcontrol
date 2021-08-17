import logging
import os
from argparse import ArgumentParser

import yaml
from softioc import asyncio_dispatcher, builder, softioc

from odinprocservcontrol import OdinProcServConfig, OdinProcServControl

__all__ = ["main"]


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "config",
        type=str,
        help="Config file specifying arguments - overrides any passed directly",
    )

    parser.add_argument("--ioc-name", type=str, help="IOC Name - e.g. BLXXY-CS-IOC-01")
    parser.add_argument(
        "--prefix", type=str, help="Prefix for PVs - e.g. BLXXY-CS-ODN-01"
    )
    parser.add_argument("--process-prefix", type=int, help="Prefix of Odin processes")
    parser.add_argument(
        "--process-count", type=int, help="Total number of odin processes"
    )
    parser.add_argument(
        "--server-process-name",
        type=str,
        help="Name of odin server process - e.g. BLXXY-EA-ODN-11",
    )
    parser.add_argument(
        "--server-delay", type=int, default=3, help="Delay before starting server"
    )
    parser.add_argument(
        "--adodin-ioc-name", type=str, help="Name of ADOdin IOC - e.g. BLXXY-EA-IOC-03"
    )
    parser.add_argument(
        "--ioc-delay", type=int, default=3, help="Delay before starting IOC"
    )

    parser.add_argument("--log-level", type=str, default="INFO", help="Log level")

    args = parser.parse_args()
    if args.config:
        with open(args.config) as config_file:
            config_text = config_file.read()
        config = yaml.load(config_text, Loader=yaml.FullLoader)
        args.__dict__.update(config)

    return args


def main():
    logging.basicConfig(
        format="[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    )

    args = parse_args()

    softioc.devIocStats(args.ioc_name)
    builder.SetDeviceName(args.prefix)
    builder.stringIn("WHOAMI", initial_value="OdinProcServControl")
    builder.stringIn("HOSTNAME", VAL=os.uname()[1])

    config = OdinProcServConfig(
        prefix=args.process_prefix,
        process_count=args.process_count,
        server_process_name=args.server_process_name,
        server_delay=args.server_delay,
        ioc_name=args.adodin_ioc_name,
        ioc_delay=args.ioc_delay,
    )
    OdinProcServControl(config, args.log_level)

    dispatcher = asyncio_dispatcher.AsyncioDispatcher()
    builder.LoadDatabase()
    softioc.iocInit(dispatcher)
    softioc.interactive_ioc(globals())
