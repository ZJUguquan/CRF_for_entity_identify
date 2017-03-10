#coding=utf-8  

import os
os.chdir(u'E:/project/绍兴公安项目/容留吸毒')
import pandas as pd
import numpy as np

#读取数据
rlaq = pd.read_csv('rongliuanqing2.csv',sep='\t',header=None)
rlaq.columns = ['id','name','sdqk','xdbj','cxyy','ajbh','time','place','jyaq']

#文本初步去重
rlaq_u = rlaq.loc[:,['id','ajbh','time','name','place','jyaq']].drop_duplicates()  

#根据案件编号ajbh和简要案情jyaq去重
rlaq_u2 = rlaq_u.loc[:,['id','ajbh','time','place','jyaq']].groupby(['ajbh','jyaq']).last().reset_index()

#提取年月日
rlaq_u2.loc[:,'time'] = rlaq_u2.loc[:,'time'].str.slice(0,10)

#增加一列time1用于去重
time1=rlaq_u2.loc[:,'jyaq'].str.extract('([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日|号)',expand=False)
time1[time1.isnull()]=rlaq_u2.loc[:,'jyaq'][time1.isnull()].str.slice(0,12)
rlaq_u2['time1']=time1
rlaq_u2=rlaq_u2.groupby(['id','time1']).last().reset_index()


#rlaq_u2.to_csv('rlaq_u2.csv',index=False)
