################################################################################
##
##  新浪微博热点事件发现与脉络生成系统
##
##      @Filename       ./DataProcess/cutAndTransform.py
##      @Author         李林峰, 刘臻, 徐润邦, 马伯乐, 朱杰, 瞿凤业
##      @Version        3.1
##      @Date           2019/09/06
##      @Copyright      Copyright (c) 2019. All rights reserved.
##      @Description    本文件为数据处理模块提供文件分割以及将特定文件数据加载进内存
##                      功能
##
################################################################################
import os
MYDIR = os.path.dirname(__file__)



##  模块内部接口
#   <summary>
#       将微博数据文件按照事件查询起止时间分为两个文件 history_blog_file 和 current_blog_file
#   </summary>
#   <param>
#       before_cut_file_path (str): 全部微博数据的文件路径
#       start_time (str): 事件查询开始时间(如: 20170401)
#       end_time (str): 事件查询结束时间(如: 20170402)
#       dest_history_path (str): 切割后的历史数据文件路径
#       dest_current_path (str): 切割后的当前查询时间段的数据文件路径
#   </param>
#   <io>
#       file input: 从 before_cut_file_path (str) 路径读入全部微博数据 
#       file output:向 dest_history_path (str) 路径写入切割后的历史数据
#                   向 dest_current_path (str) 路径写入切割后的当前查询时间段的数据
#   </io>
def cut_original_file(before_cut_file_path, start_time, end_time, dest_history_path, dest_current_path):
    with open(os.path.join(MYDIR,before_cut_file_path),'r',encoding='utf-8') as f:
        history_blog_content = []
        current_blog_content = []
        lines = f.readlines()
        for line in lines:
            tmp = line.strip("\n").split(",")
            time = tmp[0]

            if time < start_time:
                history_blog_content.append(line)
            elif time >= start_time and time <= end_time:
                current_blog_content.append(line)
            else:
                break

        history_blog_file = open(os.path.join(MYDIR,dest_history_path),'w',encoding='utf-8')
        history_blog_file.writelines(history_blog_content)
        history_blog_file.close()

        current_blog_file = open(os.path.join(MYDIR,dest_current_path),'w',encoding='utf-8')
        current_blog_file.writelines(current_blog_content)
        current_blog_file.close()
    f.close()



##  模块内部接口
#   <summary> 转化数据形式, 将微博按照窗口时间(暂定为1天)分行加载进内存 </summary>
#   <param>
#       file (str): 读入文件路径 (文件一行为一条微博数据)
#   </param>
#   <io>
#       file input: 从 file (str) 路径读入微博数据 
#   </io>
#   <return>
#       res (二维列表): 每行为一个窗口时间的微博[['窗口1的微博1','窗口1的微博2',...],['窗口2的微博1',...]...]
#   </return>
def transform_data(file):
    with open(os.path.join(MYDIR,file), encoding='utf-8') as f:
        res = []
        blog_oneday = []
        flag = 1
        date_now = ''

        for line in f:
            tmp = []
            attributes = line.strip('\n').split(',')
            date = attributes[0]  # 博文日期
            blog = attributes[2]  # 博文内容
            if flag == 1:
                date_now = date
                blog_oneday.append(blog)
                flag = 0
                continue
            if date == date_now:
                blog_oneday.append(blog)
            if date != date_now:
                tmp.extend(blog_oneday)
                res.append(tmp)
                date_now = date
                blog_oneday.clear()
                blog_oneday.append(blog)
        res.append(blog_oneday)
        return res


