################################################################################
##
##  新浪微博热点事件发现与脉络生成系统
##
##      @Filename       ./DataProcess/RemoveAd.py
##      @Author         李林峰, 刘臻, 徐润邦, 马伯乐, 朱杰, 瞿凤业
##      @Version        3.1
##      @Date           2019/09/06
##      @Copyright      Copyright (c) 2019. All rights reserved.
##      @Description    本文件为数据处理模块提供微博数据广告过滤功能
##
################################################################################
import csv
import os
MYDIR = os.path.dirname(__file__)



#   广告词名单文件路径
ad_word_filepath = '../Configuration/ad_word.txt'



##  模块内部接口
#   <summary> 去除含有广告词的文本 </summary>
#   <param>
#       input_filepath (str): 微博原始数据文件路径 
#       output_filepath (str): 广告过滤后的微博数据文件路径 
#   </param>
#   <io>
#       file input: 从 ad_word_filepath (str) 路径读入广告词 
#                   从 input_filepath (str) 路径读入原始微博 
#       file output:向 output_filepath (str) 路径写入过滤后的微博 
#   </io>
def remove_advertising(input_filepath, output_filepath):
    ad_word_set = set()                 # 广告等敏感词集合

    # 1.读入广告词到 ad_word_set (set)
    with open(os.path.join(MYDIR,ad_word_filepath), 'r', encoding='utf8') as ad_word_fp:
        for line in ad_word_fp:
            ad_word_set.add(line.strip('\n'))

    # 2.对每条微博筛选 (含有广告词则去除)
    with open(input_filepath, 'r', encoding='utf8') as fp_r, \
            open(os.path.join(MYDIR, output_filepath), 'w', encoding='utf8', newline='') as fp_w:
        csv_writer = csv.writer(fp_w)
        for line in fp_r:
            res = line[:-5].split(",")
            # 查看该条微博是否含有广告词 (flag_ad = True, 则含有, 去除该条微博)
            flag_ad = False
            for ad_word in ad_word_set:
                try:
                    if res[2].find(ad_word) != -1:
                        flag_ad = True
                        break
                except:
                    # print(ad_word)    # 打印出问题的广告词
                    continue
            if not flag_ad:
                csv_writer.writerow(res)


