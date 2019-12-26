# encoding:utf-8
import requests
import time
import json
import re

# 此处需要ak，ak申请地址：https://lbs.amap.com/dev/key/app
ak = "zILU7LMjZwrzEAynY2bp1xLeIMF4iBqy"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
}


# 地理信息解析
def add_parse(addr=None):
    # url = 'http://api.map.baidu.com/geocoding/v3/?address=北京市海淀区上地十街10号&output=json&ak=您的ak&callback=showLocation'
    url = 'http://api.map.baidu.com/geocoding/v3/'
    params = {"output": 'json',
              "address": addr,
              "ak":ak,
              "callback": 'showLocation',
              "city": '南京市'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        response = re.findall('location":(.*?),"precise', response.text, re.I)[0]
        dic = json.loads(response)
        lat = dic['lat']
        lng = dic['lng']
        return lng,lat
    else:
        return None,None,

if __name__ =='__main__':
    (lng,lat) = add_parse("南京雨花台区德讯科技大厦5楼")
    print(type(lng))
    print(lng,lat)
    print('{0},{1}'.format(lng,lat))