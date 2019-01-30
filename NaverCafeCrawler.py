
# coding: utf-8

# In[7]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import datetime 
import pymysql


# In[8]:


def createDB(conn,dbname):
    curs = conn.cursor()
    query = """CREATE DATABASE """+dbname
    try :
        curs.execute(query)
    except :
        print('DB가 이미 존재합니다. DB_NAME : ',dbname)
    
    query = """ALTER DATABASE """+ dbname + """ CHARACTER SET utf8 COLLATE utf8_general_ci;"""
    curs.execute(query)
    conn.commit()


# In[9]:


def save_DB() : 
    temp = keyword.replace(' ','_')
    conn = pymysql.connect(host = "", user = "root", password = "", charset = "utf8")
    dbname = 'naver_cafe_'+ temp
    createDB(conn,dbname)
    curs = conn.cursor()
    curs.execute("""use """+dbname)

    query = """CREATE TABLE IF NOT EXISTS """+ temp + """(ID int, URL varchar(100), Title varchar(100), Date varchar(20), Writer varchar(50), cafe_like int, Count int,Text text(62200));"""
    curs.execute(query)

    query = """ALTER TABLE """ + temp +""" CHARACTER SET utf8 COLLATE utf8_general_ci;"""
    curs.execute(query)

    conn.commit()
    
    select_query = """SELECT * from """ + temp
    index = curs.execute(select_query)

    for value in total_list :
        url = value[0]
        title = value[1]
        date = value[2]
        writer = value[3]
        like = value[4]
        count = value[5]
        content = value[6]

        query = """insert into """ + temp + """(ID, URL, Title, Date, Writer, cafe_like, Count, Text) values (%s, %s, %s, %s, %s, %s, %s, %s) ; """
        curs.execute(query, (str(index), url, title, date,writer,like,count,content))

        index = index + 1 

        conn.commit()
        
    conn.close()
    print("FINISH")


# In[17]:


keyword = input("Keyword ? ")

start_year = input("Start Year ? ")
start_month = input("Start Month ? ")
start_day = input("Start Day ? ")

end_year = input("End Year ? ")
end_month = input("End Month ? ")
end_day = input("End Day ? ")

start_date = start_year+start_month+start_day
end_date = end_year+end_month+end_day


# In[18]:


dt_start_date = datetime.datetime.strptime(start_date,"%Y%m%d").date()
dt_end_date = datetime.datetime.strptime(end_date,"%Y%m%d").date()
day_1 = datetime.timedelta(days=1)
dt_start_1 = dt_start_date


# In[19]:


# 일수를 하루씩 잘라서 반복
while dt_start_1 <= dt_end_date :
    total_list = []
    URL_date_list = []
    page_num = 0
    print(dt_start_1)
    # 페이지 만큼 돌면서 링크 수집
    while True : 
        p_url = 'https://search.naver.com/search.naver?where=article&query='+keyword+'&ie=utf8&st=rel&date_option=6&date_from='+start_date+'&date_to='+start_date+'&board=&srchby=text&dup_remove=1&sm=tab_opt&t=0&mson=0&prdtype=0&start='+str(page_num)+'1'
        driver = webdriver.Chrome('./chromedriver/chromedriver')
        driver.implicitly_wait(3)
        driver.get(p_url)
        soup = BeautifulSoup(driver.page_source,'html.parser')
        a_tags = soup.select('ul#elThumbnailResultArea li dl dt a')

        # 한 페이지에 있는 링크들 전부 가져오기
        for a in a_tags :
            if 'href' in a.attrs :
                url = a.attrs['href']
                print(url)
                driver = webdriver.Chrome('./chromedriver/chromedriver')
                driver.implicitly_wait(3)
                driver.get(url)
                 # 페이지 변환      
                frame = driver.find_element_by_name('cafe_main')
                driver.switch_to_frame(frame)

                soup = BeautifulSoup(driver.page_source,'html.parser')
                # 전체공개 버튼 없다면
                if soup.find("img", {"class" : "recomm"}) is not None :
                    cafe_title = soup.find("span", {"class" : "b m-tcol-c"}).get_text().strip().encode('cp949','ignore')
                    cafe_title = cafe_title.decode('cp949','ignore')
                    print(cafe_title)
                    cafe_date = soup.find("td", {"class" : "m-tcol-c date"}).get_text()
                    print(cafe_date)
                    cafe_writer = soup.find("a", {"class" : "m-tcol-c b"}).get_text()
                    print(cafe_writer)
                    # 좋아요 없으면 0으로
                    if soup.find("em", {"class" : "u_cnt _count"}) is not None :
                        cafe_like = soup.find("em", {"class" : "u_cnt _count"}).get_text()
                    else :
                        cafe_like = 0
                    print(cafe_like)
                    # 댓글 창이 없으면 0으로 
                    if soup.find("a", {"class" : "reply_btn b m-tcol-c m-tcol-p _totalCnt"}) is not None :
                        reply_count = soup.find("a", {"class" : "reply_btn b m-tcol-c m-tcol-p _totalCnt"}).get_text().strip()[3:]
                    else :
                        reply_count = 0
                    print(reply_count)
                    cafe_content = soup.find("div", {"class" : "tbody m-tcol-c"}).get_text().replace('\n','').strip().encode('cp949','ignore')
                    cafe_content = cafe_content.decode('cp949','ignore')
                    print(cafe_content)
                    total_list.append([url,cafe_title,cafe_date,cafe_writer,cafe_like,reply_count,cafe_content])
        driver.get(p_url)
        # 다음 페이지 버튼 있나 확인 후 없으면 while문 빠져나감
        try :
            driver.find_element_by_xpath("//a[@class='next']").click()
            page_num += 1
        except : 
            break;
            
     # 날짜 변환    
    dt_start_1 = dt_start_1 + day_1
    temp = str(dt_start_1)
    start_date = temp[:4]+temp[5:7]+temp[8:]
    
    save_DB()


# In[ ]:


#DB삭제시 이용
# conn = pymysql.connect(host = "", user = "root", password = "", charset = "utf8")
# curs = conn.cursor()
# query = """DROP DATABASE naver_cafe; """
# curs.execute(query)


# In[ ]:


#DB내용 확인시 이용
# conn = pymysql.connect(host = "", user = "root", password = "", charset = "utf8")
# curs = conn.cursor()
# curs.execute("use naver_cafe ;")
# query = """select * from 원자력; """
# curs.execute(query)
# all_rows = curs.fetchall()
# for i in all_rows:
#     print(i)

