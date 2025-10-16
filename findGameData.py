# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 20:13:33 2025

@author: john2
"""

from bs4 import BeautifulSoup
from datetime import datetime
import time
# import mysqlDb
import sqlite3
import requests
import findGameType

# 更新本月文字雲
import doCloud

# 更新統計圖
import doPlot

def topGameToday(dbTable):
    
    sql = "select * from {} where date = '{}' \
        limit 10".format(dbTable, datetime.strftime(datetime.today(), "%Y-%m-%d"))
        
    mydb = sqlite3.connect("steam.db")
    cursor = mydb.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    
    try:
        if len(data) != 0:
            print("有資料")
        else:            
            print("沒資料")  
            
            cursor = mydb.cursor()   
            
            url = f"https://store.steampowered.com/search/?filter=global{dbTable}" 
            
            # 使用 requests 抓HTML
            header = {
                "accept":
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                
                "accept-encoding":"gzip, deflate, br, zstd",
                    
                "accept-language":
                    "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
                
                "cache-control":"max-age=0",                
                "connection":"keep-alive",
                
                "cookie":
                    "browserid=572622827210656996; timezoneOffset=28800,0; lastagecheckage=1-January-2008; steamCountry=TW%7Cedf7f2aebfa5a8a4b7bcb5075b360bac; sessionid=2e5791d0127e1a8a38b15bd3; recentapps=%7B%22730%22%3A1759024398%2C%22578080%22%3A1759024395%2C%222858880%22%3A1755511428%2C%221371980%22%3A1755433743%2C%22835570%22%3A1753877729%2C%222139460%22%3A1753704073%2C%22951620%22%3A1753532871%2C%221850740%22%3A1753422111%2C%221313290%22%3A1753420753%2C%221203220%22%3A1753420157%7D; app_impressions=1172470@1_7_7_7000_150_1|2139460@1_7_7_7000_150_1|3008130@1_7_7_7000_150_1|3489700@1_7_7_7000_150_1|578080@1_7_7_7000_150_1|2947440@1_7_7_7000_150_1|730@1_7_7_7000_150_1|1172470@1_7_7_7000_150_1|2139460@1_7_7_7000_150_1|3008130@1_7_7_7000_150_1|3489700@1_7_7_7000_150_1|578080@1_7_7_7000_150_1|2947440@1_7_7_7000_150_1|730@1_7_7_7000_150_1|1172470@1_7_7_7000_150_1|2139460@1_7_7_7000_150_1|3008130@1_7_7_7000_150_1|3489700@1_7_7_7000_150_1|578080@1_7_7_7000_150_1|2947440@1_7_7_7000_150_1|730@1_7_7_7000_150_1|2947440@1_4_4__118|1364780@1_7_7_7000_150_1|1145350@1_7_7_7000_150_1|3447040@1_7_7_7000_150_1|1551360@1_7_7_7000_150_1|578080@1_7_7_7000_150_1|2947440@1_7_7_7000_150_1|3489700@1_7_7_7000_150_1|730@1_7_7_7000_150_1|3008130@1_7_7_7000_150_1|2139460@1_7_7_7000_150_1|1172470@1_7_7_7000_150_1|1984270@1_7_7_7000_150_1|3447040@1_7_7_7000_150_1|1145350@1_7_7_7000_150_1|3142050@1_7_7_7000_150_1|2444750@1_7_7_7000_150_1|2344520@1_7_7_7000_150_1|1364780@1_7_7_7000_150_1|813780@1_7_7_7000_150_1|3259600@1_7_7_7000_150_1|1551360@1_7_7_7000_150_1",
                
                "sec-fetch-dest":"document",                
                "sec-fetch-mode":"navigate",
                "sec-fetch-site":"same-origin",
                "sec-fetch-user":"?1",
                
                "user-agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
            }
        
            # 
            data = requests.get(url, headers=header)
            data.encoding="utf-8"
            data = data.text
            
            
            dataLimit = 25   # 抓取資料數量
        
            # 執行BeautifulSoup 抓資料            
            soup = BeautifulSoup(data, "html.parser")  
            resultsRows = soup.find("div", id = "search_resultsRows")
            rows = resultsRows.find_all("a")[:dataLimit]
            rank = 1
    
            
            # 將抓取的資料進行整理，並存入資料庫中。
            for row in rows:
                link = row.get("href")      # 遊戲頁面連結
                img = row.find("img").get("src")          # 遊戲圖片網址
                name = row.find("span", class_="title").text                # 遊戲名稱
                name = name.replace("'","")                                 # 去掉90`s之類的名稱
                if row.find("div", class_="discount_prices") is None:
                    continue
                prices = row.find("div", class_="discount_prices").text     # 遊戲原價
                
                sale = 0
 
                
                # 遊戲價格整理
                if not("NT$" in prices):
                    price = 0
                else:                
                    price = prices.split("NT$ ")[1].replace(".00","").replace(",","")
                    if len(prices.split("NT$ ")) > 2:
                        sale = prices.split("NT$ ")[2].replace(".00","").replace(",","")
        
                # 抓取今日時間
                now = datetime.today()
                date = datetime.strftime(now, "%Y-%m-%d")
                
                # 執行PY檔 到個別遊戲頁面，抓取遊戲類別
                gameType = findGameType.gameType(dbTable, name, link, date)
                
                # 檢查變數是否正常
                print("排名：", rank)
                print("連結：", link)
                print("圖片：", img)
                print("名稱：", name)
                print("價格：", price)
                print("特價：", sale)
                print("日期：", date)
                print("類型：", gameType)
                print()
    
                # 將資料新增
                sql = "insert into {}(name,image,price,`sale`,`rank`,link,`type`,date) \
                            values ('{}','{}','{}','{}','{}','{}','{}','{}')".format(dbTable, name, img, price, sale, rank, link, gameType, date)
                cursor.execute(sql)
                mydb.commit()
                print(f"MySQL DB 今天新增{name}")
                print()
    
                rank += 1

    except Exception as e:
        print(e)
        time.sleep(5)
    
    finally:
        cursor.close()
        
        # 最後對文字雲進行更新
        doCloud.markCloud(dbTable)
        
        # 對統計圖進行更新
        doPlot.markPlot(dbTable)

        return ""
    
if __name__ == "__main__":
    tableName = ["topsellers","mostplayed"]
    for name in tableName:
        topGameToday(name)