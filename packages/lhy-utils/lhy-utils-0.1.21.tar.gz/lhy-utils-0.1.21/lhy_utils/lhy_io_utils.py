# coding: utf-8
import json
import pickle as pkl


def read_json(j_path):
    with open(j_path, "r", encoding="utf-8") as fr:
        return json.load(fr)


def read_json_line(j_path):
    with open(j_path, "r", encoding="utf-8") as fr:
        return [json.loads(i.strip()) for i in fr.readlines()]


def write_json(j_path, j_data):
    with open(j_path, "w", encoding="utf-8") as fw:
        json.dump(j_data, fw, ensure_ascii=False, indent=4)


def write_json_line(j_path, j_data):
    with open(j_path, "w", encoding="utf-8") as fw:
        for data in j_data:
            fw.write(json.dumps(data, ensure_ascii=False) + "\n")


def read_text_line(file_name):
    return [i.strip() for i in open(file_name, "r", encoding="utf-8").readlines()]


def write_text_line(file_name, data):
    with open(file_name, "w", encoding="utf-8") as fw:
        fw.write("\n".join(data))


def save_pkl(pkl_path, obj):
    with open(pkl_path, "wb") as fwb:
        pkl.dump(obj, fwb)


def load_pkl(pkl_path):
    with open(pkl_path, "rb") as frb:
        return pkl.load(frb)
