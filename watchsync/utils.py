import os
import subprocess

from watchsync.logger import logger


def path(*args) -> str:
    exapnd_path = os.path.join(
        *(a.replace("~", os.path.expanduser("~")) for a in args)
    )
    return os.path.abspath(exapnd_path)


def shell(cmd, timeout=10, show_stdout=True, **kwargs):
    logger.debug(f"$: {cmd}")
    if not show_stdout:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            start_new_session=True,
            **kwargs,
        )
        return process.returncode
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True,
        **kwargs,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        if stdout:
            logger.debug(f"OK: {stdout}")
        if stderr:
            logger.debug(f"KO: {stdout}")
    except subprocess.TimeoutExpired:
        process.kill()
        logger.error(f"Timeout expired for command: {cmd}")
        raise
    if process.returncode != 0 and stderr:
        logger.error(f"Error executing command: {cmd}")
        logger.error(stderr)
        raise subprocess.CalledProcessError(
            process.returncode, cmd, output=stdout, stderr=stderr
        )
    return stdout.strip()
