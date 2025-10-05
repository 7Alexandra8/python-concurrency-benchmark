import threading

TOTAL = 1000000
NUM_THREADS = 5

def calculate_partial_sum(start, end):
    return sum(range(start, end + 1))

def main():
    partial_sums = []
    lock = threading.Lock()

    def worker(start, end):
        partial_sum = calculate_partial_sum(start, end)
        with lock:
            partial_sums.append(partial_sum)

    threads = []
    for i in range(NUM_THREADS):
        start = i * (TOTAL // NUM_THREADS) + 1
        end = (i + 1) * (TOTAL // NUM_THREADS)
        thread = threading.Thread(target=worker, args=(start, end))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    total_sum = sum(partial_sums)
    print("Total sum using threading:", total_sum)

if __name__ == "__main__":
    import time

    start_time = time.time()
    main()
    print("Execution time:", time.time() - start_time)
