import random
from concurrent.futures import ThreadPoolExecutor, wait
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
from selenium.webdriver import ActionChains
from lxml import etree
import requests
import re

header = {
    "user-agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0",
    'Connection': 'close',
    "Accept-Encoding": "Gzip",
}
api_url = "https://dps.kdlapi.com/api/getdps/?orderid=998712121111062&num=3&signature" \
          "=fa8xv25ud1o8v5lzw6bk368cytc0pf9t&pt=1&format=json&sep=1 "
api_url2 = "https://dps.kdlapi.com/api/getdps/?orderid=998712121111062&num=1&signature" \
           "=fa8xv25ud1o8v5lzw6bk368cytc0pf9t&pt=1&format=json&sep=1 "

proxy_ip = requests.get(api_url).json()['data']['proxy_list']


def auto_login(area, keyword, url, page):
    province = area['province']
    city = area['city']
    option = ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(executable_path=r'chromedriver.exe', options=option)
    driver.get(url)
    driver.implicitly_wait(10)
    sleep(1)
    driver.find_element_by_xpath('//*[@id="alibar"]/div[1]/div[2]/ul/li[3]/a').click()
    driver.implicitly_wait(20)
    driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="loginchina"]/iframe'))
    sleep(1)
    # 选择扫码登录,可以拿手机直接扫selenium打开的网站 等待时间4秒，五秒后刷新网站，等待三秒等网站刷新
    driver.find_element_by_xpath('//div[@id="login"]/div[1]/i').click()
    sleep(4)
    driver.refresh()
    driver.implicitly_wait(10)
    sleep(2)
    # 选择搜索关键词
    driver.find_element_by_xpath('//*[@id="home-header-searchbox"]').send_keys(keyword)
    driver.find_element_by_xpath("//div[@class='alisearch-action']/button").click()
    sleep(2)
    driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
    # 选择供应商
    driver.find_element_by_xpath(
        '//*[@id="render-engine-page-container"]/div/div[2]/div/div[3]/div[1]/div/span[3]/a/span').click()
    sleep(1)
    input = driver.find_element_by_xpath('//*[@id="q"]')
    # 刷新
    input.send_keys(Keys.ENTER)
    sleep(1)
    # 选择省份城市
    area = driver.find_element_by_xpath("//li[@id='sw_mod_filter_area']")
    ActionChains(driver).move_to_element(area).perform()
    province = driver.find_element_by_link_text(province)
    ActionChains(driver).move_to_element(province).perform()
    driver.find_element_by_link_text(city).click()
    driver.implicitly_wait(10)
    sleep(1)
    count = 1
    # 打开文件做个标记
    with open('temp.txt', 'w', encoding='utf-8') as f:
        f.write('---------------------------------------')
    while count <= page:
        print('开始解析第%s页数据' % count)
        count += 1
        sleep(3)
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        old_url = driver.current_url
        driver.implicitly_wait(10)
        sleep(1)
        c = driver.get_cookies()
        cookies = {}
        # 获取cookie中的name和value,转化成requests可以使用的形式
        for cookie in c:
            cookies[cookie['name']] = cookie['value']
        page_text = driver.page_source
        executor = ThreadPoolExecutor(3)
        urls_list = prase_urls(page_text)
        url_dict = {}
        url_dict['cookies'] = cookies
        for detail_url in urls_list:
            executor.submit(get_page, detail_url, cookies).add_done_callback(parase_info)
        executor.shutdown(wait=True)
        print('-------------------------------------------')
        driver.find_element_by_xpath('//*[@id="jumpto"]').send_keys(count)
        sleep(0.5)
        driver.find_element_by_xpath('//*[@id="jump-sub"]').click()
        driver.refresh()
        new_url = driver.current_url
        # 页面没有跳转 尝试重新刷新
        while new_url == old_url:
            driver.find_element_by_xpath('//*[@id="jumpto"]').send_keys(count)
            sleep(0.5)
            driver.find_element_by_xpath('//*[@id="jump-sub"]').click()
            driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            new_url = driver.current_url

    # else:
    #     driver.quit()


def prase_urls(page_text):
    tree = etree.HTML(page_text)
    url_list = tree.xpath('//*[@id="sw_mod_searchlist"]/ul/li/div[1]/div[2]/div[1]/a[1]/@href')
    for i in [3, 4, 5]:
        del url_list[i]

    return url_list


def get_page(start_url, cookies):
    ip = random.choice(proxy_ip)
    try:
        response = requests.get(url=start_url + '/page/contactinfo.htm', headers=header,
                                proxies={"http": ip}, cookies=cookies).text
        sleep(random.randint(1, 3))
    except Exception as e:
        response = ' '
        print(e)
    return {'url': url, 'text': response}


def parase_info(result):
    res = result.result()
    page_text = res.get('text')
    try:
        if page_text:
            tree = etree.HTML(page_text)
            company_name = tree.xpath('//*[@id="site_content"]/div[1]/div/div/div/div[2]/div/div[1]/div[1]/h4/text()')
            company_member_name = tree.xpath('//*[@id="site_content"]/div[1]/div/div/div/div[2]/div/div[1]/div['
                                             '1]/dl/dd//text()')
            compang_phone = tree.xpath(
                '//*[@id="site_content"]/div[1]/div/div/div/div[2]/div/div[1]/div[2]/div[2]/dl[1]/dd/text()')
            compang_mobilephone = tree.xpath('//*[@id="site_content"]/div[1]/div/div/div/div[2]/div/div[1]/div[2]/div['
                                             '2]/dl[2]/dd/text()')
            if len(company_name) > 0:
                company_name = company_name[0]
                company_member_name = company_member_name[1] + ''.join(company_member_name[2].split())
                rule = re.compile(r'^\d')
                if len(compang_mobilephone) > 0:
                    compang_mobilephone = compang_mobilephone[0].strip(' ').strip('\n')
                    if rule.match(compang_mobilephone[0:1]) is None:
                        compang_mobilephone = ''
                else:
                    compang_mobilephone = ''

                if len(compang_phone) > 0:
                    compang_phone = compang_phone[0].strip(' ').strip('\n')
                    if rule.match(compang_phone[0:1]) is None:
                        compang_phone = ''
                else:
                    compang_phone = ''
                if len(compang_mobilephone) > 0 or len(compang_phone) > 0:
                    print('%s|%s|%s|%s' % (company_name, company_member_name, compang_mobilephone, compang_phone))
                    with open('temp.txt', 'a', encoding='utf-8') as f:
                        f.write('%s|%s|%s|%s' % (company_name, company_member_name, compang_mobilephone, compang_phone))
    except Exception as e:
        print(e)


# 搜索关键词
keyword = '夏装女短裙'
# 搜索省份 城市
area = {'province': '湖北', 'city': '武汉'}
url = 'https://www.1688.com/'
# 爬取页面数量
page = 20
# 开爬
auto_login(area, keyword, url, page)
