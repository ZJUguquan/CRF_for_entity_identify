#coding:utf-8

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Required
import numpy as np
from numpy import *
import pandas as pd
import json
import jieba
import jieba.analyse
import thulac
import requests
import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#地点关联相应函数
#将文本文件导入到列表
def loadDataSet(fileName):
    dataSet = []
    fr = open(fileName)
    i = 0
    for line in fr.readlines():
        curLine = line.strip().split('\t')
        fltLine = map(float, curLine)
        dataSet.append(fltLine)
        i += 1
    return dataSet

#单位km
def distSLC(vecA, vecB):
    # 将十进制度数转化为弧度
    lng1, lat1 = map(radians, vecA)
    lng2, lat2 = map(radians, vecB)

    # haversine公式
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * arcsin(sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r

def geocodeB(address):
    response = requests.get('http://api.map.baidu.com/geocoder/v2/?address=' + address + '&output=json&ak=CkTBCTLMZjwfPmM0KvMqug4xdbVtS2BL')
    ans = response.json()
    if ans['status'] == 0:
        return ans['result']['location']['lng'],ans['result']['location']['lat']
    else:
        return 'NULL', 'NULL'

#返回与当前点距离较近的点的集合
#address:输入地址，maxNum:最多取附近的地点的个数，maxDist:最大的距离范围
def nearby(dataSet, address, maxNum, maxDist):
    #判断输入地址的格式，并作适当调整
    if address.startswith('浙江') or address.startswith('绍兴') or (address.find('市') != -1 and address.find('市区') == -1):
        lng, lat = geocodeB(address)
    else:
        lng, lat = geocodeB('浙江绍兴' + address)
    result = []
    if lng == 'NULL':
        result.append('there is something wrong in the address!')
    else:
        near = []
        dataSize = shape(dataSet)[0]
        for i in range(dataSize):
            dist = distSLC(dataSet[i], [lng, lat])
            near.append(dist)
        nplist = np.array(near)
        index = np.argsort(nplist)
        num = 0
        result = []
        distance = []
        for i in index:
            if nplist[i] < maxDist and num < maxNum:
                num += 1
                result.append(i)
                distance.append(nplist[i])
    return result, distance


thu1 = thulac.thulac(user_dict=u'E:/project/绍兴公安项目/容留吸毒/data/shaoxingInfo.txt')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)

#全局变量
resultDf=pd.read_csv(u'E:/project/绍兴公安项目/容留吸毒/data/resultDf.csv')
nrow = resultDf.shape[0]
df = pd.read_csv(u'E:/project/绍兴公安项目/容留吸毒/data/rlaq_u2.txt',sep='\t',encoding='gbk')
jyaq = df['jyaq'].values
dataSet = loadDataSet(u'E:/project/绍兴公安项目/容留吸毒/data/jingweidu.txt')

#表单输入的类
class NameForm(FlaskForm):
    content = TextAreaField(u'请输入案情:', validators=[Required()],
        render_kw={'rows': 5, 'placeholder': u'如：2012年5月8日08时30分，本所在对已抓获吸毒人员胡国松的审查中，发现该犯于2012年4月1日18时30分至2012年4月28日凌晨2时40分，在解放北路隆来堂8438房间，提供吸毒工具，毒品冰毒，先后三次容留金浩勇吸食冰毒，每次共同吸食冰毒约0.2克。'})
    submit = SubmitField(u'提交')

#导出json的类
class NumPyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64) or isinstance(obj, np.int32):
            return int(obj)
        if isinstance(obj, np.float64) or isinstance(obj, np.float32):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500



@app.route('/', methods=['GET', 'POST'])
def index():

    ###案情要素提取
    content = None
    form = NameForm()
    #待输出的结果
    result = {'CJ':[],'AF':[],'DD':[],'RL':[],'BRL':[],'DP':[],'GJ':[],'XY':[]}
    keywords = []

    if form.validate_on_submit():
        #分词
        content = form.content.data
        content = re.sub('\r|\n|\t| ','',content)
        fw = open('C:/Users/guquan/Desktop/CRF++-0.58/test/testData2.txt', 'w')
        segs = thu1.cut(content, text=True).split(' ')
        for seg in segs:
            spl = seg.split('_')
            fw.write(spl[0] + ' ' + spl[1] + '\n')
        fw.write('\n')
        fw.close()

        #执行CRF
        os.system('C:/Users/guquan/Desktop/CRF++-0.58/crf_test.exe -m C:/Users/guquan/Desktop/CRF++-0.58/test/model C:/Users/guquan/Desktop/CRF++-0.58/test/testData2.txt > C:/Users/guquan/Desktop/CRF++-0.58/test/result012.txt')
        
        #读取预测结果
        lines = open('C:/Users/guquan/Desktop/CRF++-0.58/test/result012.txt').readlines()
        tags = ['CJ','AF','DD','RL','BRL','DP','GJ','XY']
        
        #处理预测结果
        strsText = []
        strsTag = []
        for line in lines:
            if len(line) > 1:
                text = line.split('\t')[0]
                tag = line.split('\t')[2]
                strsText.append(text)
                strsTag.append(tag)
            
            else:
                #每一整条结果
                string = ''
                for i in range(len(strsTag)): 
                    if strsTag[i][0] == 'B' or strsTag[i][0] == 'M':
                        tag = strsTag[i][2:-1]
                        string = string + strsText[i]
                        #结束点处理
                        if  i+1<len(strsTag) and strsTag[i+1][0] != 'M' and strsTag[i+1][0] != 'E':
                            result[tag].append(string)
                            result[tag] = list(set(result[tag]))
                            string = ''
                            continue
                    elif strsTag[i][0] == 'E':
                        string = string + strsText[i]
                        result[tag].append(string)
                        result[tag] = list(set(result[tag]))
                        string = ''
                        continue        
                #后期处理
                result['XY'] = list(set(result['XY']) - set(result['RL']))
                result['BRL'] = list(set(result['BRL']) - set(result['RL']))
                if len(result['RL'])==0 and len(result['XY'])>0:
                    result['RL'], result['XY'] = result['XY'], []
                if len(result['RL'])==0 and len(result['XY'])==0:
                    result['XY'], result['BRL'] = result['BRL'], []
                if len(result['RL'])>0 and len(set(result['XY']) - set(result['BRL']))>0:
                    result['XY'] = list(set(result['XY']) - set(result['BRL']))
                #print result
                strsText = []
                strsTag = []

        slct = result
        for key in result.keys():
            result[key] = '，'.join(result[key]).decode('utf8')

        #关键词提取
        jieba.analyse.set_idf_path("C:/Users/guquan/Desktop/CRF++-0.58/IDF_rongliu.txt")
        pat = reduce(lambda x,y:x+y, result.values())
        pat = ('('+ '|'.join(pat)+')').decode('utf8')
        remain = re.sub(pat, '', content)
        keywords = jieba.analyse.extract_tags(remain, topK=10, allowPOS=('a', 'ad', 'an', 'n', 'ns', 'nt', 'nz', 'v', 'vd', 'vn', 'i', 'I'))
        slct['KW'] = keywords
        keywords = '，'.join(keywords).decode('utf8')


        ###社会网络分析

        ##根据涉案人关联
        #'\uff0c'表示逗号
        rl = slct['RL'].replace('[','').replace(']','').replace(' ','').split(u'\uff0c')
        brl = slct['BRL'].replace('[','').replace(']','').replace(' ','').split(u'\uff0c')
        xy = slct['XY'].replace('[','').replace(']','').replace(' ','').split(u'\uff0c')
        people = list(set(rl + brl + xy))
        people = [p for p in people if len(p)>0]
        pat = ('('+ '|'.join(people)+')')
        pat = pat.encode('utf8')
        # num1 = [i for i,v in enumerate(resultDf.RL) if len(re.findall(pat, v))>0]
        # num2 = [i for i,v in enumerate(resultDf.BRL) if len(re.findall(pat, v))>0]
        # num3 = [i for i,v in enumerate(resultDf.XY) if len(re.findall(pat, v))>0]
        # num = list(set(num1 + num2 +num3))
        num1 = resultDf.RL.str.contains(pat)
        num2 = resultDf.BRL.str.contains(pat)
        num3 = resultDf.XY.str.contains(pat)
        num = [(num1[i] or num2[i] or num3[i]) for i in range(nrow)]
        num = [i for i,v in enumerate(num) if v==True]
        print num

        ##根据地点关联
        d0 = slct['DD'].replace('[','').replace(']','').replace(' ','').split(u'\uff0c')[0]
        d0 = d0.decode('utf8')
        near = ['NULL', 'NULL']
        if len(d0)>0:
            near = nearby(dataSet, d0,10, 1)
            if near[0] != 'NULL':
                num = list(sorted(set(num+near[0])))

        ##关联结果
        res = resultDf.loc[num, ]
        print res

        #生成nodes和edges
        nrow2 = res.shape[0]
        ajbh = res.AJBH.tolist()
        index = res.index.values
        nodes = {}
        edges = []
        nodes[d0] = {'id':d0, 'size': 3, 'group': 4, 'class': u'案发地点', 'num': -1, 'dist': 0}
        if len(d0)==0:
            nodes[d0]['id'] = u'本案案发地(未知)'
            nodes[u'AJ本案'] = {'id': u'AJ本案', 'size': len(people), 'group': 0, 'class': u'案件', 'num': -1, 'wzbh': u'无案件编号'}
            edges.append({'source': u'AJ本案', 'target': u'本案案发地(未知)', 'value': 1})
            for p in people:
                edges.append({'source': u'AJ本案', 'target': p, 'value': 1})

        for i in range(nrow2):
            aj = 'AJ'+ajbh[i][-8:]
            nodes[aj] = {'id': aj, 'size': 0, 'group': 0, 'class': u'案件', 'num': index[i], 'wzbh': ajbh[i]}
            for p in res.RL.tolist()[i][1:-1].replace(' ','').split(','):
                if len(p)>0:
                    nodes[aj]['size'] += 1
                    p = p.decode('utf8')
                    if p in nodes.keys():
                        nodes[p]['size'] += 3
                        nodes[p]['group'] = 1
                        nodes[p]['class'] = u'容留者'
                    else :
                        nodes[p] = {'id': p, 'size': 3, 'group': 1, 'class': u'容留者', 'num': index[i]}
                    edges.append({'source': aj, 'target': p, 'value': 1})      
            for p in res.BRL.tolist()[i][1:-1].replace(' ','').split(','):
                if len(p)>0:
                    nodes[aj]['size'] += 1
                    p = p.decode('utf8')
                    if p in nodes.keys():
                        nodes[p]['size'] += 1.5
                    else :
                        nodes[p] = {'id': p, 'size': 1.5, 'group': 3, 'class': u'被容留', 'num': index[i]}
                    edges.append({'source': aj, 'target':p, 'value': 1})
            for p in res.XY.tolist()[i][1:-1].replace(' ','').split(','):
                if len(p)>0:
                    nodes[aj]['size'] += 1
                    p = p.decode('utf8')
                    if p in nodes.keys():
                        nodes[p]['size'] += 2
                    else :
                        nodes[p] = {'id':p, 'size': 2, 'group': 2, 'class': u'其他嫌疑人', 'num': index[i]}
                    edges.append({'source': aj, 'target': p, 'value': 1})
                    
            d = res.DD.tolist()[i][1:-1].replace(' ','').split(',')[0]
            if len(d)>0:
                nodes[aj]['size'] += 1
                d = d.decode('utf8')
                edges.append({'source': aj, 'target': d, 'value': 1})
                #判断是否为本案地点
                if d!=d0:
                    if d in nodes.keys():
                        nodes[d]['size'] += 1
                    else :
                        nodes[d] = {'id':d, 'size': 2, 'group': 4, 'class': u'案发地点', 'num': index[i]}
                    #判断是否为根据经纬度关联到的地点  
                    if near[0] != 'NULL' and (index[i] in near[0]):
                        nodes[d]['dist'] = near[1][near[0].index(index[i])]
                        edges.append({'source': d0, 'target': d, 'value': 1})


        #每个nodes的相应说明info
        info = {}
        for item in nodes.items():
            if item[1]['class'] == u'案件':
                #判断是否‘AJ本案’
                if item[1]['num'] == -1:
                    info[item[0]] = {'name': item[0], u'案件编号': item[1]['wzbh'], u'简要案情': content}
                else:
                    info[item[0]] = {'name': item[0], u'案件编号': item[1]['wzbh'], u'简要案情': jyaq[item[1]['num']]}
            elif item[1]['class'] == u'案发地点':
                if 'dist' in item[1].keys():
                    info[item[0]] = {'name': item[0], u'与本案距离': str(round(item[1]['dist']*1000))+u'米'}
                else:
                    info[item[0]] = {'name': item[0]}
            else:
                info[item[0]] = {'name': item[0], u'性别': 'XX', u'出生日期': '19XX-XX-XX'}

        #导出json供d3调用
        nodes1 = []
        for value in nodes.values():
            nodes1.append(value)

        global data1
        global data2
        data1 = {'nodes': nodes1, 'links': edges}
        data2 = info   

    return render_template('index.html', form=form, name=content, result=result, keywords=keywords)

@app.route('/data1')
def data1():
    return json.dumps(data1,ensure_ascii=False,indent=2,cls=NumPyEncoder,encoding='utf8')

@app.route('/data2')
def data2():
    return json.dumps(data2,ensure_ascii=False,indent=2,cls=NumPyEncoder,encoding='utf8',sort_keys=True)



if __name__ == '__main__':
    app.run(port=111)
