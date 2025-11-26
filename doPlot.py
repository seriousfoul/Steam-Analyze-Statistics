from mysqlDb import mydb
# import sqlite3

from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# 繪製折線圖
def linePlot(Plot, tableName , today):

    # 中文字體
    chinese_font = matplotlib.font_manager.FontProperties(fname="../wwwroot/font/kaiu.ttf")

    plt.legend(handles = Plot, prop = chinese_font)
    plt.gca().invert_yaxis()  # 反轉 Y 軸
    pltname = "{} ".format(today.strftime("%Y-%m -")) + tableName.upper() + " - line"
    plt.title(pltname, fontsize= 20, color= "darkblue", fontproperties=chinese_font)
    plt.xlabel('Date', fontsize=15, color="darkblue", fontproperties=chinese_font)
    plt.ylabel('Rank', fontsize=15, color="darkblue", fontproperties=chinese_font)
    
    pltname = tableName.upper() + " - line"
    plt.tick_params(axis='both' ,labelsize=12, color = 'darkblue')  
    plt.savefig(f'../wwwroot/img/{pltname}.png')
    plt.clf()
    plt.close()   


# 繪製長方圖
def barPlot(dictData, tableName, today):
    
    typeGroup = {'typeName': list(dictData.keys()), 'typeCount':list(dictData.values())}
    typeDf = pd.DataFrame(typeGroup)
    typeDf = typeDf.sort_values(by='typeCount',ascending=False)
    typeDf = typeDf.reset_index()

    typeDf = typeDf.head(10)
    
    # 將整理好的資料存到資料表中
    for time in range(len(typeDf)):
        if tableName == 'topsellers':
            toTable = "top10sellgametype"
            sql = "select id from {} where month = '{}' and `rank` = '{}'".format(toTable, today.strftime("%Y-%m-01"), time+1)
        else:
            toTable = "top10peoplegametype"
            sql = "select * from {} where month = '{}' and `rank` = '{}'".format(toTable, today.strftime("%Y-%m-01"), time+1)
        

        cursor = mydb.cursor()
        cursor.execute(sql)
        
        if cursor.fetchall():
            sql = "update {} set type = '{}', count = '{}' where month = '{}' and `rank` = '{}'".format(toTable, typeDf['typeName'][time], typeDf['typeCount'][time], today.strftime("%Y-%m-01"), time+1)
        else:
            sql = "insert into {} (type, count, `rank`, month) values ('{}','{}','{}','{}')".format(toTable, typeDf['typeName'][time], typeDf['typeCount'][time], time+1, today.strftime("%Y-%m-01"))

        
        cursor.execute(sql)
        mydb.commit()
        cursor.close()        
    
    plt.figure(figsize=(12,9))    

    pltname = "{} ".format(today.strftime("%Y-%m -")) + tableName.upper() + "(Type) - bar"
    plt.bar(typeDf['typeName'], typeDf['typeCount'], tick_label = typeDf['typeName'], width=0.5)
    
    # 中文字體
    chinese_font = matplotlib.font_manager.FontProperties(fname="../wwwroot/font/kaiu.ttf")
    
    plt.title(pltname, fontsize= 40, color= "darkblue", fontproperties=chinese_font)
    plt.xlabel('Type', fontsize=20, color="darkblue", fontproperties=chinese_font)
    plt.ylabel('Count', fontsize=20, color="darkblue", fontproperties=chinese_font)
    plt.xticks(rotation=20)
    plt.tick_params(axis='both' ,labelsize=12, color = 'darkblue')   
    
    pltname = tableName.upper() + "(Type) - bar"
    plt.savefig(f'../wwwroot/img/{pltname}.png')
    plt.clf()
    plt.close()
    

#繪製 圓餅圖
def piePlot(tableName, today):
    sql = "select price, sale from {} where date >= {}".format(tableName, today.strftime("%Y-%m-01"))
    

    cursor = mydb.cursor()
    cursor.execute(sql)
    price = {'free':0, 'price':0, 'sale':0}
    priceData = cursor.fetchall()
    for row in priceData:
        if row[1] != 0:
            price['sale'] += 1
        elif row[0] != 0:
            price['price'] += 1
        else:
            price['free'] += 1
    
    price = {'priceType' : list(price.keys()), 'count': list(price.values())}
    priceDf = pd.DataFrame(price)
    
    # 將分類好的資料存進資料表
    for time in range(len(priceDf)):
        if tableName == 'topsellers':
            toTable = "topsellpricepie"
            sql = "select id from {} where month = '{}' and type = '{}'".format(toTable, today.strftime("%Y-%m-01"), priceDf['priceType'][time])
        else:
            toTable = "mostplaypricepie"
            sql = "select * from {} where month = '{}' and type = '{}'".format(toTable, today.strftime("%Y-%m-01"), priceDf['priceType'][time])
        

        cursor = mydb.cursor()
        cursor.execute(sql)
        sumNum = sum(priceDf['count'])    
        priceData = cursor.fetchone()
        
        if priceData != None:
            sql = "update {} set percent = '{:.0%}' where month = '{}' and type = '{}'".format(toTable, priceDf['count'][time] / sumNum , today.strftime("%Y-%m-01"), priceDf['priceType'][time])
        else:
            sql = "insert into {} (type, percent, month) values ('{}','{:.0%}','{}')".format(toTable, priceDf['priceType'][time], priceDf['count'][time] / sumNum, today.strftime("%Y-%m-01"))
       
        cursor.execute(sql)
        mydb.commit()
        cursor.close()
   
    plt.figure(figsize=(7,5))
    plt.pie(priceDf['count'],
                radius = 0.8,
                center = (-5,-5),
                labels= priceDf['priceType'],
                labeldistance = 1.3,
                pctdistance = 0.5,
                autopct='%.1f%%',
                textprops = {"fontsize" : 15},
                wedgeprops = {'linewidth':2,'edgecolor':'w'},
                shadow=True
                )
    
    chinese_font = matplotlib.font_manager.FontProperties(fname="../wwwroot/font/kaiu.ttf")
    
    pltname = "{} ".format(today.strftime("%Y-%m -")) + tableName.upper() + "(Price) - pie"
    plt.title(pltname, fontsize= 12, color= "darkblue", x=0.5, y=1, fontproperties=chinese_font)
    
    plt.legend(loc = 'upper right', prop = chinese_font)
    
    pltname = tableName.upper() + "(Price) - pie"
    plt.savefig(f'../wwwroot/img/{pltname}.png')
    plt.clf()
    plt.close()


def markPlot(dbTable):
    
    # 擷取資料 - 時間為該月份
    now = datetime.today()
    
    # 搜尋當月上榜最多的前5筆資料
    sql = 'select name,type,price,count(`name`) as time from `{}` where date >= "{}" Group by name,type,price Order by time desc, avg(`rank`) asc limit 5'.format(dbTable, now.strftime("%Y-%m-01"))

    cursor = mydb.cursor()
    cursor.execute(sql)
    info = cursor.fetchall()
    
    # 取得前5名的細項資料，並Json格式整理
    gameList = []
    for row in info:
        gameNameData = {}
        gameNameData["name"] = row[0]
        gameNameData["type"] = row[1]
        gameNameData['price'] = row[2]
        sql = "select `rank`, sale, date from {} where date >= '{}' and name = '{}'".format(dbTable, now.strftime("%Y-%m-01"), row[0])
        cursor.execute(sql)
        rowInfo = cursor.fetchall()
        
        gameInfoList = []
        for col in rowInfo:
            gameInfo = {}
            gameInfo['rank'] = col[0]
            gameInfo['sale'] = col[1]
            gameInfo['date'] = col[2].strftime("%d");
            gameInfoList.append(gameInfo)
            
        
        gameNameData['gameInfo'] = gameInfoList
        
        gameList.append(gameNameData)
    

    # 資料由 Json 轉成 pandas
    gameListDf = pd.DataFrame(gameList)
    
    
    # 開始繪製圖形
    # 折線圖 - 時間與排名的關係
    lineColor = ["red","skyblue","orange","purple","green"]
    plotList = []
    rankCount = []
    
    for time in range(len(gameList)):        
        gameDf = pd.DataFrame(gameListDf['gameInfo'][time], columns=['rank','date'])
        gameDf.set_index('date', inplace=True)
        
        tempPlot = plt.plot(gameDf, '-o', label = gameListDf['name'][time], color=lineColor[time])
        plotList.append(tempPlot[0])
        
        rankCount.append(gameDf['rank'].sum())

    rankSort = pd.DataFrame({'name':gameListDf['name'], "count": rankCount}) 

    rankSort = rankSort.sort_values(by='count', ascending=True)
    rankSort = rankSort.reset_index(drop=True)


    # 將統計好的資料 存到 專屬的統計資料表中
    for time in range(len(gameList)):
        if dbTable == 'topsellers':
            toTable = "top5sellgame"
            sql = "select id from {} where month = '{}' and `rank` = '{}'".format(toTable, now.strftime("%Y-%m-01"), time+1)
        else:
            toTable = "top5peoplegame"
            sql = "select id from {} where month = '{}' and `rank` = '{}'".format(toTable, now.strftime("%Y-%m-01"), time+1)
        
        cursor = mydb.cursor()
        cursor.execute(sql)

        if cursor.fetchall():
            sql = "update {} set name = '{}' where month = '{}' and `rank` = '{}'".format(toTable, rankSort['name'][time],  now.strftime("%Y-%m-01"), time+1)
        else:
            sql = "insert into {} (name, `rank`, month) values ('{}','{}','{}')".format(toTable, rankSort['name'][time], time+1, now.strftime("%Y-%m-01"))
        
        cursor.execute(sql)
        mydb.commit()
        cursor.close()
    
    linePlot(plotList, dbTable, now)
    

    # 長方圖 - 一個月內上榜遊戲的類別比較
    typeGroup = {}
    for time in range(len(info)):
        for typeName in info[time][1].split(","):
            if typeName in typeGroup:
                typeGroup[typeName] += 1
            else:
                typeGroup[typeName] = 1

    barPlot(typeGroup, dbTable, now)

    # 圓餅圖 - 特價與免費與沒有特價的比例
    piePlot(dbTable, now)
    
    
if __name__ == "__main__":
    tableName = ["topsellers","mostplayed"]
    for name in tableName:
        markPlot(name)