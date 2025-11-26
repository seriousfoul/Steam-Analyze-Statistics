from mysqlDb import mydb
# import sqlite3

from datetime import datetime
from wordcloud import WordCloud

def markCloud(dbtable):       
    now = datetime.today()
    month = now.strftime("%Y-%m-01")
    
    sql = "select type from {} where date >= {}".format(dbtable, month)
    

    cursor = mydb.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()

    text = ""
    for row in data:
        if row[0] == "None":
            continue
        
        if text == "":
            text = " ".join([item for item in row[0].split(",")])
        else:
            text += " " + " ".join([item for item in row[0].split(",")])
            
    cloud = WordCloud(font_path="msjh.ttc", width=800, height=600, background_color="white").generate(text)
    
    
    if dbtable == "topsellers":
        image_path = '../wwwroot/img/topsellers_cloud.png' 
    elif dbtable == "mostplayed":
        image_path = '../wwwroot/img/mostplay_cloud.png'
    cloud.to_file(image_path) # 讓文字雲存檔
    
    cursor.close()
    return print(f"{dbtable}文字雲建立成功")

if __name__ == "__main__":
    tableName = ["topsellers","mostplayed"]
    for name in tableName:
        markCloud(name)