import requests
from bs4 import BeautifulSoup

# 爬 該遊戲的類別 有新的就存在類別資料表
# 並把資料存在遊戲與類別  

def gameType(dataTable, name, link, date):
    url = link
        
    header = {
        "cookie":"wants_mature_content=1; browserid=572622827210656996; timezoneOffset=28800,0; steamCountry=TW%7Cedf7f2aebfa5a8a4b7bcb5075b360bac; sessionid=0cb25a8589047e296cd3eb6e; app_impressions=%7C2379740%401_7001_topselling__7003%7C1430190%401_7001_topselling__7003%7C1203220%401_7001_topselling__7003; birthtime=-820573199; lastagecheckage=1-January-1944; recentapps=%7B%222139460%22%3A1753401490%7D",
        'cache-control':'max-age=0',
        "user-agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }

    data = requests.get(url, headers = header)
    data.encoding="utf-8"
    data = data.text
    soup = BeautifulSoup(data, "html.parser")

    typeInfo = soup.find("div", class_="glance_tags popular_tags")

    if typeInfo.find("a") == None:
        return ""
    else:
        typeInfos = typeInfo.find_all("a")
    
    typeData = ""
    for a in typeInfos:
        typeData += a.text.strip().replace("'", "")
        typeData += ","
    typeData = typeData[:-1]
    print("取得遊戲類別")
        
    return typeData

if __name__ == "__main__":
    s = gameType("topsellers", "Counter-Strike 2","https://store.steampowered.com/app/730/CounterStrike_2/","2025-04-01")
    print(s)