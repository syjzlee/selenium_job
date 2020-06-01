from django.shortcuts import render
from tmall.tmall_store.goods import Goods
# Create your views here.
import datetime

def get_latest_month(request):
    today = datetime.datetime.today()
    latest_30days = today + datetime.timedelta(days=-30)
    datas = Goods.objects.filter(create_time__lte=today)
    result = {}
    for data in datas:
        if data.create_time in result:
            result[data.create_time]['store_nums'] += 1
            result[data.create_time]['goods_nums'] += data.goods_nums
        else:
            result[data.create_time] = {'store_nums': 1}
            result[data.create_time]['goods_nums'] = data.goods_nums
        # print(data.store_name, data.goods_nums, data.create_time)
    result = sorted(result.items(), key = lambda x: x[0])
    print(result)
    return render(request, 'index.html', locals())