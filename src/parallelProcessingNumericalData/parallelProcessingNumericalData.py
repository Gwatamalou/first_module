import json
from concurrent.futures import ThreadPoolExecutor
from math import factorial
from multiprocessing import Pool, Process, Queue, cpu_count
from random import randint
from threading import Thread
from time import time

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")


def timer(func):
    def inner(*args, **kwargs):
        start = time()
        func(*args, **kwargs)
        end = time()
        return end - start

    return inner


def generate_data(n: int) -> list[int]:
    return [randint(0, 1001) for i in range(n)]


def process_number(number):
    return factorial(number)


@timer
def mono_thread(data):
    return list(map(process_number, data))


@timer
def thread_pool(data):
    with ThreadPoolExecutor() as executor:
        return list(executor.map(process_number, data))


@timer
def process_pool(data):
    with Pool(cpu_count()) as pool:
        return list(pool.map(process_number, data))


def worker_queue(in_queue, out_queue):
    while True:
        n = in_queue.get()
        if n is None:
            break
        out_queue.put(process_number(n))


def out_consumer(out_queue, len_data, result):
    for _ in range(len_data):
        result.append(out_queue.get())

    return result


@timer
def process_queue(data):
    in_queue = Queue()
    out_queue = Queue()
    result = []

    for num in data:
        in_queue.put(num)

    for _ in range(cpu_count()):
        in_queue.put(None)

    processes = [
        Process(target=worker_queue, args=(in_queue, out_queue))
        for _ in range(cpu_count())
    ]
    consumer = Thread(target=out_consumer, args=(out_queue, len(data), result))

    for p in processes:
        p.start()

    consumer.start()

    for p in processes:
        p.join()

    consumer.join()

    return result


def main():
    data = generate_data(100000)

    result = {
        "mono_thread": mono_thread(data),
        "thread_pool": thread_pool(data),
        "process_pool": process_pool(data),
        "process_queue": process_queue(data),
    }

    with open("result.json", "w") as file:
        json.dump(result, file, indent=4)

    plt.bar([x for x in result.keys()], [y for y in result.values()])
    plt.show()


if __name__ == "__main__":
    main()
