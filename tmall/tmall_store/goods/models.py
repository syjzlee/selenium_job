from django.db import models


class Goods(models.Model):
    store_name = models.CharField(max_length=128, verbose_name='店铺名')
    goods_nums = models.PositiveIntegerField(default=1, verbose_name='相关商品数量')
    create_time = models.DateField(auto_now_add=True, verbose_name='创建日期')

    class Meta:
        db_table = 'goods'
        verbose_name = '店铺每日商品数量'
        verbose_name_plural = '店铺每日商品数量'
        unique_together = ("store_name", "create_time")
