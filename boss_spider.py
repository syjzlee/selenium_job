import os
import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from lxml import etree
import pymysql
import datetime
from address_parse import add_parse

def qiancheng_spider():
    stop_flag = False
    conn = pymysql.connect(host='*', port=*, user='*', password='*', database='*')
    cursor = conn.cursor()
    last_date = datetime.datetime.now().date()

    # 获取当前库里的job_url_list (这边后续需要修改应该是在招聘的job)
    # sql1 = """select job_url from jobs"""
    sql1 = """select job_url from jobs where job_status!='职位已关闭' and source=5"""
    cursor.execute(sql1)
    job_url_list = [i[0] for i in cursor.fetchall()]

    keyword = 'python'
    base_url = 'https://www.51job.com/'
    option = ChromeOptions()
    # # 不加载图片,加快访问速度
    # option.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    brower = webdriver.Chrome(options=option, executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver')
    time.sleep(2)
    url = 'https://search.51job.com/list/070200,000000,0000,00,9,99,{0},2,1.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='.format(keyword)
    brower.get(url)
    time.sleep(2)
    html = brower.page_source

    for i in range(10):
        i += 1
        res = etree.HTML(html)
        try:
            next_url = res.xpath("//*[@class='bk'][2]/a/@href")[0]
        except:
            next_url = None
        # todo  记录下企查查的网站链接， 能查到公司名称。
        # todo 两个数据库，job-公司名,  记录名应该还有search_keyword  创建时间  以及 updatetime， black黑名单系统, source源数据来源
        jobs = res.xpath("//div[@class='dw_table']//div[@class='el']")
        for job in jobs:
            try:
                result = {}
                result['job_url'] = job.xpath('./p[1]/span/a/@href')[0]
                month = job.xpath("./span[4]/text()")[0].split('-')[0]
                day = job.xpath("./span[4]/text()")[0].split('-')[1]
                create_time = datetime.datetime.now()
                # create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                stf_create_time = str(create_time.year) + '-' + str(month) + '-' + str(day) + ' ' + str(
                    create_time.time())[:8]
                create_time = datetime.datetime.strptime(stf_create_time, "%Y-%m-%d %H:%M:%S")
                if create_time.date() > last_date:
                    stop_flag = True
                    break  # 当发布日期大于上一个以后，说明已经是智能排序之外的了，基本不符合搜索关键词，停止爬取
                last_date = create_time.date()
                # todo  增加判断，URL已经存在的话跳过
                if result['job_url'] in job_url_list:
                    job_url_list.remove(result['job_url'])
                    continue
                result['title'] = job.xpath("./p[1]/span/a/text()")[0].strip()
                result['salary'] = job.xpath("./span[3]/text()")[0]
                result['location'] = job.xpath("./span[2]/text()")[0]
                result['company_url'] = job.xpath('./span[1]/a/@href')[0]
                result['company_name'] = job.xpath('./span[1]/a/text()')[0]
                """job详情页"""
                brower.get(result['job_url'])  # 跳转到详情页
                time.sleep(1)
                detail_html = brower.page_source
                detail_res = etree.HTML(detail_html)
                result['work_experience'] = detail_res.xpath("//p[@class='msg ltype']/text()[2]")[0].strip()
                result['degree'] = detail_res.xpath("//p[@class='msg ltype']/text()[3]")[0].strip()
                company_classification = detail_res.xpath('//div[@class="com_tag"]/p[3]/@title')[0]
                finance = detail_res.xpath('//div[@class="com_tag"]/p[1]/@title')[0]
                company_size = detail_res.xpath('//div[@class="com_tag"]/p[2]/@title')[0]
                result['company_resume'] = company_classification + '|' + finance + '|' + company_size
                result['job-status'] = '招聘中'  # 不知道什么时候算招聘结束
                try:
                    result['job-tags'] = '|'.join(
                        detail_res.xpath("//div[@class='jtag']/div/span/text()"))
                except Exception as err:
                    print('该job没有该标签URL', result['job_url'])
                    result['job-tags'] = '五险一金' + '|' + '双休'
                result['other-jobs'] = detail_res.xpath("//div[@class='tBorderTop_box']/a/@href")[0]
                result['job-sec'] = ('\n').join(
                    [x.strip() for x in detail_res.xpath("//div[@class='bmsg job_msg inbox']/p//text()")])
                result['work_location'] = detail_res.xpath("//div[@class='bmsg inbox']/p/text()")[0]

                # 获取经纬度
                (lng, lat) = add_parse(result['work_location'])  # 只解析南京的

                """"公司详情页，暂时没写，日后从job表里去统一获取"""
                # 这边需要加判断，已经存在的公司不去更新。
                print(lng, lat, result)
                job_sql = """insert into jobs(keyword,job_url,title,salary,location,work_location,work_experience,degree,company_url,
                    company_name,company_resume,job_status,other_jobs,job_sec,create_time,update_time,black,job_tags,source,lng,lat) values('{0}','{1}','{2}','{3}',
                     '{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}','{14}','{15}',{16},'{17}',{18},{19},{20})""".format(
                    keyword, result['job_url'], result['title'],
                    result['salary'], result['location'], result['work_location'], result['work_experience'],
                    result['degree'], result['company_url'],
                    result['company_name'], result['company_resume'], result['job-status'], result['other-jobs'],
                    result['job-sec'],
                    create_time, create_time, 0, result['job-tags'], 5, lng, lat)
                company_sql = """insert into company(company_name,company_url) values('{0}','{1}')""".format(
                    result['company_name'],
                    result['company_url'])
                try:
                    cursor.execute(job_sql)
                    conn.commit()
                except Exception as err:
                    print('Job已存在{0}'.format(result['job_url']), err)
                try:
                    cursor.execute(company_sql)
                    conn.commit()
                except BaseException as err:
                    print('公司已存在{0}'.format(result['company_url']), err)
            except Exception as err:
                print(result['job_url'], "该页面元素不完整或有错误无法爬取")
        # 继续访问下个job_list页面
        if stop_flag:
            break
        if next_url:
            brower.get(next_url)
            html = brower.page_source
        else:
            break

    # 对不在boss里的职位进行查看, 本来的逻辑应该是不在现有库里说明boss下架该职位了（职位已关闭），但是实际情况是有些职位boss现在没有了，但是它仍在招聘中。
    for job_url in job_url_list:
        try:
            brower.get(job_url)  # 跳转到详情页
            time.sleep(2)
            detail_html = brower.page_source
            detail_res = etree.HTML(detail_html)
            if not detail_res.xpath("//div[@class='research']/p/text()"):
                print('未发生变动', job_url)
                continue
            if '很抱歉' in detail_res.xpath("//div[@class='research']/p/text()")[0]:
                job_status = '职位已关闭'
                update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                update_sql = """update jobs set update_time='{0}',job_status='{1}' where job_url='{2}'""".format(
                    update_time, job_status, job_url)
                print(update_sql)
                cursor.execute(update_sql)
                conn.commit()
        except:
            print("该页面已删除，无法打开该页面:{0}".format(job_url))
            job_status = '职位已关闭'
            update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_sql = """update jobs set update_time='{0}',job_status='{1}' where job_url='{2}'""".format(
                update_time, job_status, job_url)
            print(update_sql)
            cursor.execute(update_sql)
            conn.commit()
            continue

    conn.close()
    brower.close()

def boss_spider():
    conn = pymysql.connect(host='106.54.126.210', port=3306, user='kiven', password='kiven', database='jobs')
    cursor = conn.cursor()


    # 获取当前库里的job_url_list (这边后续需要修改应该是在招聘的job)
    # sql1 = """select job_url from jobs"""
    sql1 = """select job_url from jobs where job_status!='职位已关闭' and source=1"""
    cursor.execute(sql1)
    job_url_list = [i[0] for i in cursor.fetchall()]

    keyword = 'python'
    base_url = 'https://www.zhipin.com'
    # 开启远程调试模式
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    # brower = webdriver.Chrome(executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver", chrome_options=chrome_options)
    option = ChromeOptions()
    # # 不加载图片,加快访问速度
    option.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    brower = webdriver.Chrome(options=option, executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver')
    time.sleep(2)
    url = 'https://www.zhipin.com/job_detail/?query={0}&city=101190100&industry=&position='.format(keyword)
    brower.get(url)
    time.sleep(2)
    html = brower.page_source

    for i in range(10):
        i += 1
        res = etree.HTML(html)
        try:
            next_url = res.xpath("//a[@class='next']/@href")[0]
            next_url = base_url + next_url
        except:
            next_url = None
        # todo  记录下企查查的网站链接， 能查到公司名称。
        # todo 两个数据库，job-公司名,  记录名应该还有search_keyword  创建时间  以及 updatetime， black黑名单系统
        jobs = res.xpath("//div[@class='job-primary']")
        for job in jobs:
            result = {}
            result['job_url'] = job.xpath('./div[1]/h3/a/@href')[0]
            # result['job_url'] = base_url + result['job_url']
            # todo  增加判断，URL已经存在的话跳过
            if result['job_url'] in job_url_list:
                job_url_list.remove(result['job_url'])
                continue
            result['title'] = job.xpath("./div[1]/h3/a/div[1]/text()")[0]
            result['salary'] = job.xpath("./div[1]/h3/a/span/text()")[0]
            # result['work_explain_list'] = job.xpath("//div[@class='detail-bottom-text']/text()")   # 删除， 很多为空
            result['location'] = job.xpath("./div[1]/p[1]/text()[1]")[0]
            result['work_experience'] = job.xpath("./div[1]/p[1]/text()[2]")[0]
            result['degree'] = job.xpath("./div[1]/p[1]/text()[3]")[0]

            result['company_url'] = job.xpath('./div[2]/div[1]/h3[1]/a/@href')[0]
            # result['company_url'] = base_url + result['company_url']
            result['company_name'] = job.xpath('./div[2]/div[1]/h3[1]/a/text()')[0]
            result['company_resume'] = ('|').join(job.xpath('./div[2]/div[1]/p/text()'))  # 替代以下的三条描述，因为有部分公司没有融资描述
            # result['company_classification'] = job.xpath('./div[2]/div[1]/p/text()[1]')[0]
            # result['finance'] = job.xpath('./div[2]/div[1]/p/text()[2]')[0]
            # result['company_size'] = job.xpath('./div[2]/div[1]/p/text()[3]')[0]
            """job详情页"""
            brower.get(base_url + result['job_url'])   # 跳转到详情页
            time.sleep(2)
            detail_html = brower.page_source
            detail_res = etree.HTML(detail_html)
            result['job-status'] = detail_res.xpath("//div[@class='job-status']/text()")[0]
            result['job-tags'] = '|'.join(detail_res.xpath("//div[@class='job-banner']//div[@class='tag-all job-tags']/span/text()"))
            result['other-jobs'] = detail_res.xpath("//a[@class='link-more']/@href")[0]
            # result['other-jobs'] = base_url + result['other-jobs']
            result['job-sec'] = ('\n').join([x.strip() for x in detail_res.xpath("//div[@class='detail-content']/div[1]/div[1]/text()")])
            result['work_location'] = detail_res.xpath("//div[@class='location-address']/text()")[0]

            #获取经纬度
            (lng, lat) = add_parse(result['work_location'])

            """"公司详情页，暂时没写，日后从job表里去统一获取"""
            # 这边需要加判断，已经存在的公司不去更新。
            print(lng,lat, result)
            create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            job_sql = """insert into jobs(keyword,job_url,title,salary,location,work_location,work_experience,degree,company_url,
            company_name,company_resume,job_status,other_jobs,job_sec,create_time,update_time,black,job_tags,source,lng,lat) values('{0}','{1}','{2}','{3}',
             '{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}','{14}','{15}',{16},'{17}',{18},{19},{20})""".format(keyword, result['job_url'], result['title'],
             result['salary'],result['location'],result['work_location'],result['work_experience'],result['degree'],result['company_url'],
             result['company_name'],result['company_resume'],result['job-status'],result['other-jobs'], result['job-sec'],
             create_time, create_time, 0, result['job-tags'], 1, lng, lat)
            company_sql = """insert into company(company_name,company_url) values('{0}','{1}')""".format(result['company_name'],
                             result['company_url'])
            try:
                cursor.execute(job_sql)
                conn.commit()
            except Exception as err:
                print('Job已存在{0}'.format(result['job_url']), err)
            try:
                cursor.execute(company_sql)
                conn.commit()
            except BaseException as err:
                print('公司已存在{0}'.format(result['company_url']), err)
        # 继续访问下个job_list页面
        if next_url:
            brower.get(next_url)
            html = brower.page_source
        else:
            break


    print(job_url_list)
    # 对不在boss里的职位进行查看, 本来的逻辑应该是不在现有库里说明boss下架该职位了（职位已关闭），但是实际情况是有些职位boss现在没有了，但是它仍在招聘中。
    for job_url in job_url_list:
        try:
            brower.get(base_url + job_url)  # 跳转到详情页
            time.sleep(2)
            detail_html = brower.page_source
            detail_res = etree.HTML(detail_html)
            job_status = detail_res.xpath("//div[@class='job-status']/text()")[0]
            sql = """select job_status from jobs where job_url='{0}'""".format(job_url)
            cursor.execute(sql)
            db_job_status = cursor.fetchall()[0][0]
            if job_status == db_job_status:
                print("该职位未发生变化且没有关闭",job_url)
                continue
            update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_sql = """update jobs set update_time='{0}',job_status='{1}' where job_url='{2}'""".format(
                update_time, job_status, job_url)
            print(update_sql)
            cursor.execute(update_sql)
            conn.commit()
        except:
            print("没有该页面:{0}".format(base_url+job_url))
            continue



    conn.close()
    brower.close()



if __name__ == '__main__':
    while True:
        try:
            hour = datetime.datetime.now().hour
            if hour == 9:
                print("BOSS直聘开始爬取......")
                boss_spider()
                print("BOSS直聘爬取结束......\n\n")
                print("前程无忧开始爬取......")
                qiancheng_spider()
                print("前程无忧爬取结束......")
                time.sleep(3600 * 24)
            else:
                print(datetime.datetime.now())
                time.sleep(60*60)
        except Exception as err:
            time.sleep(60*60)
            print(err)