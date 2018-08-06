from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unicodedata
import urllib.request
from time import sleep
import csv
from datetime import datetime, timedelta
import os
import multiprocessing as mp
#from joblib import Parallel, delayed
import threading
import re

def is_japanese(string):
    for s in string:
        name = unicodedata.name(s)
        print(name)
        if "CJK UNIFIED" in name or "HIRAGANA" in name or "KATAKANA" in name:
            return True
    return False
def download(link,savename):
    urllib.request.urlretrieve(link,savename)
    urllib.request.urlcleanup()

class multidownload(threading.Thread):

    def __init__(self,value,home,year,submode,point,mode):
        threading.Thread.__init__(self)
        self.value = value
        self.home = home
        self.year = year
        self.sub_mode = submode
        self.point = point
        self.mode = mode

    def run(self):
        #chromeOptions = webdriver.ChromeOptions()
        #chromeOptions.add_argument('--headless')
        chromeOptions.add_argument('--disable-application-cache')
        chromeOptions.add_argument('--disk-cache-size=0')
        driver = webdriver.Chrome(executable_path = driver_path,chrome_options = chromeOptions)
        driver.get(self.home)
        sleep(0.3)
        Byear_element = driver.find_element_by_name("BYEAR")
        Byear_element.clear()
        Byear_element.send_keys(str(self.year))
        BMON_element = driver.find_element_by_name("BMON")
        BMON_element.clear()
        BMON_element.send_keys("01")

        Ayear_element = driver.find_element_by_name("AYEAR")
        Ayear_element.clear()
        Ayear_element.send_keys(str(self.year))
        AMON_element = driver.find_element_by_name("AMON")
        AMON_element.clear()
        AMON_element.send_keys("12")
        radio = driver.find_element_by_xpath("//input[@value='" + self.value + "']")
        value = radio.get_attribute('value')
        radio.click()
        driver.find_element_by_name("SUBMIT").click()
        sleep(0.3)
        driver.switch_to.window(driver.window_handles[1])
        linkinfo = driver.find_element_by_xpath('//a[img/@src="/img/download.png"]').get_attribute('href')
        print(linkinfo)
        savename = "./dat/" + self.mode + "/" +  self.point + "_" + self.sub_mode + "_" + self.value + "_" + str(self.year) + ".csv"
        download(linkinfo,savename)
        driver.quit()

class multiexplorer(threading.Thread):

    def __init__(self,start,end,mode,submode,t_start,t_end,rivername,url):
        threading.Thread.__init__(self)
        self.page_start = start
        self.page_end = end
        self.mode = mode
        self.submode = submode
        self.term_start = t_start
        self.term_end = t_end
        self.river = rivername
        self.url = url

    def run(self):
        chromeOptions.add_argument('--disable-application-cache')
        chromeOptions.add_argument('--disk-cache-size=0')
        driver = webdriver.Chrome(executable_path = driver_path,chrome_options = chromeOptions)
        url = self.url + "&PAGES=" + str(self.page_start)
        driver.get(url)
        pages = 0
        datasize = 0
        lists = driver.find_elements_by_xpath("//*[@href]")
        files = os.listdir('dat/' + mode)
        for i in range(self.page_start,self.page_end):
            lists = driver.find_elements_by_xpath("//*[@href]")
            print(len(lists))
            for link in lists:
                if is_japanese(link.text):
                    datasize = datasize + 1
                    print(link.text)
                    if mode == "水質・底質":
                        if not link.text + "_" + self.submode + "_" + "01_2017" + ".csv" in files:
                            link.click()
                            sleep(1)
                            mining(driver,self.mode,self.term_start,self.term_end,link.text,self.submode,files)
                    else:
                        if not link.text + ".csv" in files:
                            link.click()
                            mining(driver,self.mode,self.term_start,self.term_end,link.text,self.submode,files)
                    #link.close()
                if datasize == 10:
                    driver.find_element_by_xpath('//a[img/@src="/img/next.gif"]').click()
                    pages = pages + 1
                    datasize = 0
                    break
                    sleep(1)
            if len(lists) < 12:
                break

        driver.quit()

    #driver.close()

    #for i in range(0,)


def mining(driver,mode,start,end,point,sub_mode,files):
    if mode == "雨量":
        try:
            driver.switch_to.window(driver.window_handles[1])
            sleep(3)
            driver.find_element_by_xpath('//a[img/@src="/img/btn_srch_rain_mon.png"]').click()
            for year in range(start,end+1):
                print("A")
                driver.switch_to.window(driver.window_handles[2])
                sleep(3)
                year_element = driver.find_element_by_name("BYEAR")
                year_element.clear()
                year_element.send_keys(str(year))
                sleep(3)
                for month in range(1, 13):
                    month_element = driver.find_element_by_name("BMON")
                    month_element.clear()
                    month_element.send_keys(str(month).zfill(2))
                    sleep(3)
                    driver.find_element_by_name("SUBMIT").click()
                    sleep(3)
                    driver.switch_to.window(driver.window_handles[3])
                    linkinfo = driver.find_element_by_xpath('//a[img/@src="/img/download.gif"]').get_attribute('href')
                    print(linkinfo)
                    savename = "./dat/" + mode + "/" +  point + "_" + str(year) + "_"+ str(month).zfill(2) + ".csv"
                    urllib.request.urlretrieve(linkinfo,savename)
                    sleep(3)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[2])
        except NoSuchElementException:
            print("skip")
        driver.close()
        driver.switch_to.window(driver.window_handles[1])

    if mode == "水位流量":
        try:
            driver.switch_to.window(driver.window_handles[1])
            sleep(3)
            driver.find_element_by_xpath('//a[img/@src="/img/btn_srch_water_mon.png"]').click()
            for year in range(start,end+1):
                print("A")
                driver.switch_to.window(driver.window_handles[2])
                sleep(3)
                year_element = driver.find_element_by_name("BYEAR")
                year_element.clear()
                year_element.send_keys(str(year))
                sleep(3)
                for month in range(1, 13):
                    month_element = driver.find_element_by_name("BMON")
                    month_element.clear()
                    month_element.send_keys(str(month).zfill(2))
                    sleep(3)
                    driver.find_element_by_name("SUBMIT").click()
                    sleep(3)
                    driver.switch_to.window(driver.window_handles[3])
                    linkinfo = driver.find_element_by_xpath('//a[img/@src="/img/download.gif"]').get_attribute('href')
                    print(linkinfo)
                    savename = "./dat/" + "水位" + "/" +  point + "_"+ str(year) + "_"+ str(month).zfill(2) + ".csv"
                    urllib.request.urlretrieve(linkinfo,savename)
                    sleep(3)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[2])

            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            sleep(3)
        except NoSuchElementException:
            print("skip")
        try:
            driver.find_element_by_xpath('//a[img/@src="/img/btn_srch_ryu_mon.png"]').click()
            for year in range(start,end+1):
                print("A")
                driver.switch_to.window(driver.window_handles[2])
                sleep(3)
                year_element = driver.find_element_by_name("BYEAR")
                year_element.clear()
                year_element.send_keys(str(year))
                sleep(3)
                for month in range(1, 13):
                    month_element = driver.find_element_by_name("BMON")
                    month_element.clear()
                    month_element.send_keys(str(month).zfill(2))
                    sleep(3)
                    driver.find_element_by_name("SUBMIT").click()
                    sleep(3)
                    driver.switch_to.window(driver.window_handles[3])
                    linkinfo = driver.find_element_by_xpath('//a[img/@src="/img/download.gif"]').get_attribute('href')
                    print(linkinfo)
                    savename = "./dat/" + "流量" + "/" +  point + "_"+ str(year) + "_"+ str(month).zfill(2) + ".csv"
                    urllib.request.urlretrieve(linkinfo,savename)
                    sleep(3)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[2])
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
        except NoSuchElementException:
            print("skip")
    if mode == "観測地情報":
        f = open('./dat/' + mode + '/' + point + '.csv','w')
        try:
            writer = csv.writer(f,lineterminator='\n')
            driver.switch_to.window(driver.window_handles[1])
            driver.find_element_by_xpath('//a[img/@src="/img/btn_view_detail.png"]').click()
            driver.switch_to.window(driver.window_handles[2])
            sleep(3)
            table = driver.find_element_by_tag_name("table")
            print("a")
            trs = table.find_elements_by_tag_name("tr")
            for i in range(1,len(trs)):
                tds = trs[i].find_elements_by_tag_name("td")
                line = []
                for j in range(0,len(tds)):
                    if j < len(tds)-1:
                        line.append(tds[j].text)
                        #line += "%s" % (",")
                    else:
                        line.append(tds[j].text + "\n")
                print(line)
                writer.writerow(line)

            driver.close()
            driver.switch_to.window(driver.window_handles[1])
        except NoSuchElementException:
            try:
                #print("skip")
                driver.switch_to.window(driver.window_handles[1])
                table = driver.find_element_by_tag_name("table")
                sleep(1)
                trs = table.find_elements_by_tag_name("tr")
                for i in range(1,len(trs)):
                    tds = trs[i].find_elements_by_tag_name("td")
                    line = []
                    for j in range(0,len(tds)):
                        if j < len(tds)-1:
                            line.append(tds[j].text)
                            #line += "%s" % (",")
                        else:
                            line.append(tds[j].text + "\n")
                    print(line)
                    writer.writerow(line)
                table = driver.find_element_by_tag_name("table")
            except NoSuchElementException:
                print("skip")
        f.close()

    if mode == "水質・底質":
        if sub_mode == "水質自動観測":
            try:
                driver.switch_to.window(driver.window_handles[1])
                sleep(1)
                driver.find_element_by_xpath('//a[img/@src="/img/btn_srch_wqua_auto.png"]').click()
                date = datetime(start,1,1)
                while True:
                    print("A")
                    driver.switch_to.window(driver.window_handles[2])
                    sleep(1)
                    Byear_element = driver.find_element_by_name("BYEAR")
                    Byear_element.clear()
                    Byear_element.send_keys(date.year)
                    BMON_element = driver.find_element_by_name("BMON")
                    BMON_element.clear()
                    BMON_element.send_keys(date.month)
                    BDAY_element = driver.find_element_by_name("BDAY")
                    BDAY_element.clear()
                    BDAY_element.send_keys(date.day)

                    date += timedelta(weeks=1)
                    Ayear_element = driver.find_element_by_name("AYEAR")
                    Ayear_element.clear()
                    Ayear_element.send_keys(date.year)
                    AMON_element = driver.find_element_by_name("AMON")
                    AMON_element.clear()
                    AMON_element.send_keys(date.month)
                    ADAY_element = driver.find_element_by_name("ADAY")
                    ADAY_element.clear()
                    ADAY_element.send_keys(date.day)
                    sleep(1)
                    driver.find_element_by_name("SUBMIT").click()
                    sleep(1)
                    driver.switch_to.window(driver.window_handles[3])
                    linkinfo = driver.find_element_by_xpath('//a[img/@src="/img/download.png"]').get_attribute('href')
                    print(linkinfo)
                    savename = "./dat/" + mode + "/" +  point + "_" + sub_mode + "_" + str(date.year) + "_"+ str(date.month).zfill(2) + str(date.day).zfill(2) + ".csv"
                    urllib.request.urlretrieve(linkinfo,savename)
                    sleep(1)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[2])
                    if date.year > end:
                        break
                    date += timedelta(days=1)
                driver.close()
                driver.switch_to.window(driver.window_handles[1])
            except NoSuchElementException:
                print("skip")
        if sub_mode == '任意期間水質':
            try:
                driver.switch_to.window(driver.window_handles[1])
                driver.find_element_by_xpath('//a[img/@src="/img/btn_srch_wqua_free.png"]').click()
                date = datetime(start,1,1)
                driver.switch_to.window(driver.window_handles[2])
                sleep(0.3)
                nForm = driver.find_element_by_name('nForm')
                tables = nForm.find_elements_by_tag_name("table")
                line = []
                for table in tables:
                    trs = table.find_elements_by_tag_name("tr")
                    for i in range(1,len(trs)):
                        tds = trs[i].find_elements_by_tag_name("td")
                        for j in range(0,len(tds)):
                            if j < len(tds)-1:
                                line.append(tds[j].text)
                                #line += "%s" % (",")
                            else:
                                line.append(tds[j].text + "\n")
                    print(line)
                    if "197*" in line:
                        downfloor = 1970
                    elif "198*" in line:
                        downfloor = 1980
                    elif "199*" in line:
                        downfloor = 1990
                    elif "200*" in line:
                        downfloor = 2000
                    elif "201*" in line:
                        downfloor = 2010
                    else:
                        downfloor = start
                upfloor = driver.find_element_by_name("BYEAR").get_attribute('value')
                if not point + "_" + sub_mode + "_" + "01_" + upfloor + ".csv" in files:
                    for year in range(downfloor,int(upfloor)+1):
                        driver.switch_to.window(driver.window_handles[2])
                        sleep(1)
                        Byear_element = driver.find_element_by_name("BYEAR")
                        Byear_element.clear()
                        Byear_element.send_keys(str(year))
                        BMON_element = driver.find_element_by_name("BMON")
                        BMON_element.clear()
                        BMON_element.send_keys("01")

                        Ayear_element = driver.find_element_by_name("AYEAR")
                        Ayear_element.clear()
                        Ayear_element.send_keys(str(year))
                        AMON_element = driver.find_element_by_name("AMON")
                        AMON_element.clear()
                        AMON_element.send_keys("12")
                        #radios = driver.find_elements_by_xpath("//*[@type='radio']")
                        #thread = []
                        #for i in range(len(radios)):
                        #    thread.append(multidownload(radios[i].get_attribute('value'),driver.current_url,year,sub_mode,point,mode))
                        #    pool.apply_async(thread[i].start())
                        #for t in thread:
                        #    t.join()
                            #t.clear()

                        #Parallel(n_jobs=-1)([delayed(download_radio)(radios[n]) for n in range(len(radios))])
                        #pool = mp.Pool(len(radios))
                        #pool.map(download_radio(radios),range(len(radios)))
                        for radio in driver.find_elements_by_xpath("//*[@type='radio']"):
                            value = radio.get_attribute('value')
                            radio.click()
                            driver.find_element_by_name("SUBMIT").click()
                            sleep(0.5)
                            driver.switch_to.window(driver.window_handles[3])
                            linkinfo = driver.find_element_by_xpath('//a[img/@src="/img/download.png"]').get_attribute('href')
                            print(linkinfo)
                            savename = "./dat/" + mode + "/" +  point + "_" + sub_mode + "_" + value + "_" + str(year) + ".csv"
                            p = mp.Process(target=download(linkinfo,savename))
                            p.deamon = False
                            p.start()
                            driver.close()
                            driver.switch_to.window(driver.window_handles[2])
                driver.switch_to.window(driver.window_handles[2])
                driver.close()
                driver.switch_to.window(driver.window_handles[1])
                    #p.join()
            except NoSuchElementException:
                print("skip")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

if __name__ == '__main__':
    chromeOptions = Options()
    driver_path = 'chromedriver.exe'
    URL = 'http://www1.river.go.jp/cgi-bin/SrchSite.exe?KOMOKU=0&SUIKEI=0&KEN=0'
    rivername = "全水系"
    #mode = "雨量"
    #mode = "水質・底質"
    #mode = "水位流量"
    mode = "観測地情報"
    #sub_mode = "水質自動観測"
    sub_mode = "任意期間水質"
    term_start = 1970
    term_end = 2018
    prefs = {"download.deafult_derectory" : './'}
    #chromeOptions.add_experimental_option("prefs",prefs)
    #chromeOptions.add_argument('--headless')
    #chromeOptions.add_argument('--disable-gpu')
    #chromeOptions.add_argument('--window-size=1200,1100')
    chromeOptions.add_argument('--disable-application-cache')
    chromeOptions.add_argument('--disk-cache-size=0')

    driver = webdriver.Chrome(executable_path = driver_path,chrome_options = chromeOptions)
    driver.get(URL)
    #driver.manage().window().maximize()
    #sleep(1)
    pool = mp.Pool(8)

    element = driver.find_element_by_name('SUIKEI')
    select = Select(element)
    selectOp = select.options
    for options in selectOp:
        if (rivername in options.text):
            print(options.text)
            options.click()

    if mode != "観測地情報":
        element = driver.find_element_by_name('KOMOKU')
        select = Select(element)
        selectOp = select.options
        for options in selectOp:
            if (mode in options.text):
                print(options.text)
                options.click()

    driver.find_element_by_name('SUBMIT1').click()
    sleep(0.3)
    totalpages = driver.find_element_by_name('SELECT').text.splitlines()
    nums = str([num for num in totalpages if "全部で" in num][0])
    nums = int([i for i in re.findall(r'([0-9]*)',nums) if i != ''][0])

    #def __init__(self,start,end,mode,submode,t_start,t_end,rivername):
    thread = []
    for i in range(0,round(nums/10),round((nums/10)/8)):
        print(i)
        thread.append(multiexplorer(i,(i+round((nums/10)/8))-1,mode,sub_mode,term_start,term_end,rivername,driver.current_url))
        pool.apply_async(thread[-1].start())
    for t in thread:
        t.join()
'''
    #for i in range(0,)
    #a = driver.find_element_by_tag_name('a').click()
    #print(a.text)
    datasize = 0
    pages = 0
    #while True:
    lists = driver.find_elements_by_xpath("//*[@href]")
    files = os.listdir('dat/' + mode)
    #main_window = driver.current_window_handle.copy()
    while True:
        lists = driver.find_elements_by_xpath("//*[@href]")
        print(len(lists))
        for link in lists:
            if is_japanese(link.text):
                datasize = datasize + 1
                print(link.text)
                if mode == "水質・底質":
                    if not link.text + "_" + sub_mode + "_" + "01_2017" + ".csv" in files:
                        link.click()
                        mining(mode,term_start,term_end,link.text,sub_mode)
                else:
                    if not link.text + ".csv" in files:
                        link.click()
                        mining(mode,term_start,term_end,link.text,sub_mode)
                #link.close()
            if datasize == 10:
                driver.find_element_by_xpath('//a[img/@src="/img/next.gif"]').click()
                pages = pages + 1
                datasize = 0
                break
                sleep(1)
        if len(lists) < 12:
            break
        #if datasize == 10 and pages > 0:
        #    lists[12].click()
    #driver.find_element_by_xpath("//img[@src="+'/img/next.gif'+"]").click()


    #driver.close()
    #driver.quit()
'''
