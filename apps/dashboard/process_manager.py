import subprocess
import json
import time
import os

STATUS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dashboard_status.json")
DOCKER_DESKTOP_PATH = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"  # adjust if installed elsewhere
REDIS_CONTAINER_NAME = "yatra-redis"


def _read_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {}


def _write_status(data):
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f)


def is_docker_running():
    result = subprocess.run(["docker", "info"], capture_output=True)
    return result.returncode == 0


def start_docker(timeout=60):
    # 1. Start Docker Desktop if Docker isn't running
    if not is_docker_running():
        subprocess.Popen([DOCKER_DESKTOP_PATH])

        waited = 0
        while waited < timeout:
            if is_docker_running():
                break

            time.sleep(3)
            waited += 3
        else:
            return {
                "ok": False,
                "message": "Docker Desktop didn't start in time. Check it manually."
            }

    # 2. Check whether the Redis container exists
    container_exists = subprocess.run(
        [
            "docker",
            "ps",
            "-a",
            "--filter",
            f"name=^{REDIS_CONTAINER_NAME}$",
            "-q"
        ],
        capture_output=True,
        text=True
    ).stdout.strip()

    # 3. If it exists, start it
    if container_exists:
        running = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                f"name=^{REDIS_CONTAINER_NAME}$",
                "--filter",
                "status=running",
                "-q"
            ],
            capture_output=True,
            text=True
        ).stdout.strip()

        if not running:
            result = subprocess.run(
                ["docker", "start", REDIS_CONTAINER_NAME],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {
                    "ok": False,
                    "message": f"Failed to start Redis: {result.stderr.strip()}"
                }

    # 4. If it doesn't exist, create it
    else:
        result = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "-p",
                "6379:6379",
                "--name",
                REDIS_CONTAINER_NAME,
                "redis"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {
                "ok": False,
                "message": f"Failed to create Redis: {result.stderr.strip()}"
            }

    # 5. Verify Redis is actually running
    running = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            f"name=^{REDIS_CONTAINER_NAME}$",
            "--filter",
            "status=running",
            "-q"
        ],
        capture_output=True,
        text=True
    ).stdout.strip()

    if not running:
        return {
            "ok": False,
            "message": "Redis container exists but is not running."
        }

    return {
        "ok": True,
        "message": "Docker and Redis started."
    }


def stop_docker():
    subprocess.run(["docker", "stop", REDIS_CONTAINER_NAME], capture_output=True)
    subprocess.run(["taskkill", "/IM", "Docker Desktop.exe", "/F"], capture_output=True)
    return {"ok": True, "message": "Docker stopped."}


def start_worker():
    proc = subprocess.Popen(
        ["celery", "-A", "config", "worker", "--loglevel=info", "--pool=solo"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    status = _read_status()
    status["worker_pid"] = proc.pid
    _write_status(status)
    return {"ok": True, "message": f"Worker started (PID {proc.pid})."}


def start_beat():
    proc = subprocess.Popen(
        ["celery", "-A", "config", "beat", "--loglevel=info"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    status = _read_status()
    status["beat_pid"] = proc.pid
    _write_status(status)
    return {"ok": True, "message": f"Beat started (PID {proc.pid})."}


def stop_process(pid_key):
    status = _read_status()
    pid = status.get(pid_key)
    if pid:
        subprocess.run(["taskkill", "/PID", str(pid), "/F", "/T"], capture_output=True)
        status[pid_key] = None
        _write_status(status)
    return {"ok": True}


def stop_worker():
    return stop_process("worker_pid")


def stop_beat():
    return stop_process("beat_pid")


def start_everything():
    docker_result = start_docker()
    if not docker_result["ok"]:
        return docker_result
    start_worker()
    start_beat()
    return {"ok": True, "message": "Docker, worker, and beat all started."}


def stop_everything():
    stop_worker()
    stop_beat()
    stop_docker()
    return {"ok": True, "message": "Everything stopped."}