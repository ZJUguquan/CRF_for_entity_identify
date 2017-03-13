#coding=utf-8

import os
os.chdir(u'E:/project/绍兴公安项目/容留吸毒')
import pandas as pd
import numpy as np

#读取去重后的数据
rlaq_u2=pd.read_csv('rlaq_u2.csv')

#-------------------------------------------------------

#1.jieba分词
import jieba
import jieba.posseg as pseg
import jieba.analyse
jieba.initialize()

#文本初始化
i = 1111
id = rlaq_u2.loc[i,'id']
ajbh = rlaq_u2.loc[i,'ajbh']
fssj = pd.to_datetime(rlaq_u2.loc[i,'time'])
txt = rlaq_u2.loc[i,'jyaq']
txt0 = txt
place = rlaq_u2.loc[i,'place']
print(txt0)

#时间处理
time = pd.Series(txt).str.findall('([0-9]{4}年[0-9]{1,2}月[0-9]{1,2})')[0]
if len(time)>0:
    time = pd.Series(time).str.replace('(年|月)','-')
time = pd.to_datetime(time)
print time,'\n'

#剩下的文本
txt = pd.Series(txt).str.replace('([0-9]{4}年|[0-9]{1,2}月|([0-9]{1,2}日|号)|[0-9]{1,2}时|[0-9]{1,2}分|[0-9]{1,2}秒)','')
print(txt[0])

#地点处理
#录入的地点
print(place)

#提取的地点
seg = pseg.cut(txt[0])
place0 = [w.word for w  in seg if w.flag=='ns' and len(w.word)>=2]

#修改录入地点（去重）
pat = ('('+'|'.join(set(place0))+')').encode('utf-8')#也能在括号前面+u
print(pat)
place1 = pd.Series(place).str.replace(pat,'')[0]
print(place1)

#最终地点
place2 = ''.join(set(place0))+place1.decode('utf-8')
print(place2)

#剩下的文本
if len(place1)!=0:
    txt = txt.str.replace(pat,'')
print txt[0]

#人物处理
#提取出的人
seg = pseg.cut(txt[0])
people0 = set([w.word for w  in seg if w.flag=='nr' and len(w.word)>=2])
pat = ('('+'|'.join(set(people0))+')').encode('utf-8')
print pat

#录入的人（嫌疑人）
people1 = rlaq_u.name[rlaq_u.ajbh==ajbh].tolist()[0].decode('utf8')
print people1

#仅参与吸毒的人
people2 = people0 - set([people1])
print '|'.join(people2)

#剩下的文本
if len(people0)!=0:
    txt = txt.str.replace(pat,'')
print txt[0]

#事件关键词
#tf-idf
event1 = '|'.join(jieba.analyse.extract_tags(txt[0], topK=10))
print event1

#textrank
event2 = '|'.join(jieba.analyse.textrank(txt[0], topK=10))
print event2

#------------------------------------------------------

#2.清华大学LAC分词工具
import thulac
thu1 = thulac.thulac()

#文本初始化
i = 77
id = rlaq_u2.loc[i,'id']
ajbh = rlaq_u2.loc[i,'ajbh']
fssj = pd.to_datetime(rlaq_u2.loc[i,'time'])
txt = rlaq_u2.loc[i,'jyaq']
txt0 = txt
place = rlaq_u2.loc[i,'place']
print(txt0)

#时间处理
time = pd.Series(txt).str.findall('([0-9]{4}年[0-9]{1,2}月[0-9]{1,2})')[0]
if len(time)>0:
    time = pd.Series(time).str.replace('(年|月)','-')
time = pd.to_datetime(time)
print time,'\n'

#剩下的文本
txt = pd.Series(txt).str.replace('([0-9]{4}年|[0-9]{1,2}月|([0-9]{1,2}日|号)|[0-9]{1,2}时|[0-9]{1,2}分|[0-9]{1,2}秒)','')
print(txt[0])

#地点处理
#录入的地点
print(place)

#提取的地点
seg =  thu1.cut(txt[0])
place0 = set([w[0].decode('utf8') for w  in seg if w[1]=='ns' and len(w[0])>=2])

#修改录入地点（去重）
pat = ('('+'|'.join(place0)+')').encode('utf-8')#也能在括号前面+u
print(pat)
place1 = pd.Series(place).str.replace(pat,'')[0]
print(place1)

#最终地点
place2 = ''.join(set(place0))+place1.decode('utf-8')
print(place2)

#剩下的文本
if len(place1)!=0:
    txt = txt.str.replace(pat,'')
print txt[0]

#人物处理
#提取出的人，注意编码...
seg = thu1.cut(txt[0])
people0 = set([w[0].decode('utf8') for w  in seg if w[1]=='np' and len(w[0])>=2])

pat = ('('+ '|'.join(people0)+')').encode('utf-8')
print pat

#录入的人（嫌疑人）
people1 = rlaq_u.name[rlaq_u.ajbh==ajbh].tolist()
people1 = [p.decode('utf8') for p in people1]
print '/'.join(people1)

#仅参与吸毒的人
people2 = people0 - set(people1)
print '|'.join(people2)

#剩下的文本
if len(people0)!=0:
    txt = txt.str.replace(pat,'')
print txt[0]

#----------------------------------------------------

#3.bosennlp分词器
from __future__ import print_function, unicode_literals
from bosonnlp import BosonNLP
mytoken = 'wHXup4Wh.13586.tkz9YxHxkO_o'
nlp = BosonNLP(mytoken)

#文本初始化
i = 77
id = rlaq_u2.loc[i,'id']
ajbh = rlaq_u2.loc[i,'ajbh']
fssj = pd.to_datetime(rlaq_u2.loc[i,'time'])
txt = rlaq_u2.loc[i,'jyaq']
txt0 = txt
place = rlaq_u2.loc[i,'place']
print(txt0)

#提取时间、地点、人物
result = nlp.ner(txt)[0]
words = result['word']
entities = result['entity']
Btime = []
Bplace = []
Bpeople = []
for entity in entities:
    if entity[2]=='time':
        Btime.append(''.join(words[entity[0]:entity[1]]))
    if entity[2]=='location':
        Bplace.append(''.join(words[entity[0]:entity[1]]))
    if entity[2]=='person_name':
        Bpeople.append(''.join(words[entity[0]:entity[1]]))
print('时间：',' | '.join(Btime))
print('地点：',' | '.join(Bplace))
print('人物：',' | '.join(Bpeople))

#提取关键词
kw = nlp.extract_keywords(txt, top_k=10)
for w,k in kw:
    print('关键词：',k,' , ','权重：',w)