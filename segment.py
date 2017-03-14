#coding:utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import thulac
import pandas as pd

df = pd.read_csv('data/rlaq_u2.csv')
lines = df['jyaq'].values

#输出文件
fw = open('data/testData.txt', 'w')
#添加自定义字典
thu1 = thulac.thulac(user_dict='data/shaoxingInfo.txt')
n = 0
for line in lines:
    if n >= 1000:
        segs = thu1.cut(line, text=True).split(' ')
        for seg in segs:
            spl = seg.split('_')
            fw.write(spl[0] + ' ' + spl[1] + '\n')
        fw.write('\n')
    n += 1
fw.close()
