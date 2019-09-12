################################################################################
##
##  新浪微博热点事件发现与脉络生成系统
##
##      @Filename       ./DetectHotspots/HierarchicalClustering.py
##      @Author         李林峰, 刘臻, 徐润邦, 马伯乐, 朱杰, 瞿凤业
##      @Version        3.1
##      @Date           2019/09/06
##      @Copyright      Copyright (c) 2019. All rights reserved.
##      @Description    事件聚类和热度计算模块. 特征向量提取, SL层次聚类, 热度计算.
##
################################################################################
import numpy as np
import scipy.cluster.hierarchy as sch
from gensim import corpora
from gensim import models
from scipy.stats import entropy



##  模块内部接口
#   <summary> 敏感词列表生成候选事件文档 </summary>
#   <param>
#       sensitive_word_list (二维列表): 敏感词列表 [[主要词1,(语境词1,概率),(语境词2,概率),..], ...]
#       scale (int): 扩大比例系数
#   </param>
#   <return>
#       documents (二维列表): 候选事件文档 [[词语1, 词语2, ...], ...]
#   </return>
def dic2doc(sensitive_word_list, scale):
	documents = []
	for dic_list in sensitive_word_list:
		doc_list = [word[0] for word in dic_list for i in range(int(word[1] * scale))]
		documents.append(doc_list)
	return documents



##  模块内部接口
#   <summary> 文档生成特征向量(LDA主题模型) </summary>
#   <param>
#       documents (二维列表): 候选事件文档 [[词语1, 词语2, ...], ...]
#       topics_ratio (float): 主题数量参数(默认1.5), 即主题数为文档数的 topics_ratio 倍
#       passes (int): 轮数参数
#   </param>
#   <return>
#       feature_vec (二维列表): 各候选事件特征向量 [[候选事件1特征向量], [候选事件2特征向量], ...]
#   </return>
def doc2vec(documents, topics_ratio, passes):
	dictionary = corpora.Dictionary(documents)
	corpus = [dictionary.doc2bow(doc_list) for doc_list in documents]
	ldamodel = models.LdaModel(corpus=corpus, num_topics=int(len(documents) * topics_ratio), id2word=dictionary, passes=passes)

	lda_vec = np.zeros([len(documents), int(len(documents) * topics_ratio)])
	for i, doc_bow in enumerate(corpus):
		topic = [topic_pr[0] for topic_pr in ldamodel[doc_bow]]
		lda_vec[i][topic] = [topic_pr[1] for topic_pr in ldamodel[doc_bow]]
	return lda_vec



##  模块内部接口
#   <summary> 计算特征向量p和q的JS散度 </summary>
#   <param>
#       p (一维列表): 候选事件特征向量
#       q (一维列表): 候选事件特征向量
#   </param>
#   <return>
#       js_dis (float): p和q的JS散度
#   </return>
def js_divergence(p, q):
	M = (p + q) / 2
	js_dis = 0.5 * entropy(p, M) + 0.5 * entropy(q, M)
	return js_dis



##  模块内部接口
#   <summary> 计算JS散度距离矩阵 </summary>
#   <param>
#       feature_vec (二维列表): 各候选事件特征向量 [[候选事件1特征向量], [候选事件2特征向量], ...]
#   </param>
#   <return>
#       dismat (一维列表): 压缩距离矩阵 [候选事件1和2的距离, 候选事件1和3的距离, ... ,候选事件2和3的距离, ...]
#   </return>
def js_distance_mat(feature_vec):
	n = len(feature_vec)
	dismat = [js_divergence(feature_vec[i], feature_vec[j])\
				for i in range(n) for j in range(i + 1, n)]
	return dismat



##  模块对外接口
#   <summary> 层次聚类 </summary>
#   <param>
#       sensitive_word_list (三维列表): 敏感词列表 [[[窗口1主要词1,(语境词1,概率),..],...], ...]
#       scale (int): 生成文档时, 语境词出现次数扩大比例系数(默认100)
#       topics_ratio (float): 主题数量参数(默认1.5), 即主题数为文档数的 topics_ratio 倍
#       passes (int): 轮数参数(默认20)
#       threshold (float): 聚类阈值参数(默认0.3)
#   </param>
#   <return>
#       cluster (二维列表): 聚类结果 [[窗口1的文档1类编号, 窗口1的文档2类编号, ...], ...]
#       heat (二维列表): 事件热度 [[窗口1的类编号为1的事件热度, 窗口1类编号为2的事件热度,...],...]
#   </return>
def hierarchical_clustering(sensitive_word_list, scale=100, topics_ratio=1.5, passes=20, threshold=0.3):
	cluster, heat = [], []
	for word_perwindow in sensitive_word_list:
		# 1. 生成文档
		documents = dic2doc(word_perwindow, scale=scale)
		# 2. 文档主题生成及特征提取
		feature_vec = doc2vec(documents, topics_ratio=topics_ratio, passes=passes)
		# 3. 层次聚类
		#   计算距离矩阵
		dismat = js_distance_mat(feature_vec)
		#   聚类
		z = sch.linkage(dismat, method='single')
		clu = sch.fcluster(z, t=threshold, criterion='distance')
		heat.append([list(clu).count(i) for i in range(1, clu.max()+1)])
		cluster.append(clu)
	return cluster, heat


