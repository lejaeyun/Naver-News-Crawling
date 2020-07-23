# -*- coding: utf-8 -*-


def check_smilarity(path, notimportant_list, stock) :
    import os
    from sklearn.feature_extraction.text import TfidfVectorizer

    for filename in os.listdir(path):
        if '시황' in filename : continue
        if 'result' in filename : continue
    
        with open(path+ '/' + filename, 'r+', encoding = 'utf-8') as f :
            lst = list(map(lambda x: x.rstrip(), f.readlines()))
        
        # 중요하지 않은 내용은 거르기
        for s in notimportant_list :
            for l in lst :
                if s in l : 
                    lst.remove(l)
        
        vect = TfidfVectorizer(min_df=1)
        tfidf = vect.fit_transform(lst)
        smilarity = (tfidf * tfidf.T).A
        
        
        overlap_list = check_overlap(lst, stock, smilarity)
        for overlap in overlap_list :
            lst.remove(overlap)
            
        save_result(path, filename, lst)
            

def check_overlap(lst, stock, smilarity) :
    overlap_list = list()
    for i in range(len(lst)) :
        for j in range(i,len(lst)) :
            if i == j : continue
            for stock_name in stock.keys() :
                if stock_name in lst[i] and stock_name in lst[j] :
                    if smilarity[i,j] > 0.2 :
                        overlap_list.append(lst[j])
                        
    return list(set(overlap_list))

def save_result(path, filename, lst) :
    import os
    result_filename = path+ '/' + filename.split('.')[0] + '_result.txt'
    if os.path.exists(result_filename):
        with open(result_filename, 'r+', encoding = 'utf-8') as f :
            for i in list(map(lambda x: x.rstrip(), f.readlines())) :
                if i in lst :
                    lst.remove(i)
    else :
        open(result_filename, 'w', encoding = 'utf-8').close()
        
    if lst :                
        with open(path+ '/' + filename.split('.')[0] + '_result.txt', 'a', encoding = 'utf-8') as f :
            for l in lst :
                print(l)
                f.write(l + '\n')

def get_notimportant() :
    notimportant = list()
    with open('notimportant','r', encoding = 'utf-8') as f :
        l = list(map(lambda x: x.rstrip(), f.readlines()))
        for s in l :
            notimportant.append(s)
    return notimportant
                 
def get_stock(path) :
    import pandas as pd
    df = pd.read_csv(path)
    df.code = df.code.map('{:06d}'.format)
    df = df.astype({'code': 'str'})
    print("Company Data Load 완료!")
    return df.set_index('name').T.to_dict('list')

def main() :
    from datetime import date
    import os
    stock_path = os.getcwd() + '/../Tensor Data Api (Kiwoom)/Company.csv'
    date = date.today().strftime('%Y%m%d')
    path = os.getcwd()+'/News/'+date
    stock = get_stock(stock_path)
    notimportant_list = get_notimportant()
    
    while True :
        check_smilarity(path,notimportant_list, stock)
    
main()