################################################################################
##
##  新浪微博热点事件发现与脉络生成系统
##
##      @Filename       ./HotspotsAnalysis/CorrelationAnalysis.py
##      @Author         李林峰, 刘臻, 徐润邦, 马伯乐, 朱杰, 瞿凤业
##      @Version        3.1
##      @Date           2019/09/06
##      @Copyright      Copyright (c) 2019. All rights reserved.
##      @Description    本文件实现热点事件相关性分析模块
##
################################################################################
import numpy as np
import os
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
MYDIR = os.path.dirname(__file__)



##  模块内部接口
#   <summary> 计算两个向量之间的余弦相似度 </summary>
#   <param>
#       vector_a (一维列表): [num1, num2, ...]
#       vector_a (一维列表): [num1, num2, ...]
#   </param>
#   <return>
#       sim (float): 相关性系数
#   </return>
def cos_sim(vector_a, vector_b):
    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    if denom == 0:
        sim = 0.0
    else:
        cos = num / denom
        sim = 0.5*cos + 0.5
    return sim



##  模块对外接口
#   <summary> 生成相关性矩阵 </summary>
#   <param>
#       input_file_path (str) 热点事件的文件路径
#       output_filepath (str) 输出关联性矩阵的文件路径
#   </param>
#   <io>
#       file input: 从 input_file_path (str) 路径读入热点事件
#       file output:向 output_filepath (str) 路径写入事件关联性矩阵 "num11 num12 ...\n num21 num22 ...\n ..."
#   </io>
def generate_correlation_matrics(input_file_path, output_file_path):

    blogs = []
    with open(os.path.join(MYDIR,input_file_path), 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            content = line.split(',')[2]
            blogs.append(content)

    # print(blogs)
    # 构建TF-IDF向量
    vectorizer = CountVectorizer()
    count = vectorizer.fit_transform(blogs)
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(count)
    weight = tfidf.toarray()

    # 计算相关性系数，存入矩阵
    correlation_matrics = []
    n = len(blogs)
    for i in range(n):
        tmp = []
        for j in range(n):
            cos_between_two_matric = cos_sim(weight[i], weight[j])
            tmp.append(cos_between_two_matric)
        correlation_matrics.append(tmp)

    with open(os.path.join(MYDIR,output_file_path), 'w', encoding='utf-8') as f:
        for i in correlation_matrics:
            content = " ".join('%s' % num for num in i)
            f.write(content+'\n')
    f.close()


