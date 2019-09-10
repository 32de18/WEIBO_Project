################################################################################
##
##  新浪微博热点事件发现与脉络生成系统
##
##      @Filename       ./DataProcess/Segment.py
##      @Author         李林峰, 刘臻, 徐润邦, 马伯乐, 朱杰, 瞿凤业
##      @Version        3.1
##      @Date           2019/09/06
##      @Copyright      Copyright (c) 2019. All rights reserved.
##      @Description    本文件为数据处理模块提供分词及词语筛选功能
##
################################################################################
import re
import csv
import pkuseg
import os
MYDIR = os.path.dirname(__file__)



#   表情词名单文件路径
expression_word_filepath = '../Configuration/expression_word_cleaned.txt'
#   停顿词名单文件路径
sw_filepath = '../Configuration/stopping_word.txt'



##  模块内部接口
#   <summary> 对微博进行分词并去除表情词、停顿词、URL链接以及标点符号 </summary>
#   <param>
#       input_filepath (字符串): 待分词微博文件输入路径 
#       output_filepath (字符串): 已分词的微博文件输出路径 
#   </param>
#   <io>
#       file input: 从 expression_word_filepath (str) 路径读入表情词
#                   从 sw_filepath (str) 路径读入停顿词 
#                   从 input_filepath (str) 路径读入原始微博 
#       file output:向 output_filepath (str) 路径写入分词后的微博 
#   </io>
def word_segmentation(input_filepath, output_filepath):
    # 1.加载表情词 
    ex_word_set = []            # 表情词
    with open(os.path.join(MYDIR,expression_word_filepath), 'r', encoding='utf8') as ex_word_fp:
        for line in ex_word_fp:
            ex_word_set.append(line.strip('\n') + ']')

    # 2.加载停顿词 
    sw_set = set()              # 停顿词
    with open(os.path.join(MYDIR,sw_filepath), 'r', encoding='utf-8') as fp_sw:
        for line in fp_sw:
            sw_set.add(line.strip())

    # 3.加载分词库
    seg = pkuseg.pkuseg(model_name='web')

    # 4.去除表情词、停顿词、URL链接 并 分词
    with open(os.path.join(MYDIR,input_filepath), 'r', encoding='utf8') as fp_r, \
            open(os.path.join(MYDIR,output_filepath), 'w', encoding='utf8', newline='') as fp_w:
        csv_writer = csv.writer(fp_w)

        for line in fp_r:
            res = line.strip('\n').split(',')
            if res.__len__() < 3:
                continue
            content = res[2]

            # 4.1. 去除表情词
            for ex_word in ex_word_set:
                if content.find(ex_word) != -1:  # 包含表情词
                    content = content.replace(ex_word, ' ')

            # 4.2. 去除URL链接
            content = re.sub(
                r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', content, flags=re.MULTILINE)

            # 4.3. 去除标点符号, 仅保留中英文词及数字
            content = re.sub(
                u'[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a]', ' ', content)

            # 4.4. 去除多余空格
            content = re.sub(r'\s+', ' ', content, flags=re.MULTILINE).strip()

            # 4.5. 分词
            str_cut = seg.cut(content)

            # 4.6. 获取长度大于1个汉字以及非停顿词的词语
            content = ''
            for i in str_cut:
                if len(bytes(i, encoding='utf8')) > 3 and (i not in sw_set):
                    content += i + ' '
            content = content.strip()

            # 4.7. 去除过短词语, 多于两个汉字
            if len(bytes(content, encoding='utf8')) < 7:
                continue

            res[2] = content
            csv_writer.writerow(res)


