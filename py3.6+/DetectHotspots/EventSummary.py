################################################################################
##
##  新浪微博热点事件发现与脉络生成系统
##
##      @Filename       ./DetectHotspots/EventSummary.py
##      @Author         李林峰, 刘臻, 徐润邦, 马伯乐, 朱杰, 瞿凤业
##      @Version        3.1
##      @Date           2019/09/06
##      @Copyright      Copyright (c) 2019. All rights reserved. 
##      @Description    事件摘要模块. 查找热点事件主要词与语境词, 查找热点事件原博文,
##                      生成热点事件摘要. 
##
################################################################################
import numpy as np
import re
from textrank4zh import TextRank4Sentence
import os
MYDIR = os.path.dirname(__file__)



##  模块内部接口
#   <summary> 查找热点事件主要词、语境词 </summary>
#   <param>
#       sensitive_word_list (二维列表): 敏感词列表 [[主要词1,(语境词1,概率),(语境词2,概率),..], ...]
#       cluster (二维列表): 分类结果 [热点事件1的类编号, 热点事件2的类编号, ...]
#   </param>
#   <return>
#       main_words (二维列表): 热点事件主要词集 [[热点事件1主要词1, 热点事件1主要词2, ...], ...]
#       situ_words (二维列表): 热点事件语境词集 [[热点事件1语境词1, 热点事件1语境词2, ...], ...]
#   </return>
def get_words(sensitive_word_list, cluster):
	n = cluster.max()
	main_words, situ_words = [], []
	for cluster_number in range(1, n + 1):
		indices = np.where(cluster == cluster_number)[0].tolist()
		main_words.append(list(set([sensitive_word_list[index][0][0] for index in indices])))
		situ_list = [word for index in indices for word in sensitive_word_list[index][1:]]
		situ_list.sort(key=lambda elem:elem[1], reverse=True)
		situ_list = [word[0] for word in situ_list[:20]]
		situ_words.append(list(set(situ_list)))
	return main_words, situ_words



##  模块内部接口
#   <summary> 查找热点事件原博文 </summary>
#   <param>
#       main_words (二维列表): 热点事件主要词集 [[热点事件1主要词1, 热点事件1主要词2, ...], ...]
#       situ_words (二维列表): 热点事件语境词集 [[热点事件1语境词1, 热点事件1语境词2, ...], ...]
#       blogs (二维列表): 原博文 [[窗口时间1的博文1, 窗口时间1的博文2, ...], ...]
#   </param>
#   <return>
#       cluster_blog (二维列表): 热点事件原博文集 [[热点事件1原博文1, 热点事件1原博文2, ...], ...]
#   </return>
def search_blog(main_words, situ_words, blogs):
	n = len(main_words)		# 热点事件数目
	cluster_blog = []
	for cluster_number in range(n):
		print('number=', cluster_number)
		c_blog = []
		for blog in blogs:
			flag = False
			if len(main_words[cluster_number]) > 1:
				count = 0
				for mword in main_words[cluster_number]:
					if re.search(mword, blog):
						count += 1
					if count == 2:
						c_blog.append(blog)
						flag = True
						break
			elif len(main_words[cluster_number]) == 1 or flag == False:
				find = False
				mword = main_words[cluster_number][0]
				if re.search(mword, blog):
					find = True
				if find == True:
					count = 0
					for sword in situ_words[cluster_number]:
						if re.search(sword, blog):
							count += 1
						if count == 2:
							c_blog.append(blog)
							break
		cluster_blog.append(c_blog)
	return cluster_blog



##  模块内部接口
#   <summary> 生成热点事件内容(text_rank) </summary>
#   <param>
#       cluster_blog (二维列表): 热点事件原博文集 [[热点事件1原博文1, 热点事件1原博文2, ...], ...]
#   </param>
#   <return>
#       summary (一维列表): 热点事件摘要[[热点事件1摘要], [热点事件2摘要], ...]
#   </return>
def text_rank(cluster_blog):
	summary = []
	for blog_list in cluster_blog:
		text = ""
		for blog in blog_list:
			text += blog + '\n'

		tr4s = TextRank4Sentence()
		tr4s.analyze(text=text, lower=True, source='all_filters')
		summary.append([item.sentence for item in tr4s.get_key_sentences(num=3)])
	return summary



##  模块对外接口
#   <summary> 热点事件内容生成 </summary>
#   <param>
#       sensitive_word_list (三维列表): 敏感词列表 [[[窗口1主要词1,(语境词1,概率),..],...], ...]
#       cluster (二维列表): 聚类结果 [[窗口1的文档1类编号, 窗口1的文档2类编号, ...], ...]
#       heat (二维列表): 事件热度 [[窗口1的类编号为1的事件热度, 窗口1类编号为2的事件热度,...],...]
#		hotspots_file (str): 热点事件输出文件路径 
#   </param>
#   <io>
#       file output:向 hotspots_file (str) 路径写入热点事件, 每行为 "主要词1 主要词2 ..., 语境词1 语境词2 ..., 摘要"
#   </io>
def event_summary(sensitive_word_list, cluster, heat, blogs, hotspots_file):
	hotspots, mword, sword = [], [], []
	for i,word_perwindow in enumerate(sensitive_word_list):
		# 1. 生成热点事件主要词、语境词
		#	main_words (二维列表): 热点事件主要词集 [[热点事件1主要词1, 热点事件1主要词2, ...], ...]
		#	situ_words (二维列表): 热点事件语境词集 [[热点事件1语境词1, 热点事件1语境词2, ...], ...]
		main_words, situ_words = get_words(word_perwindow, cluster[i])
		mword.append(main_words)
		sword.append(situ_words)
		# 2. 查找热点事件微博
		#   cluster_blog (二维列表): 热点事件原博文集 [[热点事件1原博文1, 热点事件1原博文2, ...], ...]
		cluster_blog = search_blog(main_words, situ_words, blogs[i])
		# 3. 生成热点事件内容(text_rank摘要算法)
		# hotspots (三维列表), 每一维是一个窗口内热点事件的摘要 [[热点事件1摘要], [热点事件2摘要], ...]
		hotspots.append(text_rank(cluster_blog))
	with open(os.path.join(MYDIR,hotspots_file), 'w', encoding='utf-8') as f:
		for i in range(len(hotspots)):
			for j in range(len(mword[i])):
				anEvent = " ".join(mword[i][j]) + "," + " ".join(sword[i][j]) + "," + \
					"。".join(hotspots[i][j]) + "。" + "," + str(heat[i][j]) + "\n"
				f.write(anEvent)
	f.close()


