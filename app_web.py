from flask import Flask, render_template, request
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ["DATABASE_URL"]

def get_connection():
    return psycopg2.connect(DATABASE_URL)


def get_clusters(offset=0, limit=None):
    print("= DEBUG START =")

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id_news, title, summary_final, date, link, img, content, source
            FROM news
            ORDER BY date DESC
        """)
        rows = cur.fetchall()

    except Exception as e:
        print("ERROR:", e)
        rows = []

    conn.close()

    columns = ["id_news", "title", "summary_final", "date", "link", "img", "content", "source"]

    rows = [dict(zip(columns, r)) for r in rows]

    # pagination
    if limit:
        rows = rows[offset:offset + limit]
    else:
        rows = rows[offset:]

    print("Rows:", len(rows))
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

    clusters_list = []

    for cluster in clusters:
        summary_final = cluster['summary_final']

        if not summary_final and cluster['content']:
            summary_final = cluster['content'][:200] + "..."
        elif not summary_final:
            summary_final = ""

        clusters_list.append({
            'title': cluster['title'],
            'summary_final': summary_final,
            'date': cluster['date'],
            'link': cluster['link'],
            'img': cluster['img'],
            'source': cluster['source']
        })

    return {'clusters': clusters_list}


if __name__ == "__main__":
    app.run(debug=True)
