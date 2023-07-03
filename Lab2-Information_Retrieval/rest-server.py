# 导入必要的库和模块
from flask import Flask, jsonify, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import re
import os
import shutil
import numpy as np
from search import recommend
from tensorflow.python.platform import gfile

# 创建 Flask 应用并配置静态 URL 路径
app = Flask(__name__, static_url_path="")
# 设置文件上传文件夹
UPLOAD_FOLDER = 'uploads'
# 设置允许的文件扩展名
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# 将应用配置的上传文件夹设置为之前定义的 UPLOAD_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 从文本文件中加载预先提取的特征向量，并将它们存储在名为 extracted_features 的 NumPy 数组中
extracted_features = np.zeros((2955, 2048), dtype=np.float32)
with open('saved_features_recom.txt') as f:
    for i, line in enumerate(f):
        extracted_features[i, :] = line.split(" ")


# 查找该特征文件中是否有对应的编号
def check_num_in_file(filename, num):
    """
    检查num是否在文件中
    Args:
        filename:string
        num: int
    """
    count = 0
    with open(filename, 'r') as f:
        for line in f:
            for word in line.split():
                if word.isdigit() and int(word) == num:
                    return True
                count += 1
                if count >= 3000:
                    return False
    return False


feature_txt = ['animals', 'baby', 'bird', 'car', 'clouds', 'dog', 'female', 'flower', 'food', 'indoor', 'lake', 'male',
               'night', 'people', 'plant_life', 'portrait', 'river', 'sea', 'sky', 'structures', 'sunset', 'transport',
               'tree', 'water']


def find_features(img_path):
    """
    根据图片路径寻找到其特征
    Args:
        img_path: 图片路径
    Returns:list 所有特征名字的列表
    """
    import os
    current_path = os.getcwd()
    feature = []
    match = re.search(r'\d+', img_path)
    if match:
        img_num = int(match.group())
    for txt in feature_txt:
        filename = current_path + '/database/tags/' + txt + '.txt'
        if check_num_in_file(filename, img_num) == True:
            feature.append(txt)
    return feature


# 定义 /imgUpload 路由，处理图像上传和搜索
@app.route('/imgUpload', methods=['GET', 'POST'])
def upload_img():
    # 设置结果文件夹，result文件夹中存放筛选出来的结果
    result = 'static/result'
    # 如果结果文件夹不存在，则创建
    if not gfile.Exists(result):
        os.mkdir(result)
    # 删除结果文件夹中的现有内容
    shutil.rmtree(result)

    # 当请求方法为 POST 或 GET 时
    if request.method == 'POST' or request.method == 'GET':
        # 检查请求中是否包含文件，没有文件则重定向到原始的url
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        # 检查文件名是否为空
        if file.filename == '':
            return redirect(request.url)

        # 如果有文件，保存到指定的上传文件夹
        if file:
            filename = secure_filename(file.filename)  # 使用secure_filename确保文件名是安全的
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # 将文件上传到指定的文件夹
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # 构造上传文件的完整路径

            # 调用 recommend 函数执行图像搜索
            recommend(input_path, extracted_features)
            # 删除上传的文件
            print(input_path)
            os.remove(input_path)

            # 从结果文件夹中读取搜索到的图像并将它们的路径存储在一个名为 images 的字典中
            image_list = [os.path.join("/result", file) for file in os.listdir(result) if not file.startswith('.')]
            images = {f'image{i}': image_list[i] for i in range(len(image_list))}
            feature_list = []
            for i in range(len(image_list)):
                feature_list.append(find_features(image_list[i]))
            features = {f'feature{i}': feature_list[i] for i in range(len(feature_list))}
            # 获取所有特征向量并去掉重复元素
            all_features = []
            for sublist in feature_list:
                for feature in sublist:
                    all_features.append(feature)
            unique_features = list(set(all_features))
            print(unique_features)
            # 注意jsonify传输参数只能是一个字典,故将两个字典合并
            para={}
            para.update(images)
            para.update(features)
            para.update({"all_features":unique_features})
            print(para)
            # 将包含搜索结果图像路径的字典作为 JSON 对象返回到前端，照片的名字为'image0':'/result\\im2144.jpg'
            return jsonify(para)


# 定义主页路由，渲染名为 main.html 的模板
@app.route("/")
def main():
    return render_template("main.html")


# 启动 Flask 应用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
