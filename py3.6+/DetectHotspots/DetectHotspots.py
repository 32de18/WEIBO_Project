################################################################################
##
##  新浪微博热点事件发现与脉络生成系统
##
##      @Filename       ./DetectHotspots/DetectHotspots.py
##      @Author         李林峰, 刘臻, 徐润邦, 马伯乐, 朱杰, 瞿凤业
##      @Version        3.1
##      @Date           2019/09/06
##      @Copyright      Copyright (c) 2019. All rights reserved.
##      @Description    本文件是热点事件生成功能的3个模块(敏感词发现、层次聚类与热度
##                      计算、事件总结)的集成主控程序
##
################################################################################
from GenSensitiveWord import gen_sensitive_word
from HierarchicalClustering import hierarchical_clustering
from EventSummary import event_summary



##  功能集成主控接口
#   <summary> 热点事件生成功能 </summary>
#   <param>
#       history_blogdata (二维列表): 历史微博数据 (每一维是一个窗口时间内已处理的全部微博) [['微博1','微博2',...],...]
#       current_blogdata (二维列表): 当前时间段微博数据 (每一维是一个窗口时间内已处理的全部微博) [['微博1','微博2',...],...]
#       oringe_blogdara (二维列表): 当前时间段原始微博数据 (每一维是一个窗口时间内的未分词的原始微博) [['微博1','微博2',...],...]
#       hotspots_file (str): 热点事件输出文件路径 
#   </param>
#   <io>
#       file output:向 hotspots_file (str) 路径写入热点事件, 每行为 "主要词1 主要词2 ...,语境词1 语境词2 ...,摘要,热度"
#   </io>
def detect_hotspots(history_blogdata, current_blogdata, oringe_blogdata, hotspots_file):
    # 1. 生成敏感词列表 sensitive_word_list (三维列表): 敏感词列表 [[[窗口1主要词1,(语境词1,概率),..],...], ...]
    sensitive_word_list = gen_sensitive_word(history_blogdata, current_blogdata)

    # 2. 生成聚类结果
    #   cluster (二维列表): 聚类结果 [[窗口1的文档1类编号, 窗口1的文档2类编号, ...], ...]
    #   heat (二维列表): 事件热度 [[窗口1的类编号为1的事件热度, 窗口1类编号为2的事件热度,...],...]
    cluster, heat = hierarchical_clustering(sensitive_word_list)

    # 3. 生成热点事件内容集 
    #   向 hotspots_file (str) 路径输出热点事件
    event_summary(sensitive_word_list, cluster, heat, oringe_blogdata, hotspots_file)


