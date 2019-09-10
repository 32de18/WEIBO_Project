################################################################################
##
##  新浪微博热点事件发现与脉络生成系统
##
##      @Filename       ./DataProcess/DataProcess.py
##      @Author         李林峰, 刘臻, 徐润邦, 马伯乐, 朱杰, 瞿凤业
##      @Version        3.1
##      @Date           2019/09/06
##      @Copyright      Copyright (c) 2019. All rights reserved.
##      @Description    本文件实现数据处理模块对外接口
##
################################################################################
import RemoveAd
import Segment
import cutAndTransform
import os
MYDIR = os.path.dirname(__file__)



filtered_blog_file = "../data/filtered_blog.ffss"                       # 过滤后的微博数据文件
history_blog_file = "../data/history_blog.ffss"                         # 历史时间微博
current_blog_file = "../data/current_blog.ffss"                         # 当前时间微博
segment_history_blog_file = "../data/segment_history_blog_file.ffss"    # 历史时间分词后的微博
segment_current_blog_file = "../data/segment_current_blog_file.ffss"    # 当前时间分词后的微博



##  模块对外接口
#   <summary> 数据处理模块集成控制 </summary>
#   <param>
#       original_filepath (str): 加载的全部微博原始数据文件路径
#       start_time (str) 为当前查询时间段开始时间, 格式为: YYYYMMDD
#       end_time (str) 为当前查询时间段结束时间, 格式为YYYYMMDD
#   </param>
#   <return>
#       history_blogdata (二维列表): 历史微博数据 (每一维是一个窗口时间内已处理的全部微博) [['微博1','微博2',...],...]
#       current_blogdata (二维列表): 当前时间段微博数据 (每一维是一个窗口时间内已处理的全部微博) [['微博1','微博2',...],...]
#       oringe_blogdara (二维列表): 当前时间段原始微博数据 (每一维是一个窗口时间内未分词处理的原始微博) [['微博1','微博2',...],...]
#   </return>
def data_process(original_filepath, start_time, end_time):
    # 1. 过滤广告
    #   original_filepath (str) 为加载的全部微博数据文件路径 
    #   filtered_blog_file (str) 为过滤后的微博数据文件路径 
    RemoveAd.remove_advertising(original_filepath, filtered_blog_file)
    print("过滤广告完毕")

    # 2. 将过滤后的文件分割为2个文件: 历史数据文件, 当前查询时间段的数据文件
    #   filtered_blog_file (str) 为过滤后的微博数据文件路径 
    #   start_time (str) 为开始时间, 格式为: YYYYMMDD
    #   end_time (str) 为结束时间, 格式为YYYYMMDD
    #   history_blog_file (str) 历史数据文件路径
    #   current_blog_file (str) 当前查询时间段的数据文件路径
    cutAndTransform.cut_original_file(filtered_blog_file, start_time, end_time, history_blog_file, current_blog_file)
    print("切割文件完毕")

    # 3. 分词: 将历史时间微博和当前时间微博进行分词及去除表情词、URL链接、停顿词等
    #   history_blog_file (str) 历史数据文件路径 
    #   current_blog_file (str) 当前查询时间段的数据文件路径 
    #   segment_history_blog_file (str) 历史时间分词后的微博文件路径  
    #   segment_current_blog_file (str) 当前时间分词后的微博文件路径  
    Segment.word_segmentation(history_blog_file, segment_history_blog_file)
    Segment.word_segmentation(current_blog_file, segment_current_blog_file)
    print("微博数据分词完毕")

    # 4. 将当前查询时间段的数据文件微博按窗口读入内存 origin_blogdata (用于热点事件的原始微博查询)
    #   current_blog_file (str) 当前查询时间段的数据文件路径 
    #   origin_blogdata (二维列表) 当前时间段原始微博数据 (每一维是一个窗口时间内的原始微博) [['微博1','微博2',...],...]
    origin_blogdata = cutAndTransform.transform_data(current_blog_file)

    # 5. 分词后的历史时间微博和当前时间微博加载进内存 (用于敏感词发现)
    #   segment_history_blog_file (str) 历史时间分词后的微博文件路径 
    #   segment_current_blog_file (str) 当前时间分词后的微博文件路径 
    #   history_blogdata (二维列表): 历史微博数据 (每一维是一个窗口时间内已分词的全部微博) [['微博1','微博2',...],...]
    #   current_blogdata (二维列表): 当前时间段微博数据 (每一维是一个窗口时间内已分词的全部微博) [['微博1','微博2',...],...]
    history_blogdata = cutAndTransform.transform_data(segment_history_blog_file)
    current_blogdata = cutAndTransform.transform_data(segment_current_blog_file)
    print("微博数据加载进内存")

    # 6. 删除中间过程文件
    '''
    if os.path.exists(filtered_blog_file):
        os.remove(filtered_blog_file)
    if os.path.exists(history_blog_file):
        os.remove(history_blog_file)
    if os.path.exists(current_blog_file):
        os.remove(current_blog_file)
    if os.path.exists(segment_history_blog_file):
        os.remove(segment_history_blog_file) 
    if os.path.exists(segment_current_blog_file):
        os.remove(segment_current_blog_file)
    '''

    return history_blogdata, current_blogdata, origin_blogdata


