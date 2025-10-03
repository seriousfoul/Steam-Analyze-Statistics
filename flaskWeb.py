# import mysqlDb
import sqlite3

from flask import Flask, render_template,request
from flask_paginate import Pagination, get_page_parameter

from datetime import datetime

# 載入執行BeautifulSoup的python檔案
from findGameData import topGameToday

app = Flask(__name__)


# SQL搜尋資料
def getData(tableName, funcWork): #tableName為資料表名稱，funWork為執行BeautifulSoup的python檔案
    # funcWork(tableName)
    
    # 執行今日資料總筆數
    page = request.args.get('page')
    sql = "select count(id) as GameCount from {} where date = '{}'".format(tableName, datetime.strftime(datetime.today(), "%Y-%m-%d"))

    
    mydb = sqlite3.connect("steam.db")
    cursor = mydb.cursor()
    cursor.execute(sql)
    gameCount = int(cursor.fetchone()[0])
    
    # 判斷有無get()的page參數
    if page == None:
        
        # 今日是否新增資料到資料庫裡，沒有就執行BeautifulSoup的python檔案
        sql = "select * from {} where date = '{}' \
            limit 10".format(tableName, datetime.strftime(datetime.today(), "%Y-%m-%d"))
        
        cursor = mydb.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        
        if len(data) != 0:
            print("有資料")
        else:
            print("沒資料")            
            
        pagination = Pagination(page = 1, total = gameCount ,per_page = 10)
        
        cursor.close()
        return data, pagination 

    else:        
        
        # 接續之前頁面的資料
        page = request.args.get('get_page_parameter()', type=int, default=int(page))
        startp = page - 1

        sql = "select * from {} where date = '{}' \
            limit {},10".format(tableName, datetime.strftime(datetime.today(),"%Y-%m-%d"), startp*10)

        cursor = mydb.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()

        pagination = Pagination(page = page, total = gameCount ,per_page = 10)

        cursor.close()
        return data, pagination 


# 顯示統計資料
def viewType(tableName): 

    sql = "select * from {} where month = '{}'".format(tableName, datetime.strftime(datetime.today(), "%Y-%m-01"))
    
    mydb = sqlite3.connect("steam.db")
    cursor = mydb.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
     
    cursor.close()  
    return data

# 顯示統計資料
def viewTopGame(tableName): 

    # 搜尋 tableName 的全部 並把 tableName 沒有的資料，
    # name、image(第一名)、link 從大表 由name聚合 加入 tableName
    sql = "SELECT g.*, s.image, s.link FROM {} as g LEFT JOIN ( select name, min(image) as image, link from topsellers GROUP BY name) as s on g.name = s.name  where month = '{}' ".format(tableName, datetime.strftime(datetime.today(), "%Y-%m-01"))
    
    mydb = sqlite3.connect("steam.db")
    cursor = mydb.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()         
     
    cursor.close()  
    return data


# 首頁
@app.route('/')
def index():
    top5SellGame = viewTopGame("top5sellgame")
    top5PeopleGame = viewTopGame("top5peoplegame")
    top10SellGameType = viewType("top10sellgametype")
    top10PeopleGameType = viewType("top10peoplegametype")
    topSellPricePie = viewType("topsellpricepie")
    mostPlayPricePie = viewType("mostplaypricepie")
    
    return render_template('index.html', **locals())
    
    
# 最暢銷遊戲 前25名
@app.route('/top_Seller_Today')
def topsellertoday():
    data, pagination = getData("topsellers", topGameToday)    

    return render_template('getDateToday.html', data=data, pagination=pagination)
    

# 今日人數 前25名
@app.route('/most_Played_Today')
def mostplayedtoday():
    data, pagination= getData("mostplayed", topGameToday)    

    return render_template('getDateToday.html', data=data, pagination=pagination)
   

# 統計圖表
@app.route('/analyze_data')
def analyze_data():    
    # 給日期抓本月的文字雲
    now = datetime.today()
    
    return render_template('analyze_data.html', month = now.strftime("%Y-%m"))

# 意見回饋
@app.route('/feedback', methods=['GET','POST'])
def feedback():
    if request.method == "POST":
        name = request.form.get('username')
        email = request.form.get('usermail')
        title = request.form.get('title')
        contant = request.form.get('contant')

        sql = "insert into feedback (name,email,title,contant) values ('{}','{}','{}','{}')".format(name, email, title, contant)
        mydb = sqlite3.connect("steam.db")
        cursor = mydb.cursor()
        cursor.execute(sql)
        mydb.commit()
        cursor.close()

        success = True
    else:
        success = False

    return render_template('feedback.html', **locals())
    
@app.route('/api')
def api():
    
    text = """
        <div style="margin:5%; ">
            <h2> 歡迎使用 api 工具 </h2>
            <h3> 請在網址上輸入 /api/gt/sm 來選取需要的數據： </h4>
            <ol style="font-size:20;"> 
                <li> gt：在 gt 的位置填入 game / type / price </li>
                <ul>
                    <li> game 為 前五名遊戲 </li>
                    <li> type 為 前十名遊戲類別 </li>
                    <li> price 為 價格排行百分比 </li>
                </ul>
                <br />
                <li> sm：在 sm 的位置填入 topSeller / mostPlayer </li>
                <ul>
                    <li> topSeller 為 暢銷遊戲 </li>
                    <li> mostPlayer 為 最多人由玩遊戲 </li>
                </ul>
            </ol>      
        </div>
    """
    
    return text


@app.route('/api/<gt>/<sm>')
def api2(gt, sm):
        
    if gt == "game":
        if sm == "topSeller":
            
            sql = "SELECT * FROM `top5sellgame`"
            mydb = sqlite3.connect("steam.db")
            cursor = mydb.cursor()
            cursor.execute(sql)      
            data = cursor.fetchall()
            
            gameList = []
            if data:
                for row in data:
                    gameData = {}
                    gameData['name'] = row[1]
                    gameData['rank'] = row[2]
                    gameData['month'] = row[3].strftime("%Y-%m")
                    gameList.append(gameData)

                return {"Top5 Seller Game":{"status":"Success","product":gameList}}, 200
            else:
                return {"Top5 Seller Game":{"status":"Failure","message":"Nothing Here"}}, 403
            
        elif sm == "mostPlayer":
            
            sql = "SELECT * FROM `top5peoplegame`"
            mydb = sqlite3.connect("steam.db")
            cursor = mydb.cursor();
            cursor.execute(sql)      
            data = cursor.fetchall()
            
            gameList = []
            if data:
                for row in data:
                    gameData = {}
                    gameData['name'] = row[1]
                    gameData['rank'] = row[2]
                    gameData['month'] = row[3].strftime("%Y-%m")
                    gameList.append(gameData)        

                return {"Top5 Most Player ":{"status":"Success","product":gameList}}, 200
            else:
                return {"Top5 Most Player":{"status":"Failure","message":"Nothing Here"}}, 403
        
    elif gt == "type":
        if sm == "topSeller":
            sql = "SELECT * FROM `top10sellgametype`"
            mydb = sqlite3.connect("steam.db")
            cursor = mydb.cursor();
            cursor.execute(sql)      
            data = cursor.fetchall()
            
            gameList = []
            if data:
                for row in data:
                    gameData = {}
                    gameData['type'] = row[1]
                    gameData['count'] = row[2]
                    gameData['rank'] = row[3]
                    gameData['month'] = row[4].strftime("%Y-%m")
                    gameList.append(gameData)        

                return {"Top10 Seller Game - Type":{"status":"Success","product":gameList}}, 200
            else:
                return {"Top10 Seller Game - Type":{"status":"Failure","message":"Nothing Here"}}, 403
        
        elif sm == "mostPlayer":
            sql = "SELECT * FROM `top10sellgametype` "
            mydb = sqlite3.connect("steam.db")
            cursor = mydb.cursor();
            cursor.execute(sql)      
            data = cursor.fetchall()
            
            gameList = []
            if data:
                for row in data:
                    gameData = {}
                    gameData['type'] = row[1]
                    gameData['count'] = row[2]
                    gameData['rank'] = row[3]
                    gameData['month'] = row[4].strftime("%Y-%m")
                    gameList.append(gameData)        

                return {"Top10 Most Player - Type":{"status":"Success","product":gameList}}, 200
            else:
                return {"Top10 Most Player - Type":{"status":"Failure","message":"Nothing Here"}}, 403      
    
    elif gt == "price":
        if sm == "topSeller":
            sql = "SELECT * FROM `topsellpricepie` "
            mydb = sqlite3.connect("steam.db")
            cursor = mydb.cursor();
            cursor.execute(sql)      
            data = cursor.fetchall()
            
            gameList = []
            if data:
                for row in data:
                    gameData = {}
                    gameData['type'] = row[1]
                    gameData['percent'] = row[2]
                    gameData['month'] = row[3].strftime("%Y-%m")
                    gameList.append(gameData)        

                return {"Percentage of Top Seller Price Type":{"status":"Success","product":gameList}}, 200
            else:
                return {"Percentage of Top Seller Price Type":{"status":"Failure","message":"Nothing Here"}}, 403
        
        elif sm == "mostPlayer":
            sql = "SELECT * FROM `topsellpricepie` "
            mydb = sqlite3.connect("steam.db")
            cursor = mydb.cursor();
            cursor.execute(sql)      
            data = cursor.fetchall()
            
            gameList = []
            if data:
                for row in data:
                    gameData = {}
                    gameData['type'] = row[1]
                    gameData['percent'] = row[2]
                    gameData['month'] = row[3].strftime("%Y-%m")
                    gameList.append(gameData)        

                return {"Percentage of Most Player Price Type":{"status":"Success","product":gameList}}, 200
            else:
                return {"Percentage of Most Player Price Type":{"status":"Failure","message":"Nothing Here"}}, 403      


if __name__ == "__main__":
    app.run(debug=True)