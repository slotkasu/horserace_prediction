import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

#レース名を引数に番号を返す
def getRaceNum(raceName):
	race=["札幌","函館","福島","新潟","東京","中山","中京","京都","阪神","小倉"]
	#どこかに1を挿入したいので要素を1つ少なくする
	ls = ["0" for i in race]
	ls.pop(0)
	#raceに存在しない競馬場を弾く（香港、ドバイ等）
	if raceName in race:
		#イメージ 
		# 0 0 0 0 0 0 0 0 0
		#　↓
		# 0 0 0 0 1 0 0 0 0 0
		ls.insert(race.index(raceName),"1")
		return ls
	else:
		ls.append("0")
		return ls

#芝ダを引数に番号を返す
def getShibadaNum(shibadaName):
	shibada=["芝","ダ"]
	ls = ["0" for i in shibada]
	ls.pop(0)
	if shibadaName in shibada:
		ls.insert(shibada.index(shibadaName),"1")
		return ls
	else:
		ls.append("0")
		return ls
#性別を引数に番号を返す
def getSexNum(sexName):
	#getracenumと同じ
	sex=["牡","牝","セ"]
	ls = ["0" for i in sex]
	ls.pop(0)
	if sexName in sex:
		ls.insert(sex.index(sexName),"1")
		return ls
	#不正な値を弾く
	else:
		ls.append("0")
		return ls

#馬場状態を引数に番号を返す
def getStateNum(stateName):
	state=["良","稍","重","不"]
	ls = ["0" for i in state]
	ls.pop(0)
	if stateName in state:
		ls.insert(state.index(stateName),"1")
		return ls
	#不正な値を弾く
	else:
		ls.append("0")
		return ls



#馬名、着順、単勝オッズ、複勝オッズ二つをリストで返す
def getRaceResult(date):
	url = "https://race.netkeiba.com/race/result.html?race_id="+date+"&rf=race_submenu"
	html = requests.get(url)
	html.encoding = html.apparent_encoding
	soup = BeautifulSoup(html.content,'html.parser')
	name = soup.find_all("tr", class_="HorseList")
	
	if len(name) == 0:
		print("テストデータです。")
		return []
	results = []

	for na in name:
		#2重リスト用
		temp = []
		#馬名
		horse = na.find("span", class_="Horse_Name")
		temp.append(horse.text.strip())
		#着順
		rank = na.find("div", class_="Rank")
		temp.append(rank.text.strip())
		#オッズ
		odds = na.find("td", class_="Odds Txt_R")
		temp.append(odds.text.strip())
		#馬番（ソート用）
		umaban = na.find("td", class_="Num Txt_C")
		temp.append(int(umaban.text.strip()))
		results.append(temp)
	

	results.sort(key=lambda x: x[3])#2列めを基準にソート

	#ソートに利用した馬番を削除
	for i in results:
		i.pop(3)

	return results

######複勝オッズを取得######
def getFuku(date,driver):
	
	# ブラウザを起動する
	if driver is None:
		# ブラウザのオプションを格納する変数をもらってきます。
		options = Options()

		# Headlessモードを有効にする（コメントアウトするとブラウザが実際に立ち上がります）
		# options.set_headless(True)
		options.add_argument("--log-level=3")
		driver = webdriver.Chrome(chrome_options=options)

	driver.get("https://race.netkeiba.com/odds/index.html?type=b1&race_id="+date+"&rf=shutuba_submenu")
	# time.sleep(0.5)
	# HTMLを文字コードをUTF-8に変換してから取得します。
	html = driver.page_source.encode('utf-8')

	# BeautifulSoupで扱えるようにパースします
	soup = BeautifulSoup(html, "html.parser")
	#複勝のテーブルを取得
	odds=soup.find("div", id="odds_fuku_block")
	#副賞のやつがないときは、呼び出し元で処理させる　class_fetch --> l.240らへん
	if odds == None:
		return 0
	else:
		odds=odds.find_all("tr")

	#結果格納用リスト
	results=[]

	#各馬に対して複勝オッズを取得
	for i in odds:
		#たまにNoneが存在するため、その場合はスキップ
		if not i == None:
			#各馬の複勝オッズのみを取得
			odd=i.find("td",class_="Odds Popular")

			#たまにNoneが存在するため、その場合はスキップ
			if not odd == None:
				if len(odd.string.split()) != 3:
					results.append(["0", "0"])
					f=open("badlist.txt","a")
					f.write(date+"\n")
					f.close()
					continue

				#最低オッズを取得
				min_odds=odd.string.split()[0]
				#最高オッズを取得
				max_odds=odd.string.split()[2]
				results.append([min_odds, max_odds])
	return results

#2:00.0みたいなやつを秒数にする
def TtoF(time_origin):#stringでください
	ls = time_origin.split(":",1)
	if len(time_origin.split(".")) == 3:
		ls = time_origin.split(".",1)
	if len(ls) == 1:
		return time_origin
	min = float(ls[0])
	sec = float(ls[1])
	tt = min*60 + sec
	return str(tt)


def makeRaceName(date):
	url = "https://race.netkeiba.com/race/shutuba_past.html?race_id="+date+"&rf=shutuba_submenu"

	html = requests.get(url)
	html.encoding =html.apparent_encoding
	soup = BeautifulSoup(html.content,'lxml',from_encoding="euc-jp")
	
	#trタグのHorseListクラスからtr_[0-9]{2}のものだけを抽出
	horseLists = soup.find_all("tr",class_="HorseList",id=re.compile(r"tr_[0-9]+"))
	if len(horseLists) == 0:
		print("サイトが存在しないためスキップします。")
		return 3
	if soup.find("tr",class_="HorseList Cancel"):
		print("除外馬が存在するためスキップします。")
		return 1
	try:
		title = soup.find("div",class_="RaceName").text.strip()
	except:
		print("CANT GET RACE NAME")
		title = None

	user = (int(date),title)
	
	try:
		c.execute(sql,user)
		dbname.commit()
	except:
		print(date, title, "ERROR : already exists.")

	return 0