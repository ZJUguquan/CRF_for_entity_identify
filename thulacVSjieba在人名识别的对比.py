import pandas as pd
import thulac
import jieba.posseg as pseg
names = ['rybh','xm','bj','wz1','wz2','ajbh','afsj','afdd','jyaq']
df = pd.read_table('D:\\pydata-book-master\\rongliuanqing2.csv',names = names)
text_list = pd.Series(df['jyaq']).drop_duplicates()#简要案情去重
ot = open('D:\\pydata-book-master\\thulacVSjieba.txt','w')
thu1 = thulac.thulac()
for x in text_list:
    word1 = thu1.cut(x)
    word2 = pseg.cut(x)
    thulac = [word[0] for word in word1 if word[1]=='np']
    jieba = [w.word for w in word2 if w.flag=='nr']
    #print jieba
    sort_thulac = '_'.join(sorted(set(thulac),key=thulac.index))
    sort_jieba = '_'.join(sorted(set(jieba),key=jieba.index)).encode("utf-8")
    ot.write(x+"|"+sort_thulac+"|"+sort_jieba+"\n")
ot.close()
##DataFrame查看效果
data = pd.read_table("D:\\pydata-book-master\\thulacVSjieba.txt",sep="|",names=['jyaq','thulac','jieba'])
data.head(5)