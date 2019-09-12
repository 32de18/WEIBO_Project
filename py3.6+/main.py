################################################################################
##
##  新浪微博热点事件发现与脉络生成系统
##
##      @Filename       ./main.py
##      @Author         李林峰, 刘臻, 徐润邦, 马伯乐, 朱杰, 瞿凤业
##      @Version        3.1
##      @Date           2019/09/06
##      @Copyright      Copyright (c) 2019. All rights reserved.
##      @Description    主控程序 main()
##
################################################################################
import sys
import os
MYDIR = os.path.dirname(__file__)
sys.path.append(os.path.join(MYDIR, './DataProcess/'))
sys.path.append(os.path.join(MYDIR, './DetectHotspots/'))
sys.path.append(os.path.join(MYDIR, './HotspotsAnalysis/'))
import DataProcess
import DetectHotspots
import CorrelationAnalysis



##  系统主控程序 - Master Control
#   <summary> 集成数据处理、事件发现、关联性分析功能 </summary>
#   <io>
#       std input:  向 original_filepath (str) 写入加载待处理的微博数据文件路径
#                   向 start_time (str) 写入需要发现热点事件的时间段的起始时间, 格式: "YYYYMMDD"
#                   向 end_time (str) 写入需要发现热点事件的时间段的起始时间, 格式: "YYYYMMDD"
#                   向 hotspots_filepath (str) 路径写入生成的热点事件文件路径
#                   向 correlation_filepath (str) 路径写入热点事件关联性文件路径
#       file output:向 hotspots_filepath (str) 路径写入热点事件供界面读取
#                   向 correlation_filepath (str) 路径写入热点事件关联性矩阵供界面读取
#   </io>
def main():
    # 输入原始博文，起始时间，截止时间
    original_filepath = input()
    start_time = input()
    end_time = input()
    hotspots_filepath = input()
    correlation_filepath = input()

    # 数据处理
    history_blogdata, current_blogdata, origin_blogdata \
         = DataProcess.data_process(original_filepath, start_time, end_time)

    # 热点事件生成
    DetectHotspots.detect_hotspots(history_blogdata, current_blogdata, origin_blogdata, hotspots_filepath)

    # 相关性分析
    CorrelationAnalysis.generate_correlation_matrics(hotspots_filepath, correlation_filepath)
    
    print("CODE_0")



# 执行
main()


