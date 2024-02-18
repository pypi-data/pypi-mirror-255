import os
import asyncio
import logging
import json

from typing import Tuple, Optional, Dict
from datetime import datetime


def get_env(name: str, default_value=None):
    """Returns the enviroment variable, if default_value
    is provided will return the default value.

    Arguments:
        name {str} -- The name of the enviroment variable.

    Keyword Arguments:
        default_value {any} -- The default value (default: {None})

    Returns:
        any -- The value of the enviroment variable.
    """
    value = None
    if value is None:
        value = os.environ.get(name, default_value)
    if value is None and default_value is not None:
        value = default_value

    if not value:
        raise ValueError(f"Env variable {name} was not set")
    return value

def run_custom_image_tap_and_target(project_name: str = "", config: Dict = {}):
    with open("config.json", "w") as config_file:
        config_file.write(json.dumps(config))

    tap_cmd = f"python {project_name}/tap/{project_name}_tap.py --config config.json"
    target_cmd = f"python {project_name}/target/{project_name}_target.py --config config.json"

    try:
        asyncio.run(
            _run_tap_and_target(
                tap_cmd=tap_cmd,
                target_cmd=target_cmd,
            )
        )
    except Exception as e:
        raise RuntimeError(str(e))

async def _run_tap_and_target(tap_cmd: str, target_cmd: str) -> Tuple[int, int]:
    start = datetime.now()
    logging.info(f"Starting command {tap_cmd} and {target_cmd}")

    read, write = os.pipe()
    tap = await asyncio.subprocess.create_subprocess_shell(
        tap_cmd, stdout=write, stderr=asyncio.subprocess.PIPE
    )
    os.close(write)
    target = await asyncio.subprocess.create_subprocess_shell(
        target_cmd, stdin=read, stderr=asyncio.subprocess.PIPE
    )
    os.close(read)

    await asyncio.wait([_log_stderr_msg(tap.stderr), _log_stderr_msg(target.stderr)])
    tap_return_code = await tap.wait()
    target_return_code = await target.wait()

    finish = datetime.now()
    logging.debug(
        f"Finished command {tap_cmd} and {target_cmd} at {finish.isoformat()}"
    )
    logging.info(
        f"Command {tap_cmd} and {target_cmd} finished in {(finish - start).total_seconds()} seconds"
    )
    return tap_return_code, target_return_code


async def _log_stderr_msg(stream: Optional[asyncio.StreamReader]):
    if isinstance(stream, asyncio.StreamReader):
        while True:
            line = await stream.readline()
            if line:
                msg = line.decode().strip()
                if "level=CRITICAL" in msg:
                    logging.critical(msg)
                elif "level=ERROR" in msg:
                    logging.error(msg)
                elif "level=WARNING" in msg:
                    logging.warning(msg)
                elif "level=DEBUG" in msg:
                    logging.debug(msg)
                else:
                    logging.info(msg)
            else:
                break
