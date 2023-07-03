################################################################################################################################
# This function implements the image search/retrieval .
# inputs: Input location of uploaded image, extracted vectors
#
################################################################################################################################
import random
import tensorflow.compat.v1 as tf
import numpy as np
import imageio
import os
import scipy.io
import time
from datetime import datetime
from scipy import ndimage

# from scipy.misc import imsave
imsave = imageio.imsave
imread = imageio.imread
from scipy.spatial.distance import cosine
# import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import pickle
from PIL import Image
import gc
import os
from tempfile import TemporaryFile
from tensorflow.python.platform import gfile

BOTTLENECK_TENSOR_NAME = 'pool_3/_reshape:0'
BOTTLENECK_TENSOR_SIZE = 2048
MODEL_INPUT_WIDTH = 299
MODEL_INPUT_HEIGHT = 299
MODEL_INPUT_DEPTH = 3
JPEG_DATA_TENSOR_NAME = 'DecodeJpeg/contents:0'
RESIZED_INPUT_TENSOR_NAME = 'ResizeBilinear:0'
MAX_NUM_IMAGES_PER_CLASS = 2 ** 27 - 1  # ~134M


# show_neighbors(random.randint(0, len(extracted_features)), indices, neighbor_list)

def get_top_k_similar(image_data, pred, pred_final, k):
    """
    用于找到与给定图像最相似的 k 个图像，并存放在result文件夹下
    Args:
        image_data: 输入图像的特征向量
        pred:预先计算的特征向量，通常存储在一个 NumPy 数组中
        pred_final:与 pred 对应的图像文件路径列表
        k:查找的最相似图像的数量
    """
    os.mkdir('static/result')

    # cosine calculates the cosine distance, not similiarity. Hence no need to reverse list
    top_k_ind = np.argsort([cosine(image_data, pred_row) for ith_row, pred_row in enumerate(pred)])[:k]
    print(top_k_ind)

    for i, neighbor in enumerate(top_k_ind):
        image = imread(pred_final[neighbor])
        # timestr = datetime.now().strftime("%Y%m%d%H%M%S")
        # name= timestr+"."+str(i)
        name = pred_final[neighbor]
        tokens = name.split("\\")
        img_name = tokens[-1]
        name = 'static/result/' + img_name
        imsave(name, image)


def create_inception_graph():
    """
    创建 Inception 模型的计算图并返回相关张量
    Returns:
        graph: Inception 模型的计算图
        bottleneck_tensor: Inception 模型的瓶颈层输出张量
        jpeg_data_tensor: 解码 JPEG 数据的张量
        resized_input_tensor: 缩放后的输入图像张量
    """
    with tf.Session() as sess:
        model_filename = os.path.join(
            'imagenet', 'classify_image_graph_def.pb')
        with gfile.FastGFile(model_filename, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            bottleneck_tensor, jpeg_data_tensor, resized_input_tensor = (
                tf.import_graph_def(graph_def, name='', return_elements=[
                    BOTTLENECK_TENSOR_NAME, JPEG_DATA_TENSOR_NAME,
                    RESIZED_INPUT_TENSOR_NAME]))
    return sess.graph, bottleneck_tensor, jpeg_data_tensor, resized_input_tensor


def run_bottleneck_on_image(sess, image_data, image_data_tensor, bottleneck_tensor):
    """
    计算输入图像的特征向量
    Args:
        sess: 一个 TensorFlow 会话对象
        image_data:输入图像的原始数据，通常是 JPEG 格式
        image_data_tensor:一个 TensorFlow 张量，表示输入图像的解码 JPEG 数据
        bottleneck_tensor:一个 TensorFlow 张量，表示 Inception 模型的瓶颈层输出
    """
    bottleneck_values = sess.run(
        bottleneck_tensor,
        {image_data_tensor: image_data})
    bottleneck_values = np.squeeze(bottleneck_values)
    return bottleneck_values


def recommend(input_path, extracted_features):
    """
      对输入图像进行推荐
      Args:
          input_path: 输入图像的文件路径
          extracted_features: 预先计算的特征向量，通常存储在一个 NumPy 数组中
    """
    # 重置默认的 TensorFlow 计算图
    tf.reset_default_graph()

    # 创建一个新的 TensorFlow 会话，禁用 GPU 加速
    config = tf.ConfigProto(device_count={'GPU': 0})
    sess = tf.Session(config=config)

    # 创建 Inception 计算图，并获取一些有用的张量
    graph, bottleneck_tensor, jpeg_data_tensor, resized_image_tensor = (create_inception_graph())
    # 读取上传的图像文件
    image_data = gfile.FastGFile(input_path, 'rb').read()
    # 提取上传图像的特征向量
    features = run_bottleneck_on_image(sess, image_data, jpeg_data_tensor, bottleneck_tensor)
    # 加载预先计算的相邻图像列表
    with open('neighbor_list_recom.pickle', 'rb') as f:
        neighbor_list = pickle.load(f)
    print("loaded images")
    # 查找与上传图像最相似的前 k 个图像
    get_top_k_similar(features, extracted_features, neighbor_list, k=9)
