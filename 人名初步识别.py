import pandas as pd
import thulac
names = ['rybh','xm','bj','wz1','wz2','ajbh','afsj','afdd','jyaq']
df = pd.read_table('D:\\pydata-book-master\\rongliuanqing2.csv',names = names)
text_list = pd.Series(df['jyaq']).drop_duplicates()#简要案情去重
thu1 = thulac.thulac()
#dic = {}
ot = open('D:\\pydata-book-master\\rlxd.txt','a')
for x in text_list:
    words = thu1.cut(x)
    name = [word[0] for word in words if word[1]=='np']
    sort_name = '_'.join(sorted(set(name),key=name.index))##去重，并把列表转换成字符串
    ot.write(x+"|"+sort_name+'\n')
ot.close()