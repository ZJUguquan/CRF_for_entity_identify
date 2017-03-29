#coding:utf8

from numpy import *
import numpy as np
import requests

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
#maxNum:最多取附近的地点的个数
#maxDist:最大的距离范围
#inPoint:输入地址
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


if __name__ == '__main__':
    dataSet = loadDataSet('data/jingweidu.txt')
    near, distance = nearby(dataSet, '绍兴市公安局',10, 1)
    print near
    print distance