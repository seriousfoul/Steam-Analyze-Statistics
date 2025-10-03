import sqlite3
from datetime import datetime

tableName = "top5sellgame"
sql = "SELECT g.*, s.image, s.link FROM {} as g LEFT JOIN ( select name, min(image) as image, link from topsellers GROUP BY name) as s on g.name = s.name  where month = '{}' ".format(tableName, datetime.strftime(datetime.today(), "%Y-%m-01"))
    
mydb = sqlite3.connect("steam.db")
cursor = mydb.cursor()
cursor.execute(sql)
data = cursor.fetchall()         
 
cursor.close()  