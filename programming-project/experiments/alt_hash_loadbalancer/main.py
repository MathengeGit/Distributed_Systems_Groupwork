import os
import random
import string
import threading
import time

import requests
from flask import Flask, request, jsonify
import docker

from consistent_hash import ConsistentHashMap

app = Flask(__name__)

M = int(os.environ.get("M", 512))
K = int(os.environ.get("K", 9))
N = int(os.environ.get("N", 3))
SERVER_IMAGE = os.environ.get("SERVER_IMAGE", "server:latest")
NETWORK = os.environ.get("NETWORK", "net1")
SERVER_PORT = 5000
GRACE_PERIOD_SECONDS = 8  # don't heartbeat-check a container until it's had time to boot

chm = ConsistentHashMap(M=M, K=K)
lock = threading.Lock()
docker_client = docker.from_env()

server_num_ids = {}
server_spawn_time = {}
_next_num_id = 1


def _random_hostname():
    return "S" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))


def _spawn_container(hostname: str):
    global _next_num_id
    docker_client.containers.run(
        SERVER_IMAGE,
        name=hostname,
        hostname=hostname,
        network=NETWORK,
        environment={"SERVER_ID": hostname},
        detach=True,
    )
    server_num_ids[hostname] = _next_num_id
    server_spawn_time[hostname] = time.time()
    _next_num_id += 1
    chm.add_server(server_num_ids[hostname], hostname)


def _remove_container(hostname: str):
    try:
        c = docker_client.containers.get(hostname)
        c.stop()
        c.remove()
    except docker.errors.NotFound:
        pass
    chm.remove_server(hostname)
    server_num_ids.pop(hostname, None)
    server_spawn_time.pop(hostname, None)


def _bootstrap(n_initial: int):
    with lock:
        for _ in range(n_initial):
            _spawn_container(_random_hostname())


def _heartbeat_loop():
    while True:
        time.sleep(4)
        with lock:
            hostnames = chm.servers()
        for hostname in hostnames:
            if time.time() - server_spawn_time.get(hostname, 0) < GRACE_PERIOD_SECONDS:
                continue  # still starting up, give it time before judging it dead
            try:
                r = requests.get(f"http://{hostname}:{SERVER_PORT}/heartbeat", timeout=2)
                ok = r.status_code == 200
            except requests.RequestException:
                ok = False
            if not ok:
                with lock:
                    if hostname in chm.hostname_slots:
                        print(f"[heartbeat] {hostname} unresponsive, respawning replacement")
                        _remove_container(hostname)
                        _spawn_container(_random_hostname())


@app.route("/rep", methods=["GET"])
def rep():
    with lock:
        replicas = chm.servers()
    return jsonify({
        "message": {"N": len(replicas), "replicas": replicas},
        "status": "successful"
    }), 200


@app.route("/add", methods=["POST"])
def add():
    payload = request.get_json(force=True)
    n = payload.get("n")
    hostnames = payload.get("hostnames", [])

    if n is None or n < 1:
        return jsonify({"message": "<Error> 'n' must be a positive integer", "status": "failure"}), 400
    if len(hostnames) > n:
        return jsonify({"message": "<Error> Length of hostname list is more than newly added instances",
                         "status": "failure"}), 400

    with lock:
        for i in range(n):
            hostname = hostnames[i] if i < len(hostnames) else _random_hostname()
            _spawn_container(hostname)
        replicas = chm.servers()

    return jsonify({
        "message": {"N": len(replicas), "replicas": replicas},
        "status": "successful"
    }), 200


@app.route("/rm", methods=["DELETE"])
def rm():
    payload = request.get_json(force=True)
    n = payload.get("n")
    hostnames = payload.get("hostnames", [])

    if n is None or n < 1:
        return jsonify({"message": "<Error> 'n' must be a positive integer", "status": "failure"}), 400
    if len(hostnames) > n:
        return jsonify({"message": "<Error> Length of hostname list is more than removable instances",
                         "status": "failure"}), 400

    with lock:
        current = chm.servers()
        to_remove = list(hostnames)
        remaining_pool = [h for h in current if h not in to_remove]
        extra_needed = n - len(to_remove)
        if extra_needed > 0:
            to_remove += random.sample(remaining_pool, min(extra_needed, len(remaining_pool)))

        for hostname in to_remove:
            if hostname in chm.hostname_slots:
                _remove_container(hostname)

        replicas = chm.servers()

    return jsonify({
        "message": {"N": len(replicas), "replicas": replicas},
        "status": "successful"
    }), 200


@app.route("/<path:path>", methods=["GET"])
def route_request(path):
    request_id = random.randint(100000, 999999)
    with lock:
        hostname = chm.get_server_for_request(request_id)

    if hostname is None:
        return jsonify({"message": "<Error> No server replicas available", "status": "failure"}), 400

    try:
        r = requests.get(f"http://{hostname}:{SERVER_PORT}/{path}", timeout=3)
        if r.status_code == 200:
            return (r.text, 200, {"Content-Type": "application/json"})
        else:
            return jsonify({"message": f"<Error> '/{path}' endpoint does not exist in server replicas",
                             "status": "failure"}), 400
    except requests.RequestException:
        return jsonify({"message": f"<Error> '/{path}' endpoint does not exist in server replicas",
                         "status": "failure"}), 400


if __name__ == "__main__":
    _bootstrap(N)
    t = threading.Thread(target=_heartbeat_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)