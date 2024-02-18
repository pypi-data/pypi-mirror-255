# coding: utf-8
import math
from collections import Counter

import numpy as np
from .lhy_tool_utils import l2_normalize


def cal_core_pagerank(input_array):
    from DaPy.methods import PageRank
    """
    计算新的簇心
    """
    similar_mat = np.dot(input_array, input_array.T)
    similar_mat /= similar_mat.sum(axis=0)
    pg = PageRank(engine="numpy")
    node_weight = pg.transform(similar_mat)
    scores = np.argsort(-np.array(node_weight))  # 根据pagerank的重要性求出簇心群
    candidate_length = math.ceil(len(input_array) / 10)  # 取前10%个作为簇心
    scores_ids = scores[:candidate_length]
    new_core = np.mean(input_array[scores_ids], axis=0)  # 计算簇心群的平均向量作为新簇心
    return new_core.reshape(1, -1)


def single_pass(train_array: np.ndarray, text_list=None, alpha=0.8, beta=0.9, theta=0.95, core_init=50):
    """
    1、先对簇心进行初始化
        1.1、对聚类的文本进行统计，找到重复度最大的样本，作为第一个簇心（如果没有给文本列表就使用第一个样本作为第一个簇心）
        1.2、找到所有样本中，与第一个簇心相似度最低的簇心，作为第二个簇心
        1.3、遍历剩余样本，计算每个样本与当前簇心的相似度的均值，与均值最低且不大于0.7的样本作为下一个簇心
        1.4、当簇心数量大于等于预设值，或者，在每一次遍历过程中没有发生簇心的新增，即判断簇心的初始化已完成
    2、根据相似度决定把剩余样本放入簇还是新建簇
        2.1、计算样本与现有簇的相似度，取最大值，如果大于等于alpha放入簇，且如果大于等于alpha+0.5更新簇心
        2.1、否则新增一个簇
    3、对所有的簇进行合并
        3.1、计算所有簇之间的相似度矩阵，并mask掉下三角
        3.2、将所有的相似度高->低进行排序，优先合并高相似度的，相似度小于beta的不做合并
    4、簇内排序，根据样本到簇心的相似度
    5、簇间排序，根据簇的大小
    :param train_array: 要聚类的向量集合
    :param text_list: 可给可不给，如果给了，将text重复次数最多的作为第一个簇心
    :param alpha: 样本相似度阈值
    :param beta: 簇相似度阈值
    :param theta: 需要调整簇心的相似度
    :param core_init: 初始多少个簇心
    :return cluster_result_list: ["cluster_id": int, "items": [], "core": np.ndarray(可选)]
    """
    assert len(train_array.shape) == 2
    # 初始化最终结果
    cluster_result_list = []  # 存放最终返回的结果
    # 1、对簇心进行初始化
    data_num, feature_dim = train_array.shape
    if text_list is not None:
        most_text = Counter(text_list).most_common(1)[0][0]  # 出现次数最多的text
        first_init_index = text_list.index(most_text)  # 出现次数最多的text的第一个下标
    else:
        first_init_index = 0
    core_vec = None  # 初始簇心
    visited_index = set()  # 存储已被使用过的样本
    while True:
        add_bz = False  # 是否新增簇心了
        if len(cluster_result_list) == 0:  # 如果簇心暂时为空，取出现次数最大的text
            visited_index.add(first_init_index)
            cluster_template = {"cluster_id": len(cluster_result_list), "items": [first_init_index],
                                "core": train_array[first_init_index].reshape(1, -1)}
            cluster_result_list.append(cluster_template)
            core_vec = train_array[first_init_index].reshape(1, -1)
            add_bz = True
        else:
            tmp_similar = np.dot(core_vec, train_array.T)
            similar_ave = np.mean(tmp_similar, axis=0)
            similar_sort_idx = np.argsort(similar_ave)
            for can_idx in similar_sort_idx:
                if similar_ave[can_idx] >= alpha:
                    break
                if can_idx not in visited_index and np.max(tmp_similar[:, can_idx]) < beta:
                    visited_index.add(can_idx)
                    cluster_template = {"cluster_id": len(cluster_result_list), "items": [can_idx],
                                        "core": train_array[can_idx].reshape(1, -1)}
                    cluster_result_list.append(cluster_template)
                    core_vec = np.append(core_vec, train_array[can_idx].reshape(1, -1), axis=0)
                    add_bz = True
                    break
        if (not add_bz) or len(cluster_result_list) >= core_init:  # 如果某一次循环没有新增簇心，或者簇数已达到一定数量
            break
    # 2、根据相似度决定把剩余样本放入簇还是新建簇
    for sample_index, sample_array in enumerate(train_array):
        if sample_index not in visited_index:
            cluster_similar = np.dot(sample_array, core_vec.T)  # 计算该样本与现有簇心的相似度，不能一次性计算好
            max_cluster_idx = np.argmax(cluster_similar)  # 最大相似度的簇
            max_similarity = cluster_similar[max_cluster_idx]  # 最大相似度
            if max_similarity >= alpha:  # 最大相似度大于等于阈值，则合并
                cluster_result_list[max_cluster_idx]["items"].append(sample_index)
                if max_similarity >= theta:
                    new_core = np.mean([sample_array.reshape(1, -1), core_vec[max_cluster_idx]], axis=0)
                    new_core = l2_normalize(new_core)
                    core_vec[max_cluster_idx] = new_core
                    cluster_result_list[max_cluster_idx]["core"] = new_core
            else:  # 相似度不够就新增一个簇
                cluster_template = {"cluster_id": len(cluster_result_list), "items": [sample_index],
                                    "core": sample_array.reshape(1, -1)}
                cluster_result_list.append(cluster_template)
                core_vec = np.append(core_vec, sample_array.reshape(1, -1), axis=0)
    # 3、对所有的簇进行合并， core_vec 和 cluster_result_list是一一对应的
    combine_cluster_result = []  # 重置一下合并过的簇
    combine_core = None
    while True:
        combine_bz = False  # 该次循环是否产生了合并
        if combine_cluster_result and combine_core is not None:
            cluster_result_list = combine_cluster_result
            core_vec = combine_core
            combine_cluster_result = []  # 重置一下合并过的簇
            combine_core = None
        cluster_core_similarity = np.dot(core_vec, core_vec.T)
        cluster_core_similarity = np.triu(cluster_core_similarity, k=1)  # 剔除下三角
        cluster_num = len(cluster_core_similarity)
        sim_argsort = np.argsort(-cluster_core_similarity.reshape(-1, ))
        for index in sim_argsort:
            row, col = divmod(index, cluster_num)
            if cluster_core_similarity[row][col] >= beta:
                if len(cluster_result_list[col]["items"]) > 0:
                    combine_bz = True
                    # 把列的簇中所有数据放入行的簇
                    cluster_result_list[row]["items"].extend(cluster_result_list[col]["items"])
                    cluster_result_list[row]["core"] = None
                    cluster_result_list[col]["items"] = []
            else:
                break
        for cluster in cluster_result_list:
            cluster_length = len(cluster["items"])
            if cluster_length > 0:
                cluster["cluster_id"] = len(combine_cluster_result)
                if cluster["core"] is None:
                    cluster_vector = train_array[cluster["items"]]
                    core = cal_core_pagerank(cluster_vector)
                    core = l2_normalize(core)
                else:
                    core = cluster["core"]
                combine_cluster_result.append(cluster)
                combine_core = core if combine_core is None else np.append(combine_core, core, axis=0)
        if not combine_bz:
            break
    # 簇内排序, 利用cluster_result_list和core_vec进行排序
    cluster_num = len(cluster_result_list)
    assert len(core_vec) == cluster_num
    for c_index in range(cluster_num):
        cluster = cluster_result_list[c_index]
        cluster_core = core_vec[c_index]
        cluster["core"] = cluster_core
        if len(cluster["items"]) > 1:
            cluster_in_similar = np.dot(cluster_core, train_array[cluster["items"]].T)
            sorted_index_list = np.argsort(-cluster_in_similar)
            cluster["items"] = [cluster["items"][i] for i in sorted_index_list]
    # 簇间排序
    cluster_result_list.sort(key=lambda x: len(x["items"]), reverse=True)
    for c_index, cluster in enumerate(cluster_result_list):  # 重置簇的id
        cluster["cluster_id"] = c_index
    # 验证
    return cluster_result_list
