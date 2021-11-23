# htmlを保存するスクリプト
import urllib.request
import os
from bs4 import BeautifulSoup


skip = ["script","映像を見る","movie.html","colours","var"]

def save_shutubahyo_html(date):
    # netkeibaの5走出馬表をダウンロードします
    url = "https://race.netkeiba.com/race/shutuba_past.html?race_id="+date+"&rf=shutuba_submenu"
    # 保存先作成
    os.makedirs("html/"+date[:4],exist_ok = True)
    filename = "html/"+date[:4]+"/"+date+".html"

    # ダウンロード済なら飛ばす
    if os.path.exists(filename):
        print("exist")
        return 0
    try:
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html,"lxml")
        if soup.find("title").get_text() == "  |    - netkeiba.com":
            exit(1)
        urllib.request.urlretrieve(url, filename)
    except:
        print("failed download")
        return -1

    with open(filename,"r+",encoding="euc-jp") as f:
        text = f.readlines()
        aaa = []
        app = False
        for i in range(len(text)):
            if "<!-- /.RaceNumWrap -->" in text[i]:
                app = True
            if "<!-- /.Horse_Info_ItemWrap -->" in text[i]:
                app = True
            if "<!-- /.RaceList_Item02 -->" in text[i]:
                app = False
            if "<!-- オッズ -->" in text[i]:
                break
            for j in skip:
                if j in text[i]:
                    continue
            if app == False:
                continue
            if text[i] != "\n":
                aaa.append(text[i])

    with open(filename,"w+",encoding="euc-jp") as f:
        f.writelines(aaa)
    return 0

if __name__ == '__main__':
    save_shutubahyo_html("201810010501")
