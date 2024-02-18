from lhy_tool_utils import ApiTestBase
import tritonclient.grpc as grpcclient
from lhy_utils import MyLogger
import numpy as np
import time

logger = MyLogger().get_logger()


def common_grpc_client(triton_client, model_name, input_config_list, output_name_list, input_data):
    """
    所有gRPC接口的公有方法
    triton_client: triton的客户端，需初始化完成
    model_name: 调用哪个模型
    input_config_list: list,包含了输入的name,shape,type
    例: [['seq_wordids_bert', [2, 16], "INT32"],['seq_lengths', [2, 1], "INT32"]]
    output_name_list: list,包含了输出的name
    例: ["predict_probs"]
    input_data: list,包含了每个输入对应的具体数值，每个数值的形状要和input_config中的形状一致
    例: [np.ndarray1, np.ndarray2]
    logger: 日志
    返回值: this_func_result(list),length == batch
    """
    this_func_result = []  # 放置该函数的结果
    inputs = []
    outputs = []
    if len(input_config_list) != len(input_data):
        logger.error("输入配置与数据的数量不等")
        return
    # 初始化输入配置
    for input_config in input_config_list:
        if len(input_config) != 3:
            logger.error("输入配置项错误")
            return
        input_name, input_shape, input_type = input_config
        if not (isinstance(input_name, str) and isinstance(input_shape, list) and isinstance(input_type, str)):
            logger.error("输入配置项格式错误")
            return
        inputs.append(grpcclient.InferInput(input_name, input_shape, input_type))
    # 初始化输出配置
    for output_name in output_name_list:
        outputs.append(grpcclient.InferRequestedOutput(output_name))
    # 填充输入的数据
    for input_idx in range(len(inputs)):
        inputs[input_idx].set_data_from_numpy(input_data[input_idx])
    infer_result = triton_client.infer(model_name=model_name,
                                       inputs=inputs,
                                       outputs=outputs)
    for output in output_name_list:
        output_data = infer_result.as_numpy(output)
        this_func_result.append(output_data)
    return this_func_result


class ApiTest(ApiTestBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_input = [101, 200, 300, 400, 200, 300, 400, 200, 300, 400,
                           200, 300, 400, 200, 300, 400, 200, 300, 400, 200,
                           400, 200, 300, 400, 200, 300, 400, 200, 300, 400,
                           102, 101, 200, 300, 102]

    def init_client(self):
        return grpcclient.InferenceServerClient(url=f"{self.url}:{self.port}")

    def task(self):
        clint = self.init_client()
        seqs_total = []
        seq_lens_total = []
        for _ in range(self.batch_size):
            seqs_total.append(self.base_input)
            seq_lens_total.append([len(self.base_input)])
        batch_data = np.array(seqs_total, dtype=np.int32)
        batch_length = np.array(seq_lens_total, dtype=np.int32)
        input_config_list = [["seq_wordids_bert", list(batch_data.shape), "INT32"],
                             ["seq_lengths", list(batch_length.shape), "INT32"]]
        output_name_list = ["predict_probs"]
        input_data = [batch_data, batch_length]
        start = time.time()
        success_time = 0
        failure_time = 0
        while time.time() - start < self.wait_time:
            scores = common_grpc_client(clint, "text_cls_1", input_config_list, output_name_list, input_data)[0]
            if scores.shape[0] == self.batch_size:
                success_time += 1
            else:
                failure_time += 1
        return success_time, failure_time


api_test = ApiTest(url="172.16.100.7", port=8175, wait_time=10)
api_test.main()