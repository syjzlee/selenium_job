# -*- coding: utf-8 -*-
import time
import os
import random

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pymysql
import datetime

db = pymysql.connect("localhost", "root", "ljp310851649.", "tmall_store")
cursor = db.cursor()
count_perstore = list()

class tm_login:
    def __init__(self, webdriver_path):
        url = 'https://login.m.taobao.com/login.htm?loginFrom=wap_tmall&assets_js=mui%2Ffeloader%2F4.0.22%2Ffeloader-min.js,mui%2Ftmapp-standalone%2F4.0.3%2Fseed.js,mui%2Ftmapp-standalone%2F4.0.3%2Flogin-download.js&assets_css=3.0.8%2Fmobile%2Ftmallh5.css&redirectURL=https%3A%2F%2Fwww.tmall.com'
        self.url = url
        self.page_limit = 20
        self.current_href = ''

        # options = webdriver.ChromeOptions()
        #options.add_experimental_option('excludeSwitches', ['enable-automation'])  #开发者模式
        # options.add_experimental_option('useAutomationExtension', False)
        # options.add_argument('--user-data-dir=E:/项目整理/tmall/User Data')

        '''驱动位置'''
        # self.browser = webdriver.Chrome(executable_path=webdriver_path, options=options)
        self.browser = webdriver.Chrome(executable_path=webdriver_path)
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })
        self.wait = WebDriverWait(self.browser, 10)  # 超时时长10s

    # 登录tb重定向tm
    def login(self):
        self.browser.maximize_window()
        self.browser.get(self.url)

        user = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="fm-login-id"]')))
        user.click()
        user.clear()
        user.send_keys(username)

        pwd = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="fm-login-password"]')))
        pwd.click()
        pwd.clear()
        pwd.send_keys(password)

        submit = self.wait.until(EC.presence_of_element_located((By.XPATH, '//button[@class="fm-button fm-submit password-login"]')))
        submit.click()

        try:
            self.browser.find_element_by_xpath('//button[@class="login-error-dialog-ok-btn"]').click()
        except Exception:
            pass

        time.sleep(1)
        button = self.browser.find_element_by_id('nc_1_n1z')  # 滑块
        action = ActionChains(self.browser)  # action对象
        action.click_and_hold(button).perform()
        action.reset_actions()
        action = action.move_by_offset(1883, 0)
        action.perform()  # 移动滑块, 这边不同电脑需要修改
        # TODO   1. 修改屏幕滑块分辨率配置  2. 读取配置文件配置
        time.sleep(1)
        submit = self.wait.until(EC.presence_of_element_located((By.XPATH, '//button[@class="fm-button fm-submit password-login"]')))
        submit.click()


    def search_data(self):
        try:
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="s-combobox-input-wrap"]/input'))).click()
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="s-combobox-input-wrap"]/input'))).send_keys('宠物航空箱')
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mallSearch"]/form/fieldset/div/button'))).click()
            time.sleep(2)
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//a[@class="fType-w "]'))).click()
            time.sleep(2)

            div_list = self.browser.find_elements_by_xpath('//*[@id="J_ItemList"]/div')

            for div in div_list:
                shop_name = div.find_element_by_xpath('.//div[@class="shopHeader-info"]/a').text
                count = div.find_element_by_xpath('.//div[@class="shopHeader-enter"]/a[2]/em').text
                if (shop_name + '    ' + count) in count_perstore:
                    continue
                count_perstore.append(shop_name + '    ' + count)
                try:
                    sql = "INSERT INTO goods VALUES (NULL,'{0}',{1},'{2}')".format(shop_name, count, str(datetime.datetime.today())[:10])
                    cursor.execute(sql)
                    db.commit()
                except Exception as Err:
                    print(Err)
            print(count_perstore[-20:-1])

            if self.browser.find_element_by_xpath("//a[text()='下一页>>']").get_attribute('href'):
                self.current_href = self.browser.find_element_by_xpath("//a[text()='下一页>>']").get_attribute('href')
                print(self.current_href)
                self.browser.get(self.current_href)
                self.page_limit -= 1
                self.show_data()
        except Exception:
            self.huakuai_pass()
            self.search_data()

    def show_data(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="J_ItemList"]/div')))
            div_list = self.browser.find_elements_by_xpath('//*[@id="J_ItemList"]/div')

            for div in div_list:
                shop_name = div.find_element_by_xpath('.//div[@class="shopHeader-info"]/a').text
                count = div.find_element_by_xpath('.//div[@class="shopHeader-enter"]/a[2]/em').text
                if (shop_name + '    ' + count) in count_perstore:
                    continue
                count_perstore.append(shop_name + '    ' + count)
                try:
                    sql = "INSERT INTO goods VALUES (NULL,'{0}',{1},'{2}')".format(shop_name, count, str(datetime.datetime.today())[:10])
                    cursor.execute(sql)
                    db.commit()
                except Exception as Err:
                    print(Err)
            print(count_perstore[-20:-1])
            time.sleep(random.choice(range(30, 60)))
            self.page_limit -= 1
            if self.page_limit > 0:
                self.random_nextpage_choice()
                self.show_data()
        except Exception:
            self.huakuai_pass()
            self.show_data()

    def random_nextpage_choice(self):
        # choice = random.choice((1, 2, 3))
        choice = 2

        if choice == 1:
            print('点击箭头翻页')
            self.browser.find_element_by_xpath("//*[@class='ui-page-s']//a[text()='>']").click()
        elif choice == 2 and self.browser.find_element_by_xpath("//a[text()='下一页>>']").get_attribute('href'):
            print('点击下一页翻页')
            self.current_href = self.browser.find_element_by_xpath("//a[text()='下一页>>']").get_attribute('href')
            print(self.current_href)
            # self.current_href = self.browser.find_element_by_xpath("//*[@class='ui-page-s']//a[text()='>']").get_attribute('href')
            self.browser.get(self.current_href)


    def huakuai_pass(self):
        while ('亲，小二正忙，滑动一下马上回来' in self.browser.page_source):
            loop_nums = 1
            try:
                huakuai = self.browser.find_element_by_id('nc_1_n1z')  # 滑块
                track_list = []
                track_list = self.move_to_gap(huakuai, self.get_track(258))
            except Exception as err:
                time.sleep(0.5)
            try:
                if self.browser.find_element_by_xpath('//*[@id="nocaptcha"]/div/span/a').get_attribute('href'):
                    # self.browser.find_element_by_xpath('//*[@id="nocaptcha"]/div/span/a').click()
                    with open('./fail.txt', 'a') as f:
                        f.write(str(track_list) + '\n')
                    time.sleep(loop_nums + 10)
                    loop_nums += 1
                    self.browser.refresh()
                else:
                    with open('./success.txt', 'a') as f:
                        f.write(str(track_list) + '\n')
            except:
                pass
            # time.sleep(60)
            if not self.current_href:
                self.current_href = 'https://www.tmall.com/'
            print('刷新页面： ' + self.current_href)
            # self.browser.get(self.current_href)
            #self.browser.refresh()
            # time.sleep(2)

        time.sleep(15)

    # def get_track(self, distance):  # distance为传入的总距离
    #     # 移动轨迹
    #     track = []
    #     # 当前位移
    #     current = 0
    #     # 减速阈值
    #     # mid = distance * 5 / 5
    #     # 计算间隔
    #     t = 0.2
    #     # 初速度
    #     v = 0
    #     a = 4
    #
    #     while current < distance:
    #         # if current < mid:
    #         #     # 加速度为2
    #         #     a = 4
    #         # else:
    #         #     # 加速度为-2
    #         #     a = -4
    #         if current >= distance * 3/2 and v > 0:
    #             a = -10
    #         v0 = v
    #         # 当前速度
    #         v = v0 + a * t
    #         # 移动距离
    #         move = v0 * t + 1 / 2 * a * t * t
    #         # 当前位移
    #         current += move
    #         # 加入轨迹
    #         track.append(round(move))
    #     # track.append(distance)
    #     return track

    def get_track(seflf, distance):  # distance为传入的总距离
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        # mid = distance * 5 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0
        a = 4
        flag = 0

        while current < distance:
            # if current < mid:
            #     # 加速度为2
            #     a = 4
            # else:
            #     # 加速度为-2
            #     a = -4
            if current >= 205 and current < 235 and track[-1] > 0 and not flag:
                a = -50
            elif current >= distance * 1 / 2 and track[-2] == 0:
                flag = 1
                a = 20
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            if move < 0:
                move = 0
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def move_to_gap(self, slider, tracks):  # slider是要移动的滑块,tracks是要传入的移动轨迹
        action = ActionChains(self.browser)
        action.click_and_hold(slider).perform()
        track_list = []
        try:
            # for x in tracks:
            #     track_list.append(x)
            #     action = action.move_by_offset(xoffset=x, yoffset=0)
            #     if x == 0:
            #         action.pause(0.18)
            action.move_by_offset(xoffset=258, yoffset=random.uniform(-2, 2))
            action.perform()
            time.sleep(0.5)
            return track_list
        except Exception as err:
            print(err)
            return track_list

if __name__ == "__main__":

    username = "*****"  # user
    password = "******"  # pwd
    current_path = os.path.dirname(os.path.abspath(__file__))
    webdriver_path = current_path + '\chromedriver.exe'
    print(webdriver_path)

    login = tm_login(webdriver_path)
    login.login()  # 登录
    login.search_data()
    print(count_perstore)

