import multiprocessing

TOTAL = 1000000
NUM_PROCESSES = 5

def calculate_partial_sum(start, end):
    return sum(range(start, end + 1))

def main():
    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        start_end_ranges = [(i * (TOTAL // NUM_PROCESSES) + 1, (i + 1) * (TOTAL // NUM_PROCESSES)) for i in range(NUM_PROCESSES)]
        results = pool.starmap(calculate_partial_sum, start_end_ranges)
        total_sum = sum(results)
        print("Total sum using multiprocessing:", total_sum)

if __name__ == "__main__":
    import time
    start_time = time.time()
    main()
    print("Execution time:", time.time() - start_time)
