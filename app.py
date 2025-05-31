import requests
from flask import Flask, request, jsonify, render_template, Response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Missing query"}), 400

    url = f"https://jiosaavn-api-privatecvc2.vercel.app/search/songs?query={query}"
    r = requests.get(url)
    if r.status_code != 200:
        return jsonify({"error": "API error"}), 500

    data = r.json()
    # Retorna só a lista de resultados para simplificar o frontend
    return jsonify(data['data']['results'])

@app.route('/stream')
def stream():
    # Recebe o link direto para streaming/download (mp4)
    url = request.args.get('url')
    filename = request.args.get('filename', 'music.mp4')

    if not url:
        return {"error": "Missing url"}, 400

    # Faz proxy streaming
    r = requests.get(url, stream=True)
    def generate():
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": r.headers.get('Content-Type', 'audio/mpeg')
    }
    return Response(generate(), headers=headers)

if __name__ == "__main__":
    app.run(debug=True)
