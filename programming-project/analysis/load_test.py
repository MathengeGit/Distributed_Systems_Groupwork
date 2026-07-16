import sys
import time
import json
import requests
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

LB_URL = "http://localhost:5000"
NUM_REQUESTS = 10000
CONCURRENCY = 50


def fire_requests(n=NUM_REQUESTS):
    counts = {}

    def one_request(_):
        try:
            r = requests.get(f"{LB_URL}/home", timeout=5)
            if r.status_code == 200:
                msg = r.json().get("message", "")
                server_id = msg.split(":")[-1].strip()
                return server_id
        except requests.RequestException:
            return None
        return None

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        results = list(ex.map(one_request, range(n)))

    for server_id in results:
        if server_id:
            counts[server_id] = counts.get(server_id, 0) + 1
    return counts


def set_replicas(target_n):
    r = requests.get(f"{LB_URL}/rep").json()
    current_n = r["message"]["N"]
    if target_n > current_n:
        requests.post(f"{LB_URL}/add", json={"n": target_n - current_n, "hostnames": []})
    elif target_n < current_n:
        requests.delete(f"{LB_URL}/rm", json={"n": current_n - target_n, "hostnames": []})
    time.sleep(3)


def a1():
    counts = fire_requests(NUM_REQUESTS)
    print(json.dumps(counts, indent=2))
    plt.figure()
    plt.bar(counts.keys(), counts.values())
    plt.xlabel("Server")
    plt.ylabel("Requests handled")
    plt.title(f"Request distribution across servers (N={len(counts)}, {NUM_REQUESTS} requests)")
    """plt.savefig("a1_bar_chart.png")
    print("Saved a1_bar_chart.png")"""
    plt.savefig("../experiments/alt_hash_loadbalancer/results/a1_bar_chart_modified.png")


def a2():
    avg_loads = []
    ns = list(range(2, 7))
    for n in ns:
        set_replicas(n)
        counts = fire_requests(NUM_REQUESTS)
        avg = sum(counts.values()) / max(len(counts), 1)
        avg_loads.append(avg)
        print(f"N={n} -> avg load per server = {avg:.1f}, counts={counts}")

    plt.figure()
    plt.plot(ns, avg_loads, marker="o")
    plt.xlabel("N (number of servers)")
    plt.ylabel("Average requests handled per server")
    plt.title("Scalability: average load vs N")
    """plt.savefig("a2_line_chart.png")
    print("Saved a2_line_chart.png")
    plt.savefig("a2_line_chart.png")"""
    plt.savefig("../experiments/alt_hash_loadbalancer/results/a2_line_chart_modified.png")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "a1"
    if mode == "a1":
        a1()
    elif mode == "a2":
        a2()
    else:
        print("Usage: python3 load_test.py [a1|a2]")
