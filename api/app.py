import requests
from flask import Flask, request, jsonify, Response, send_file

app = Flask(__name__)

# memória simples para favoritos e histórico
FAVORITES = set()
HISTORY = []

@app.route('/')
def home():
    return "Flask API para JioSaavn no Vercel!"

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Missing query"}), 400

    url = f"https://jiosaavn-api-privatecvc2.vercel.app/search/songs?query={query}"
    r = requests.get(url)
    if r.status_code != 200:
        return jsonify({"error": "API error"}), 500

    data = r.json()
    return jsonify(data['data']['results'])

@app.route('/stream')
def stream():
    download_url = request.args.get('url')
    filename = request.args.get('filename', 'music.mp4')

    if not download_url:
        return {"error": "Missing url"}, 400

    # Proxy streaming para o cliente
    r = requests.get(download_url, stream=True)
    def generate():
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    headers = {
        "Content-Disposition": f'inline; filename="{filename}"',
        "Content-Type": r.headers.get('Content-Type', 'audio/mpeg')
    }
    return Response(generate(), headers=headers)

@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    song_id = request.json.get('id')
    if not song_id:
        return {"error": "Missing song id"}, 400
    FAVORITES.add(song_id)
    return {"status": "success"}

@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    song_id = request.json.get('id')
    if not song_id:
        return {"error": "Missing song id"}, 400
    FAVORITES.discard(song_id)
    return {"status": "success"}

@app.route('/favorites')
def favorites():
    return jsonify(list(FAVORITES))

@app.route('/add_history', methods=['POST'])
def add_history():
    song_id = request.json.get('id')
    if not song_id:
        return {"error": "Missing song id"}, 400
    if song_id not in HISTORY:
        HISTORY.append(song_id)
    return {"status": "success"}

@app.route('/history')
def history():
    return jsonify(HISTORY)

if __name__ == "__main__":
    app.run()
