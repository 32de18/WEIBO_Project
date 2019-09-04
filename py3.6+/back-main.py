#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys


def main():
    """
     通过sys模块来识别参数
    """
    # print(u'参数个数为:', len(sys.argv), '个参数。')
    # print(u'参数列表:', str(sys.argv))
    # print(u'脚本名为：', sys.argv[0])
    # for i in range(1, len(sys.argv)):
    #     print(u'参数 %s 为：%s' % (i, sys.argv[i]))

    str_in = input()
    print("output: " + str_in)


if __name__ == "__main__":
    main()
