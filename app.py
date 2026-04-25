from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route("/")
def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.route("/movie")
def movie():
    """爬取開眼電影網近期上映電影，直接顯示在網頁上"""
    
    url = "https://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url, verify=False)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    
    # 取得網站最後更新時間
    last_update_tag = sp.find("div", class_="smaller09")
    lastUpdate = last_update_tag.text[5:] if last_update_tag else "未知"

    # 開始產生 HTML 結果
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <title>近期上映電影</title>
        <style>
            body {{
                font-family: 'Microsoft JhengHei', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 40px;
                margin: 0;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
            }}
            h1 {{
                color: white;
                text-align: center;
                margin-bottom: 10px;
            }}
            .update-info {{
                color: white;
                text-align: center;
                margin-bottom: 30px;
                opacity: 0.9;
            }}
            .movie-card {{
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                display: flex;
                gap: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            .movie-pic img {{
                width: 120px;
                border-radius: 10px;
                object-fit: cover;
            }}
            .movie-info {{
                flex: 1;
            }}
            .movie-title {{
                color: #667eea;
                margin-top: 0;
                margin-bottom: 10px;
            }}
            .movie-detail {{
                color: #555;
                margin: 8px 0;
            }}
            .movie-link a {{
                color: #ff6b6b;
                text-decoration: none;
            }}
            .back-link {{
                display: inline-block;
                margin: 20px 10px;
                padding: 10px 20px;
                background: white;
                color: #667eea;
                text-decoration: none;
                border-radius: 50px;
            }}
            .footer {{
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 近期上映電影</h1>
            <div class="update-info">📅 最後更新時間：{lastUpdate}</div>
    """

    for item in result:
        # 1. 抓取海報圖片
        img_tag = item.find("img")
        picture = img_tag.get("src") if img_tag else ""
        
        # 2. 抓取電影名稱與介紹頁連結
        title_tag = item.find("div", class_="filmtitle")
        title = title_tag.text if title_tag else "未知"
        a_tag = title_tag.find("a") if title_tag else None
        hyperlink = "http://www.atmovies.com.tw" + a_tag.get("href") if a_tag else ""
        
        # 3. 抓取上映日期與片長 (這是你最關心的部分)
        runtime_tag = item.find("div", class_="runtime")
        showDate = "未知"
        showLength = "未知"
        if runtime_tag:
            # 取得區塊內的文字，例如：「上映日期：2026/04/29 片長：100 分」
            raw_text = runtime_tag.text
            # 用 replace() 方法去掉多餘的文字
            clean_text = raw_text.replace("上映日期：", "").replace("片長：", "").replace("分", "")
            # 進一步拆分出日期和片長
            if len(clean_text) >= 10:
                showDate = clean_text[0:10]
            if len(clean_text) > 13:
                showLength = clean_text[13:]

        html += f"""
            <div class="movie-card">
                <div class="movie-pic">
                    <img src="{picture}" alt="{title}">
                </div>
                <div class="movie-info">
                    <h2 class="movie-title">🎬 {title}</h2>
                    <p class="movie-detail">📅 上映日期：{showDate}</p>
                    <p class="movie-detail">⏱️ 片長：{showLength} 分鐘</p>
                    <p class="movie-link">🔗 <a href="{hyperlink}" target="_blank">點我看詳細介紹</a></p>
                </div>
            </div>
        """

    html += """
            <div class="footer">
                <a href="/" class="back-link">🏠 回首頁</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

if __name__ == "__main__":
    app.run(debug=True)
