#coding:utf-8

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Required
import thulac
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

thu1 = thulac.thulac(user_dict=u'E:/project/绍兴公安项目/容留吸毒/data/shaoxingInfo.txt')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    content = TextAreaField(u'请输入案情:', validators=[Required()],
        render_kw={'rows': 10, 'placeholder': u'如：2012年5月8日08时30分，本所在对已抓获吸毒人员胡国松的审查中，发现该犯于2012年4月1日18时30分至2012年4月28日凌晨2时40分，在解放北路隆来堂8438房间，提供吸毒工具，毒品冰毒，先后三次容留金浩勇吸食冰毒，每次共同吸食冰毒约0.2克。'})
    submit = SubmitField(u'提交')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    content = None
    form = NameForm()
    #待输出的结果
    result = {'CJ':[],'AF':[],'DD':[],'RL':[],'BRL':[],'DP':[],'GJ':[],'XY':[]}
    if form.validate_on_submit():
        #分词
        content = form.content.data
        fw = open('C:/Users/guquan/Desktop/CRF++-0.58/test/testData2.txt', 'w')
        segs = thu1.cut(content, text=True).split(' ')
        for seg in segs:
            spl = seg.split('_')
            fw.write(spl[0] + ' ' + spl[1] + '\n')
        fw.write('\n')
        fw.close()

        #执行CRF
        os.system('C:/Users/guquan/Desktop/CRF++-0.58/crf_test.exe -m C:/Users/guquan/Desktop/CRF++-0.58/test/model01 C:/Users/guquan/Desktop/CRF++-0.58/test/testData2.txt > C:/Users/guquan/Desktop/CRF++-0.58/test/result012.txt')
        
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
                #print result
                strsText = []
                strsTag = []

        for key in result.keys():
            result[key] = '，'.join(result[key]).decode('utf8')

    return render_template('index.html', form=form, name=content, result=result)


if __name__ == '__main__':
    app.run(port=111)
