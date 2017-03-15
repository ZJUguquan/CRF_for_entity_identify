#coding:utf8
import os
os.chdir(u'E:/project/绍兴公安项目/容留吸毒')
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import thulac
import pandas as pd

df = pd.read_csv('data/train_u2.txt',sep='\t',encoding='gbk')
lines = df['jyaq'].values[0:200]

#添加自定义字典
thu1 = thulac.thulac(user_dict='data/shaoxingInfo.txt')

#输出文件
fw = open('data/trainData200.txt', 'w')
n = 0
for line in lines:
    segs = thu1.cut(line, text=True).split(' ')
    for seg in segs:
        spl = seg.split('_')
        fw.write(spl[0] + ' ' + spl[1] + '\n')
    fw.write('\n')
fw.close()