#coding:utf8

lines = open('data/result.txt').readlines()

#fw = open('data/output.txt', 'w')
strsText = []
strsTag = []
tags = ['CJ','AF','DD','RL','BRL','DP','GJ','XY']
tagname = ['出警时间','案发时间','案发地点','容留者','被容留者','毒品名称','吸毒工具','嫌疑人']

for line in lines:
    if len(line) > 1:
        text = line.split('\t')[0]
        tag = line.split('\t')[2]
        strsText.append(text)
        strsTag.append(tag)
    else:
        str = ''
        for i in range(len(strsTag)):
            if strsTag[i][0] == 'B':
                str = str + ' (' + tagname[tags.index(strsTag[i][2:-1])] + ')' + strsText[i]
                if len(strsTag) > i+1 and strsTag[i+1][0] != 'M' and strsTag[i+1][0] != 'E':
                    str += ' '
            elif strsTag[i][0] == 'M':
                str = str + strsText[i]
            elif strsTag[i][0] == 'E':
                str = str + strsText[i] + ' '
            else:
                str = str + strsText[i]
        print str
        strsText = []
        strsTag = []