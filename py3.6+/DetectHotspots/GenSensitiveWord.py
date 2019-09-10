################################################################################
##
##  新浪微博热点事件发现与脉络生成系统
##
##      @Filename       ./DetectHotspots/GenSensitiveWord.py
##      @Author         李林峰, 刘臻, 徐润邦, 马伯乐, 朱杰, 瞿凤业
##      @Version        3.1
##      @Date           2019/09/06
##      @Copyright      Copyright (c) 2019. All rights reserved.
##      @Description    敏感词生成模块. 生成主要词及每个主要词的语境词列表及语境词与
##                      主要词的相关性权重. 
##
################################################################################
import numpy as np



# 参数控制
w2alpha = 3             # alpha/w 的值
lambda_const = 0.996    # 迭代系数
pri_retention = 0.004   # 主要词保留系数



##  模块内部接口
#   <summary> 生成词汇表 </summary>
#   <param>
#       history_blogdata (二维列表): 历史微博数据 (每一维是一个窗口时间内的全部微博) [['微博1','微博2',...],...]
#       current_blogdata (二维列表): 当前时间段微博数据 (每一维是一个窗口时间内的全部微博) [['微博1','微博2',...],...]
#   </param>
#   <return>
#       vocab_dic (字典): 词汇表, 词->基础词频, 基础词频默认为0
#   </return>
def gen_vocabulary_list(history_blogdata, current_blogdata):
    vocab_dic = {}
    for blog_oneday in history_blogdata:
        for blog in blog_oneday:
            for word in blog.strip('\n').split():
                vocab_dic.setdefault(word, 0)
    for blog_oneday in current_blogdata:
        for blog in blog_oneday:
            for word in blog.strip('\n').split():
                vocab_dic.setdefault(word, 0)
    return vocab_dic



##  模块内部接口
#   <summary> 计算 window_blog 窗口内微博数据的窗口词频 </summary>
#   <param>
#       window_blog (一维列表): 一个窗口内的全部微博数据 ['微博1','微博2',...]
#   </param>
#   <return>
#       frequency (字典): 窗口词表, 窗口内微博数据的窗口词频, 窗口词->窗口词频, 词频 = 词出现次数/总次数
#   </return>
def calculate_window_blog(window_blog):
    frequency = {}
    total = 0
    for blog in window_blog:
        for word in blog.strip('\n').split():
            frequency.setdefault(word, 0)
            frequency[word] += 1
            total += 1
    for word in frequency:
        frequency[word] /= total
    return frequency



##  模块内部接口
#   <summary> 迭代计算F_b(基础词频) </summary>
#   <param>
#       vocab_dic (字典): 词汇表, 所有词->基础词频
#       frequency (字典): 窗口词表, 窗口词->窗口词频
#   </param>
#   <return>
#       vocab_dic (字典): 词汇表, 所有词->基础词频
#   </return>
def cal_words_fb(vocab_dic, frequency):
    for word in frequency:
        vocab_dic[word] = lambda_const * vocab_dic[word] + (1 - lambda_const) * frequency[word]
    return vocab_dic



##  模块内部接口
#   <summary> 计算词语对应的WS </summary>
#   <param>
#       vocab_dic (字典): 词汇表, 所有词->基础词频
#       frequency (字典): 窗口词表, 窗口词->窗口词频
#   </param>
#   <return>
#       WS_dic (字典): 窗口词->窗口词WS值
#   </return>
def cal_WS_dic(vocab_dic, frequency):
    WS_dic = {}
    for word in frequency:
        WS_dic.setdefault(word, 0)
        if vocab_dic[word]:
            WS_dic[word] = frequency[word] / float(vocab_dic[word])
        else:
            WS_dic[word] = 1
    return WS_dic



##  模块内部接口
#   <summary> 对WS进行箱线图分析得到上限w和上限的 w2alpha 倍alpha </summary>
#   <param>
#       WS_dic (字典): 窗口词->窗口词WS值
#   </param>
#   <return>
#       w (float): 对WS值进行箱线图分析的上限
#       alpha (float): w的 w2alpha 倍
#   </return>
def cal_w_and_alpha(WS_dic):
    #按照value排序 
    WS_dic = sorted(WS_dic.items(), key=lambda d: d[1], reverse=True)
    nums = []
    for word in WS_dic:
        nums.append(word[1])
    res = np.percentile(nums, (25,50,75), interpolation='midpoint')
    #计算 w 和 alpha
    w = res[2] + 1.5 * (res[2] - res[0])
    alpha = w2alpha * w                                                                 						##### 参数改变
    return w, alpha



##  模块内部接口
#   <summary> 生成窗口内的主要词 </summary>
#   <param>
#       frequency (字典): 窗口词表, 窗口词->窗口词频
#       WS_dic (字典): 窗口词->窗口词WS值
#       alpha (float): WS值进行箱线图分析的上限的 w2alpha 倍
#   </param>
#   <return>
#       primary_words_list (一维列表): 主要词列表 [主要词1,主要词2,...]
#   </return>
def detect_primary_word(frequency, WS_dic, alpha):
    primary_words_dict = {}     # 主要词候选集合
    primary_words_list = []     # 主要词集合
    for word in frequency:
        if WS_dic[word] >= alpha:
            primary_words_dict.setdefault(word, frequency[word])
    sort_primary_words_dict = sorted(primary_words_dict.items(), key=lambda d: d[1], reverse=True)
    length = len(sort_primary_words_dict) * pri_retention
    count = 0
    for word in sort_primary_words_dict:
        count+=1
        if count >= length:
            break
        primary_words_list.append(word)
    return primary_words_list



##  模块内部接口
#   <summary> 生成窗口内某个主要词对应的语境词 </summary>
#   <param>
#       frequency (字典): 窗口词表, 窗口词->窗口词频
#       WS_dic (字典): 窗口词->窗口词WS值
#       w (float): 对WS值进行箱线图分析的上限
#       primary_words_list (一维列表): 主要词列表 [主要词1,主要词2,...]
#       window_blog (一维列表): 一个窗口内的全部微博数据 ['微博1','微博2',...]
#   </param>
#   <return>
#       docList (二维列表): 窗口内的敏感词 [[主要词1,(语境词1,概率),(语境词2,概率),..], ...]
#   </return>
def detect_context_word(frequency,WS_dic,w,primary_words,window_blog):
    context_words_list = [] # 语境词候选集合
    docList = []
    tmp = []                # 包含某个主要词的今日微博集合
    sort_dic = {}           # 用于对语境词的pdw排序，只取前10个pdw

    for word in frequency:
        if WS_dic[word] >= w:
            context_words_list.append(word)
    for pWord in primary_words:
        #[主要词,(语境词1，条件概率1),...]
        doc=[]
        doc.append((pWord[0], 1.00))

        tmp.clear()
        #取包含该主要词的今日微博,存入tmp
        for blog in window_blog:
            for word in blog.strip('\n').split():
                if word == pWord[0]:
                    tmp.append(blog)
                    break

        #遍历语境词候选集合，计算每个候选语境词在该集合中出现的条件概率
        for contextWord in context_words_list:
            count = 0
            #计算语境候选词在包含该主要词的今日微博中出现的次数
            for blog in tmp:
                for word in blog.strip('\n').split():
                    if word == contextWord:
                        count += 1
            # 该主要词对应的该语境候选词出现的条件概率
            pdw = count / len(tmp)
            sort_dic[contextWord] = pdw
        res = sorted(sort_dic.items(), key=lambda d: d[1], reverse=True)
        count = 0
        for i in res:
            count += 1
            if count == 11:
                break
            if i[0] == pWord[0]:
                continue
            if i[1] == 0:
                break
            doc.append((i[0],i[1]))
        if len(doc)>2:
          docList.append(doc)
    return docList



##  模块对外接口
#   <summary> 生成敏感词列表 sensitive_word_list </summary>
#   <param>
#       history_blogdata (二维列表): 历史微博数据 (每一维是一个窗口时间内的全部微博) [['微博1','微博2',...],...]
#       current_blogdata (二维列表): 当前时间段微博数据 (每一维是一个窗口时间内的全部微博) [['微博1','微博2',...],...]
#   </param>
#   <return>
#       sensitive_word_list (三维列表): 敏感词列表 [[[窗口1主要词1,(语境词1,概率),..],...], ...]
#   </return>
def gen_sensitive_word(history_blogdata, current_blogdata):
    # 1. 生成词汇表 vocab_dic (字典: 词->基础词频)
    vocab_dic = gen_vocabulary_list(history_blogdata, current_blogdata)

    # 2. 在 vocab_dic 里生成历史微博数据基础词频 
    for window_blog in history_blogdata:				# window_blog 某一窗口时间内的全部微博 ['微博1','微博2',...]
        # 计算 window_blog 窗口内微博数据的窗口词频 frequency (字典: 窗口词->窗口词频)
        frequency = calculate_window_blog(window_blog)
        # 迭代 vocab_dic 的基础词频
        vocab_dic = cal_words_fb(vocab_dic, frequency)

    # 3. 根据 current_blogdata 微博数据生成每一窗口内的敏感词: 主要词 + 语境词
    sensitive_word_list = []
    for window_blog in current_blogdata:
        # 计算 window_blog 窗口内微博数据的窗口词频 frequency (字典: 窗口词->窗口词频)
        frequency = calculate_window_blog(window_blog)
        # 计算窗口词的WS值: WS_dic(字典: 窗口词->WS值) = 窗口词频/基础词频
        WS_dic = cal_WS_dic(vocab_dic, frequency)
        # 对 WS_dic 进行箱线图分析得到 w(上限) 和 alpha
        w, alpha = cal_w_and_alpha(WS_dic)
        # 得到窗口内主要词列表 primary_words [主要词1,主要词2,...]
        primary_words = detect_primary_word(frequency, WS_dic, alpha)
        # 得到窗口内语境词列表 contextual_words [[主要词1,(语境词1,概率),(语境词2,概率),..], ...]
        context_words = detect_context_word(frequency, WS_dic, w, primary_words, window_blog)
        sensitive_word_list.append(context_words)
	    # 依据窗口词频迭代更新 vocab_dic 的基础词频
        vocab_dic = cal_words_fb(vocab_dic, frequency)

    return sensitive_word_list


