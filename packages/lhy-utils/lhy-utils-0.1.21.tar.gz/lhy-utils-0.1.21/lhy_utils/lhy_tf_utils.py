# coding: utf-8
try:
    import os
    import tensorflow as tf
    from tensorflow.python.saved_model import signature_constants
    from tensorflow.python.saved_model import tag_constants
    from tensorflow.python.framework import convert_to_constants
    from tensorflow.python.framework import tensor_shape
    from tensorflow.python.saved_model import save
except:
    pass


def get_name(tensor_name):
    """
    去掉模型名字中的:0
    :param tensor_name:
    :return:
    """
    return "".join(tensor_name.split(":")[:-1])


def read_pb_model(pb_path):
    """
    读Pb模型
    :param pb_path:
    :return:
    """
    with tf.gfile.GFile(pb_path, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        return graph_def


def covert_pb_saved_model(graph_def, export_dir, input_list, output_list):
    """
    提供pb转写saved_model格式
    :param graph_def:
    :param export_dir:
    :param input_list:
    :param output_list:
    :return:
    """
    # 如果输入是空的，解析node提示可能的输入输出
    if (not input_list) and (not output_list):
        guess_input, guess_output = [], []
        for node_index, node in enumerate(list(graph_def.node)):
            if node.op.lower() == "placeholder":
                guess_input.append(node.name)
                continue
            if node_index >= len(graph_def.node) - 5:
                guess_output.append(node.name)
        print(f"guess input: {guess_input}")
        print(f"guess output: {guess_output}")
        input_str = input("输入：（多个以空格分开，需要带上:0）")
        input_list = input_str.split()
        print(f"input_list: {input_list}")
        output_str = input("输出：（多个以空格分开，需要带上:0）")
        output_list = output_str.split()
        print(f"output_list: {output_list}")
    builder = tf.saved_model.builder.SavedModelBuilder(export_dir)
    sigs = {}
    input_dict, output_dict = {}, {}
    with tf.Session(graph=tf.Graph()) as sess:
        tf.import_graph_def(graph_def, name="")
        g = tf.get_default_graph()
        for input_name in input_list:
            input_dict[get_name(input_name)] = g.get_tensor_by_name(input_name)
        for output_name in output_list:
            output_dict[get_name(output_name)] = g.get_tensor_by_name(output_name)
        sigs[signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY] = \
            tf.saved_model.signature_def_utils.predict_signature_def(
                input_dict, output_dict)
        builder.add_meta_graph_and_variables(sess,
                                             [tag_constants.SERVING],
                                             signature_def_map=sigs)
        builder.save()


def covert_pb_to_server_model(pb_path, export_dir, input_list=None, output_list=None):
    """
    转换pb到saved_model
    :param pb_path:
    :param export_dir:
    :param input_list: 模型的输入
    :param output_list: 模型的输出
    :return:
    """
    if os.path.exists(export_dir):
        print("export_dir is already exists, please remove")
        return
    graph_def = read_pb_model(pb_path)
    covert_pb_saved_model(graph_def, export_dir, input_list, output_list)


if __name__ == '__main__':
    dirname = "/Users/lhy/Desktop/pmu_test/202204145"
    pb_model_path = os.path.join(dirname, "model.pb")
    saved_model_path = os.path.join(dirname, "model.savedmodel")
    covert_pb_to_server_model(pb_model_path,
                              saved_model_path,
                              [],
                              [])
