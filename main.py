# !/usr/bin/python3
# -*- coding: utf-8 -*-
import cProfile
import json
import pstats
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor

import gjson
import jmespath
import jsonpath
from jsonpath_ng import parse


def read_from_file(filename: str) -> dict:
    """
    从JSON文件中读取数据。
    :param filename: JSON文件的名称
    :return: 读取的字典
    """
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def test_jsonpath(data: dict, path: str):
    return jsonpath.jsonpath(data, path)


def test_gjson(data: dict, path: str):
    gjson.get(data, path)


def test_jsonpath_ng(data: dict, path: str):
    jsonpath_expr = parse(path)
    jsonpath_expr.find(data)


def test_jmespath(data: dict, path: str):
    jmespath.search(path, data)


def run_and_measure_memory(func, data: dict, path: str, num_tasks: int):
    tracemalloc.start()
    start_time = time.perf_counter()

    with ThreadPoolExecutor() as executor:
        list(executor.map(lambda x: func(data, path), range(num_tasks)))

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    print(f"{func.__name__} 总耗时: {end_time - start_time:.6f} 秒")
    print(f"{func.__name__} 使用了 {current / 10 ** 6} MB 内存，峰值为 {peak / 10 ** 6} MB\n")


def test_memory(data, num_tasks):
    run_and_measure_memory(test_jsonpath, data, "10.errors.113.description", num_tasks)
    run_and_measure_memory(test_gjson, data, "10.errors.113.description", num_tasks)
    run_and_measure_memory(
        test_jsonpath_ng, data, "[10].errors.[113].description", num_tasks
    )
    run_and_measure_memory(
        test_jmespath, data, "[10].errors[113].description", num_tasks
    )


def func_calls_profile(func, data, path):
    # 创建一个Profile对象
    profiler = cProfile.Profile()

    # 使用runctx函数运行你的代码，并捕获性能数据
    # 第一个参数是要运行的代码，第二个和第三个参数分别是全局和局部变量
    profiler.runctx("func(data, path)", globals(), locals())

    # 创建一个Stats对象，并将Profile对象的数据传递给它
    stats = pstats.Stats(profiler)

    # 使用sort_stats方法对数据进行排序，按照'ncalls'（调用次数）进行排序
    stats.sort_stats("ncalls")

    # 打印排序后的统计数据
    stats.print_stats()


def test_func_calls_profile(data):
    # data = read_from_file("big.json")
    print("*" * 20 + f' test_jsonpath func_calls_profile start {"*" * 20}\n')
    func_calls_profile(test_jsonpath, data, "10.errors.113.description")
    print("*" * 20 + f' test_jsonpath func_calls_profile end {"*" * 20}\n')

    print("*" * 20 + f' test_gjson func_calls_profile start {"*" * 20}\n')
    func_calls_profile(test_gjson, data, "10.errors.113.description")
    print("*" * 20 + f' test_gjson func_calls_profile end {"*" * 20}\n')

    print("*" * 20 + f' test_jsonpath_ng func_calls_profile start {"*" * 20}\n')
    func_calls_profile(test_jsonpath_ng, data, "[10].errors.[113].description")
    print("*" * 20 + f' test_jsonpath_ng func_calls_profile end {"*" * 20}\n')

    print("*" * 20 + f' test_jmespath func_calls_profile start {"*" * 20}\n')
    func_calls_profile(test_jmespath, data, "[10].errors[113].description")
    print("*" * 20 + f' test_jmespath func_calls_profile end {"*" * 20}\n')


def run1(data, num_tasks=1):
    print(f"run{num_tasks=} start\n")
    test_memory(data, num_tasks)
    print(f"run{num_tasks=} end\n")


def run1000(data, num_tasks=1000):
    print(f"run{num_tasks=} start\n")
    test_memory(data, num_tasks)
    print(f"run{num_tasks=} end\n")


if __name__ == "__main__":
    data = read_from_file("big.json")

    run1(data)
    run1000(data)
    test_func_calls_profile(data)
