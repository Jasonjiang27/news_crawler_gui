
import requests
import csv
import sys
from tkinter import *
from bs4 import BeautifulSoup
import scrapy
from scrapy.http import HtmlResponse
from scrapy.http import Request
from selenium import webdriver
from lxml import etree

raw_url = "http://www.zuzhirenshi.com/dianzibao/"

headers = {}
headers['User-Agent'] = 'Mozilla/5.0 ' \
                    '(Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 ' \
                    '(KHTML, like Gecko) Version/5.1 Safari/534.50'

def get_url():
    urls = []
    titles = []
    date = date_input.get()
    
    for i in range(1, 9):
        pre_url = raw_url+date+"/"+str(i)+"/index.htm"
        print(pre_url)

        # detail = requests.get(pre_url, headers=headers)
        driver = webdriver.PhantomJS()

        driver.get(pre_url)
        html = driver.page_source
        response = HtmlResponse(url=pre_url,body=html.encode('utf-8'))
        articleLink = response.xpath('.//div[@id="InfoList"]/div[@class="BanMianMuLu"]/a/@href').extract()
        print(len(articleLink))
        print(articleLink)
        
        for u in articleLink:
            url = raw_url+date+"/"+str(i)+"/"+u.split("/")[-1]
            urls.append(url)
            print(url)
        
        # title = response.xpath('.//div[@class="top" and not(@style)]/text()').extract_first()
        # print(title)
        # titles.append(title)
    
    return urls

def parse():

    urls = get_url()
    header = ["标题","标题1", "作者", "内容"]
    values = []
    for url in urls:
        res = requests.get(url, headers=headers)
        url1 = '/'.join(url.split("/")[:-1])+"/index.htm"
        res1 =requests.get(url1, headers=headers)
        html_doc = res.content
        html_doc1 = res1.content
        resp = HtmlResponse(url, headers=headers, body=html_doc)
        resp1 = HtmlResponse(url1,headers=headers, body=html_doc1)
        title = resp1.xpath('.//div[@class="top" and not(@style)]/text()').extract_first()
        title1 = resp.xpath('.//div[@class="listhottitle3"]/text()').extract_first().strip()
        author = resp.xpath('.//span[@id="Author"]/text()').extract_first().split("：")[-1]
        content = '\n'.join(resp.xpath('.//div[@class="innercontent"]/p').xpath('string(.)').extract())
        dict_data = {
            "标题": title,
            "标题1": title1,
            # "标题2": title2,
            "作者": author,
            "内容": content
        }
        values.append(dict_data)

        text.insert(END,content)
        #文本框向下滚动
        text.see(END)
        #更新
        text.update() 
    return header, values

def Write_csv():
    header, values = parse()
    with open("数字包_"+date_input.get()+".csv", 'w',encoding='utf-8', newline='') as fp:
        writer = csv.DictWriter(fp, header,dialect='excel')
        writer.writeheader()
        writer.writerows(values)
def main():
    global date_input,text
    #创建空白窗口,作为主载体
    root = Tk()
    root.title('数字报新闻抓取')
    #窗口的大小，后面的加号是窗口在整个屏幕的位置
    root.geometry('550x400+398+279')
    #标签控件，窗口中放置文本组件
    Label(root,text='请输入发布的日期:',font=("华文行楷",20),fg='black').grid()
    #定位 pack包 place位置 grid是网格式的布局

    #Entry是可输入文本框
    date_input=Entry(root,font=("微软雅黑",15))
    date_input.grid(row=0,column=1)
    Label(root,text='请输入新闻发布的日期:',font=("微软雅黑",10),fg='black').grid(row=1)
    #列表控件
    text=Listbox(root,font=('微软雅黑',15),width=45,height=10)
    #columnspan 组件所跨越的列数
    text.grid(row=2,columnspan=2)
    #设置按钮 sticky对齐方式，N S W E
    button =Button(root,text='开始下载',font=("微软雅黑",15),command=Write_csv).grid(row=3,column=0,sticky=W)
    button =Button(root,text='退出',font=("微软雅黑",15),command=root.quit).grid(row=3,column=1,sticky=E)
    #使得窗口一直存在
    mainloop()

if __name__ == "__main__":
    main()