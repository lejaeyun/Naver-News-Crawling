# -*- coding:utf-8 -*-
# Need Library lxml, bs4
from bs4 import BeautifulSoup
import requests
from datetime import date
from threading import Thread

class Crawler :
    def __init__(self, thread_num = 3) :
        import os
        path = os.getcwd() + '/../Tensor Data Api (Kiwoom)/Company.csv'
        self.stock = self.get_stock(path)        
        self.thread_num = thread_num
        
        # 401 : 시황, 전망
        # 402 : 기업, 종목분석
        # 403 : 해외증시
        # 403 : 해외증시
        # 406 : 공시, 메모
        self.section_id = [ [401, '시황, 전망'], [402, '기업, 종목분석'], [406, '공시, 메모']]
        self._newsfocus = "https://finance.naver.com/news/news_list.nhn?mode=LSS3D&section_id=101&section_id2=258&section_id3=sectionid&date="
    
    def createdir(self, path):
        import os
        try:
            if not os.path.exists(path):
                os.mkdir(path)
            else : 
                pass
        except OSError:
            print ('Createdir Error ' +  path)   
  
    def get_stock(self,path) :
        import pandas as pd
        df = pd.read_csv(path)
        df.code = df.code.map('{:06d}'.format)
        df = df.astype({'code': 'str'})
        print("Company Data Load 완료!")
        return df.set_index('name').T.to_dict('list')
    
    def mk_txt(self,path) :
        import os
        if not os.path.exists(path):
            open(path,'w').close()
                
    def find_all(self, url, filename) :
        import copy
        nowpage = copy.deepcopy(url)
        
        result = list()
        for index in range(1,1000) :
            target = nowpage + '&page='+str(index)
            tmpresult = self.finding(target)
            result = result + tmpresult
            if len(tmpresult) == 0 : break
        self.result_dict[filename] = list(set(result))
            
    def BS_Visit(self, url) :
        headers = {'User-Agent':'Chrome/66.0.3359.181'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "lxml")
        return soup
        
    def finding(self, url):
        tmp = list()
        soup = self.BS_Visit(url)
        li = soup.find_all('dd', attrs={'class': 'articleSubject'})
        li = li + (soup.find_all('dt', attrs={'class': 'articleSubject'}))
        for i in li :
            try :
                j = i.find("a")
                j = j.attrs['title']
                if '[' in j and ']' in j :
                    j = j.remove(j[ j.index('[') : j.index(']') ])
                if '-' in j :
                    j = j.remove(j[ j.index('-') ])
                if len(j) != 0 :
                    for stock in self.stock.keys() :
                        if stock in j :
                            tmp.append(j)
                            break
            except :
                pass
            
        return list(set(tmp))

    def save_result(self,filename , txtpath, result) :
        with open(txtpath,'r', encoding = 'utf-8') as f :
            news = f.readlines()
            for s in news :
                s = s.rstrip()
                if s in result :
                    result.remove(s)
                    
        if len(result) != 0 :    
            print(filename)
            
        with open(txtpath,'a', encoding = 'utf-8') as f :
            for s in result :
                print(s)
                f.write(s + '\n')   
                 
        if len(result) != 0 :    
            print()

    def find_focusnews(self, path) :
        threads = list()
        self.result_dict = dict()
        for section_id, filename in self.section_id :
            self.result_dict[filename] = list()
            target = self.newsfocus.replace('sectionid',str(section_id))
            th = Thread(target = self.find_all , args = (target, filename), daemon = True)
            threads.append(th)
            th.start()
        
        for th in threads :
            th.join()
        
        for section_id, filename in self.section_id :
            txtpath = path+'/'+filename+'.txt'
            self.mk_txt(txtpath)
            self.save_result(filename, txtpath, self.result_dict[filename])

                    
    def find_news(self) :
        import os
        self.date = date.today().strftime('%Y%m%d')
        self.newsfocus = self._newsfocus + self.date
        path = os.getcwd()+'/News/'+self.date
        self.createdir(path)
        
        self.find_focusnews(path)
        
def main(thread_num = 3):
    cr = Crawler(thread_num = 3)
    while True :
        cr.find_news()
    
main()
