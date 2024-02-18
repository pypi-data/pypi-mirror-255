# coding: utf-8
import os
import math
import subprocess
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import copy

import numpy as np


def read_dir_size(directory):
    size = 0
    if os.path.isdir(directory):
        for root, dirs, files in os.walk(directory):
            for name in files:
                try:
                    size += os.path.getsize(os.path.join(root, name))
                except Exception as e:
                    pass
    elif os.path.isfile(directory):
        size = os.path.getsize(directory)
    return size


def get_size_of_directory(directory):
    all_size = []
    for dirname in os.listdir(directory):
        path = os.path.join(directory, dirname)
        size = 0
        if os.path.isdir(path):
            size = read_dir_size(path)
        elif os.path.isdir(path):
            size = os.path.getsize(path)
        size /= (1024 * 1024)
        size = int(size)
        if size <= 100:
            continue
        all_size.append((size, dirname))
    all_size.sort(key=lambda x: -x[0])
    for size, dir in all_size:
        print(f"{size}MB  {dir}")


def read_gpu(return_least=False):
    import pynvml
    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()
    gpu_list = []
    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        name = pynvml.nvmlDeviceGetName(handle).decode()
        total = round(meminfo.total / 1024 ** 3, 2)
        used = round(meminfo.used / 1024 ** 3, 2)
        free = round(meminfo.free / 1024 ** 3, 2)
        information = {
            "id": i,
            "name": name,
            "total": total,
            "used": used,
            "free": free
        }
        gpu_list.append(information)
    if return_least:
        sort_gpu_list = copy.copy(gpu_list)
        sort_gpu_list.sort(key=lambda x: (x["used"], -x["id"]))
        least_id = sort_gpu_list[0]["id"]
        return gpu_list, least_id
    else:
        return gpu_list


def cut_list(target, batch_size):
    return [target[i:i + batch_size] for i in range(0, len(target), batch_size)]


def dict_set_value(input_data, args):
    assert len(args) == len(input_data.keys())
    for i, k in enumerate(input_data.keys()):
        input_data[k].append(args[i])


def l2_normalize(vecs):
    """l2标准化
    :param vecs: np.ndarray
    """
    norms = (vecs ** 2).sum(axis=1, keepdims=True) ** 0.5
    return vecs / np.clip(norms, 1e-8, np.inf)


def data_count(text_list, level="char"):
    """
    统计一个list的文本的长度
    """
    assert level in ["char", "word", "c", "w"]
    count_list = []
    for text in text_list:
        token_num = len(text.split()) if level[0] == "w" else len(text)
        count_list.append(token_num)
    counter = Counter(count_list)
    high_freq = counter.most_common(1)[0]
    result = {
        "min_length": min(count_list),
        "max_length": max(count_list),
        "ave_length": int(sum(count_list) / len(count_list)),
        "high_freq_length": high_freq[0],
        "high_freq_numbers": high_freq[1],
        "counter": counter
    }
    return result


def exec_shell(cmd):
    """打印并执行命令内容，并支持写入日志文件中
    Args:
        cmd: 执行命令的内容（str）
    Returns:
        status: 执行状态
    """
    print(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
    while p.poll() is None:
        line = p.stdout.readline().strip().decode()
        if line:
            print(line)
    status = p.returncode
    if status != 0:
        print(f'exec cmd failed. {cmd}')
    return status


class MultiProcessBase:
    """
    class MT(MultiProcessBase):
        @staticmethod
        def task(inputs):
            return [i ** 8 for i in inputs]
    m=MT().run()
    """

    def __init__(self, data, work_nums=4, batch_size=None, pool_type="t"):
        if batch_size:
            batch_size = batch_size
        else:
            batch_size = math.ceil(len(data) / work_nums)
        self.input_list = cut_list(data, batch_size)  # 每个进程的数据
        if pool_type == "t":
            self.pool = ThreadPoolExecutor(work_nums)
        else:
            self.pool = ProcessPoolExecutor(work_nums)

    @staticmethod
    def task(inputs):
        raise NotImplemented

    def run(self):
        obj_list = []
        for p_id in range(len(self.input_list)):
            r = self.pool.submit(self.task, self.input_list[p_id])
            obj_list.append(r)
        self.pool.shutdown()
        result_list = []
        for obj in obj_list:
            result_list.extend(obj.result())
        return result_list


class MultiThreadBar:
    """
    for i in MultiThreadBar(data, "te"):
        pass
    """

    def __init__(self, iter_data, desc=None):
        if not hasattr(iter_data, "__iter__"):
            raise ValueError("data必须是迭代器")
        self.data = iter_data
        self.length = len(iter_data)
        self.index = 0
        self.start_time = time.time()
        self.cost_time = 0
        self.time_step = 0
        self.last_time = 0
        self.msg = "\r"
        if desc:
            self.msg = self.msg + desc + ": "

    def update_time_step(self):
        self.cost_time = time.time() - self.start_time
        self.time_step = self.cost_time / self.index
        self.last_time = self.time_step * (self.length - self.index)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index != 0:
            self.update_time_step()
            print(f"{self.msg}{self.index} / {self.length - 1}, time: {int(self.cost_time)}s / {int(self.last_time)}s",
                  end="")
        else:
            print(f"{self.msg}{self.index} / {self.length - 1}", end="")
        if self.index == self.length:
            print(f"{self.msg}{self.index - 1} / {self.length - 1}, cost: {int(self.cost_time)}")
            raise StopIteration
        value = self.data[self.index]
        self.index += 1
        return value


def write_excel(path: str,
                write_data_list: list,
                sheet_name_list: list = None,
                format_title: dict = None,
                format_content: dict = None,
                row_height: list = None,
                col_width: list = None):
    """

    :param path: 文件路径
    :param write_data_list: 文件内容, 几张表就几个data，data里面的结构是{"表头": [内容1,内容2,...]}
    :param sheet_name_list:
    :param format_title:
    :param format_content:
    :param row_height:
    :param col_width:
    :return:
    """
    import xlsxwriter
    # 构建A-Z到0-25的映射
    char2num = {chr(i): i - ord("A") for i in range(ord("A"), ord("Z") + 1)}
    char2num.update({chr(i): i - ord("a") for i in range(ord("a"), ord("z") + 1)})
    # 构建format
    format_t = {"bold": True, "align": "center", "valign": "vcenter", "text_wrap": True}
    format_c = {"align": "center", "valign": "vcenter", "text_wrap": True}
    if format_title is not None:
        format_t.update(format_title)
    if format_content is not None:
        format_c.update(format_content)
    # 构建sheet_name
    sheet_num = len(write_data_list)
    if sheet_name_list is None:
        sheet_name_list = [f"sheet{i}" for i in range(sheet_num)]
    assert sheet_num == len(sheet_name_list)
    # 构建数据
    workbook = xlsxwriter.Workbook(path)
    format_t = workbook.add_format(format_t)
    format_c = workbook.add_format(format_c)
    for data, sheet_name in zip(write_data_list, sheet_name_list):
        worksheet = workbook.add_worksheet(sheet_name)
        # 写行高，如果有
        if row_height is not None:
            for row, height in row_height:
                worksheet.set_row(row, height)
        # 写列宽，如果有
        if col_width is not None:
            for col, width in col_width:
                col = char2num.get(col, col)
                worksheet.set_column(col, col, width)
        title_list = list(data.keys())
        for title_index, title in enumerate(title_list):
            worksheet.write(0, title_index, title, format_t)
            for item_index, item in enumerate(data[title]):
                worksheet.write(item_index + 1, title_index, item, format_c)
    workbook.close()


class ApiTestBase:
    def __init__(self, url=None, port=None, wait_time=300, batch_size=1, work_num=1,
                 request_type="g", cpu_num=None, logger=None):
        self.url = url
        self.port = port
        self.wait_time = wait_time  # 压测时间
        self.batch_size = batch_size
        self.work_num = work_num  # 并发请求数
        self.request_type = request_type  # 请求类型，g(grpc)或者h(http)
        self.cpu_num = cpu_num  # 服务端是否限制了核数，用于统计qps/c
        self.print = print if logger is None else logger.info
        self.pool = ThreadPoolExecutor(self.work_num)  # 压测线程池
        self.success_list = list()  # 成功次数
        self.failure_list = list()  # 失败次数

    def init_client(self):
        """
        初始化请求客户端
        :return:
        """
        raise NotImplemented

    def task(self):
        raise NotImplemented

    def main(self):
        self.print("task start")
        task_list = []
        for _ in range(self.work_num):
            t = self.pool.submit(self.task)
            task_list.append(t)
        self.pool.shutdown()
        for t in task_list:
            success_times, failure_times = t.result()
            self.success_list.append(success_times)
            self.failure_list.append(failure_times)
        self.report()

    def report(self):
        """
        获得统计结果
        :return:
        """
        total_success_times = sum(self.success_list)
        total_failure_times = sum(self.failure_list)
        failure_rate = round(total_failure_times / (total_success_times + total_failure_times), 3)
        qps = round(total_success_times / self.wait_time, 2)
        self.print(f"qps: {qps}")
        self.print(f"failure rate: {failure_rate}")
        if self.cpu_num is not None:
            qps_c = round(qps / self.cpu_num, 2)
            self.print(f"qps/c: {qps_c}")
