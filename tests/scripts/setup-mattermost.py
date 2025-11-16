#!/usr/bin/env python
import logging
import os
import shutil
import subprocess
import sys
import time
import urllib.request

HOST = os.environ.get("MATTERMOST_HOST", "127.0.0.1")
PORT = os.environ.get("MATTERMOST_PORT", "8065")
BASE_URL = f"http://{HOST}:{PORT}"  # NOSONAR
CONTAINER = os.environ.get("MATTERMOST_CONTAINER", "mattermost-mmemoji")
TAG = os.environ.get(
    "MATTERMOST_VERSION",
    "11.1.0@sha256:af0db67ff568b5a00895b0d67e62b0cc6f415b7a478de1be5a1ca3e37c41ecfb",
)
IMAGE = f"docker.io/mattermost/mattermost-preview:{TAG}"

logger = logging.getLogger("setup-mattermost")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s %(name)s %(levelname)s - %(message)s")
)
if not logger.hasHandlers():
    logger.addHandler(handler)


def check_docker_available() -> None:
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("Docker needs to be installed and running!")
    try:
        subprocess.run(
            ["docker", "info"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "Docker needs to be installed and running!"
        ) from None


def run_container() -> None:
    logger.info("Creating test instance...")
    cmd = [
        "docker",
        "run",
        "--detach",
        f"--name={CONTAINER}",
        "--env=MM_SERVICESETTINGS_ENABLECUSTOMEMOJI=true",
        "--env=MM_SERVICESETTINGS_ENABLELOCALMODE=true",
        f"--publish={HOST}:{PORT}:8065",
        "--add-host=dockerhost:127.0.0.1",
        IMAGE,
    ]
    subprocess.run(cmd, check=True)


def wait_for_ready(retries: int = 300, interval: float = 1.0) -> None:
    logger.info("Waiting for instance to be ready...")
    url = f"{BASE_URL}/api/v4/system/ping"
    req = urllib.request.Request(url, method="GET")
    for attempt in range(1, max(1, retries) + 1):
        try:
            with urllib.request.urlopen(req, timeout=interval) as resp:
                if resp.status == 200:
                    return
        except OSError as e:
            logger.debug("Ping failed: %s", e)
        if attempt < retries:
            time.sleep(interval)
    raise RuntimeError(
        f"Failed to reach {url} after {retries} attempts"
    ) from None


def load_sample_data() -> None:
    logger.info("Loading sample data...")
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "mmctl",
        "--local",
        "sampledata",
        "--channel-memberships=1",
        "--channels-per-team=1",
        "--direct-channels=0",
        "--group-channels=0",
        "--guests=0",
        "--posts-per-channel=0",
        "--posts-per-direct-channel=0",
        "--posts-per-group-channel=0",
        "--team-memberships=1",
        "--teams=1",
        "--users=2",
    ]
    subprocess.run(cmd, check=True)


def print_finish_message() -> None:
    logger.info("Your environment is ready!")
    logger.info(
        "The following users should have been created:\n\n"
        "Username           Email                           Password\n"
        "-----------------  ------------------------------  --------\n"
        "sysadmin           sysadmin@sample.mattermost.com  Sys@dmin-sample1\n"
        "user-1             user-1@sample.mattermost.com    SampleUs@r-1\n"
    )


def main() -> int:
    try:
        check_docker_available()
        run_container()
        wait_for_ready()
        load_sample_data()
        print_finish_message()
        return 0
    except RuntimeError as e:
        logger.error(e)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
