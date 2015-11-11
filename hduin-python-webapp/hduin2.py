#! /usr/bin/python
# -*- coding: utf-8 -*-
import requests, sys, time, re, urllib, os
from mysql_lib import MysqlHelper

reload(sys)  
sys.setdefaultencoding('utf8') 

s = requests.session()

base_header = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate",
}
main_url = ""

def method_get(url, headers=None):
    header = base_header
    for ex in headers:
        header[ex] = headers[ex]
    r = s.get(url, headers=header)
    return r

def method_post(url, data, headers=None):
    header = base_header
    header["Content-Type"] = "application/x-www-form-urlencoded"
    for ex in headers:
        header[ex] = headers[ex]
    r = s.post(url, headers=header, data=urllib.urlencode(data))
    return r 

def login (stu_id, password):
    global main_url
    enter_header = {
        "Host":"cas.hdu.edu.cn",
        "Referer": "http://jxgl.hdu.edu.cn/logout0.aspx",
    }
    enter_url = 'http://cas.hdu.edu.cn/cas/login?service=http://jxgl.hdu.edu.cn/index.aspx'
    enter_r = method_get(enter_url, headers=enter_header)
    LT = re.search(r'<input type="hidden" name="lt" value="(.*?)" />',enter_r.text,re.S)
    lt = LT.group(1)

    login_data = {
        "encodedService":"http%3a%2f%2fjxgl.hdu.edu.cn%2findex.aspx",
        "service":"http://jxgl.hdu.edu.cn/index.aspx",
        "serviceName":"null",
        "loginErrCnt":'0',
        "username":stu_id,
        "password":password,
        "lt":lt,
    }

    login_header = {
        "Referer":"http://cas.hdu.edu.cn/cas/login"
    }
    login_url = "http://cas.hdu.edu.cn/cas/login"
    login_r = method_post(login_url,data=login_data,headers=login_header)

    auth_header = {
        'Host':'jxgl.hdu.edu.cn',
        'Referer':'http://cas.hdu.edu.cn/cas/login'
        }
    auth_url =login_r.headers['cas-service']+'?ticket='+login_r.headers['cas-ticket']
    method_get(auth_url, headers=auth_header)

    main_url = 'http://jxgl.hdu.edu.cn/xs_main.aspx?xh='+stu_id
    main_header = auth_header
    main_header['Referer'] = auth_url
    main_r = s.get(main_url, headers=main_header)
    return main_r

def req_score (url, req_data=None):
    header = {
        'Host':'jxgl.hdu.edu.cn',
        'Referer':main_url
    }
    r = method_get(url, header)
    input_reg = re.compile(r'<input type="hidden" name="(.*?)" id=".*?" value="(.*?)" />', re.S)
    inputs = input_reg.findall(r.text)
    inputs_data = {}
    for input in inputs:
        inputs_data[input[0]] = input[1]
    for key in req_data:
        inputs_data[key] = req_data[key]
    input_header = {
        'Host':'jxgl.hdu.edu.cn',
        'Referer': url
    }
    input_r = method_post(url, headers=input_header, data=inputs_data)
    return input_r.text

def get_score(stu_id, start_year, end_year):
    score_url = 'http://jxgl.hdu.edu.cn/xscjcx_dq.aspx?xh=12051602&xm=程泱洋&gnmkdm=N121605'
    list_reg = re.compile(r'(<table class="datelist".*?</table>)', re.S)
    req_data = {}
    tr_res = []
    for xn in range(start_year,end_year+1):
        for xq in xrange(1,3):
            req_data['ddlxn'] = str(xn) + '-' + str(xn+1)
            req_data['ddlxq'] = str(xq)
            req_data['btnCx'] = '+²é++Ñ¯+'      
            res = req_score(score_url,req_data)
            html = list_reg.search(res).group(1)
            tr_reg = re.compile(r'<tr[^d]*?>(.*?)</tr>', re.S)
            tr_res.extend(tr_reg.findall(html))
    for trs in tr_res:
        tr = trs.strip().replace('<td>','').replace('&nbsp;','').split('</td>')
        conn.insert('insert into score values (%s,%s,%s,%s,%s,%s,%s)', [stu_id,tr[0],tr[1],tr[2],tr[7],tr[8],tr[9]])
        conn.insert('insert into course values (%s,%s,%s,%s,%s,%s)',[tr[2],tr[3],tr[4],tr[5],tr[6],tr[10]])

if __name__ == "__main__":
    conf = os.path.abspath('.')+os.sep+'mysql_conf'
    with open(conf, 'r') as f:
        content = f.readlines()

    conn = MysqlHelper(content[0],content[1],content[2])
    conn.create('score','(stu_id varchar(20), xn varchar(20), xq varchar(1), c_id varchar(20), score varchar(8), re_score varchar(8), is_retake tinyint(1))')
    conn.create('course','(c_id varchar(20) primary key, c_name varchar(100), c_type varchar(20), c_parent varchar(20), c_credit float, c_ins varchar(20))')

    # stu_id = '12051602'
    # pwd = 'aeef1d58d33ce786a5470678ca5c7d61'    
    print "输入学号："
    stu_id = raw_input()
    print "输入密码："
    pwd = raw_input()

    start_year = int('20'+stu_id[0:2])
    end_year = int(time.strftime("%Y"))
    login(stu_id, pwd)
    print "登录成功."
    get_score(stu_id, start_year, end_year)
    print "成绩获取成功."