import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


URL = "http://127.0.0.1:8000/health"

TOTAL_REQUESTS = 50
CONCURRENT_USERS = 10


def send_request():
    start = time.perf_counter()

    try:
        response = requests.get(URL, timeout=10)

        latency = (time.perf_counter() - start) * 1000

        return {
            "status": response.status_code,
            "latency_ms": latency,
            "success": response.status_code == 200,
        }

    except Exception as exc:
        return {
            "status": None,
            "latency_ms": None,
            "success": False,
            "error": str(exc),
        }


def main():
    print("Load / Concurrency Test")
    print("-----------------------")
    print(f"Endpoint: {URL}")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Concurrent users: {CONCURRENT_USERS}")
    print()

    start = time.perf_counter()

    results = []

    with ThreadPoolExecutor(
        max_workers=CONCURRENT_USERS
    ) as executor:

        futures = [
            executor.submit(send_request)
            for _ in range(TOTAL_REQUESTS)
        ]

        for future in as_completed(futures):
            results.append(future.result())

    total_time = time.perf_counter() - start

    successful = [
        result for result in results
        if result["success"]
    ]

    failed = len(results) - len(successful)

    latencies = [
        result["latency_ms"]
        for result in successful
    ]

    print(f"Successful requests: {len(successful)}")
    print(f"Failed requests:     {failed}")

    if latencies:
        print(f"Average latency:     {sum(latencies) / len(latencies):.2f} ms")
        print(f"Max latency:         {max(latencies):.2f} ms")

    print(f"Total test time:      {total_time:.2f} seconds")

    if failed == 0:
        print()
        print("Load test: PASSED")
    else:
        print()
        print("Load test: FAILED")


if __name__ == "__main__":
    main()