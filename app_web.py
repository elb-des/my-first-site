from flask import Flask, render_template, request
import sqlite3
import os
from datetime import datetime
import email.utils

app = Flask(__name__)

DB_PATH = r"C:\diploma\kino\news.db"   # твоя база

def get_clusters(offset=0, limit=None):
    print("=== DEBUG START ===")

    # 1. проверяем путь
    print("Using DB:", DB_PATH)
    print("Exists:", os.path.exists(DB_PATH))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 2. выводим список таблиц
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print("Tables:", [t[0] for t in tables])

    # 3. пробуем считать данные
    try:
        # Получаем все данные без сортировки на уровне SQL
        if limit:
            cur.execute("SELECT id_news, title, summary_final, date, link, img, content, source FROM news")
            rows = cur.fetchall()
        else:
            cur.execute("SELECT id_news, title, summary_final, date, link, img, content, source FROM news")
            rows = cur.fetchall()
    except Exception as e:
        print("ERROR selecting from news:", e)
        rows = []

    conn.close()

    # Сортируем результаты по дате в Python
    def parse_rss_date(date_str):
        try:
            # Преобразуем RSS дату в объект datetime
            return datetime(*email.utils.parsedate(date_str)[:6])
        except:
            # Если не получается распарсить, возвращаем минимальную дату
            return datetime.min

    # Сортируем по дате в порядке убывания (новые первыми)
    rows = sorted(rows, key=lambda x: parse_rss_date(x['date']), reverse=True)
    
    # Применяем лимит и смещение после сортировки
    if limit:
        rows = rows[offset:offset+limit]
    else:
        rows = rows[offset:]

    print("Rows in news after sorting:", len(rows))
    print("=== DEBUG END ===")
    
    return rows


@app.route("/")
def index():
    data = get_clusters()
    return render_template("web.html", clusters=data)


@app.route("/clusters")
def clusters_api():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 5))
    clusters = get_clusters(offset, limit)
    # Преобразуем объекты Row в словари для JSON сериализации
    clusters_list = []
    for cluster in clusters:
        # Используем summary, если он есть, иначе используем content в качестве резервного варианта
        summary_final = cluster['summary_final'] if cluster['summary_final'] else cluster['content'][:200] + "..." if cluster['content'] else ""
        cluster_dict = {
            'title': cluster['title'],
            'summary_final': summary_final,
            'date': cluster['date'],
            'link': cluster['link'],
            'img': cluster['img'],
            'link': cluster['link'],
            'source': cluster['source']
        }
        clusters_list.append(cluster_dict)
    return {'clusters': clusters_list}


if __name__ == "__main__":
    app.run(debug=True)
