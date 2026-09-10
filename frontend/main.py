import requests
from flask import Flask, jsonify, render_template, request

from config import Config

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def homepage():
    return render_template("pages/home.html")


@app.route("/summarize", methods=["POST"])
def summarize():
    """Rota intermediária do Flask que consome o endpoint /api/v1/summarize do backend."""
    data = request.get_json() or {}
    url = data.get("url")

    if not url:
        return jsonify({"error": "A URL do artigo é obrigatória."}), 400

    backend_endpoint = f"{app.config['BACKEND_API_URL']}/api/v1/summarize"

    try:
        response = requests.post(
            backend_endpoint,
            json={"url": url},
            timeout=app.config["BACKEND_API_TIMEOUT_SECONDS"],
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code

    except requests.exceptions.HTTPError:
        error_detail = response.json().get("detail", "Erro no processamento pelo backend.")
        return jsonify({"error": error_detail}), response.status_code
    except requests.exceptions.RequestException as err:
        return jsonify({"error": f"Falha na comunicação com o servidor backend: {str(err)}"}), 502


@app.route("/translate", methods=["POST"])
def translate():
    """Rota intermediária do Flask que consome o endpoint /api/v1/translate do backend."""
    data = request.get_json() or {}
    url = data.get("url")
    target_language = data.get("target_language")

    if not url or not target_language:
        return jsonify({"error": "A URL e o idioma de destino são obrigatórios."}), 400

    backend_endpoint = f"{app.config['BACKEND_API_URL']}/api/v1/translate"

    try:
        response = requests.post(
            backend_endpoint,
            json={"url": url, "target_language": target_language},
            timeout=app.config["BACKEND_API_TIMEOUT_SECONDS"],
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code

    except requests.exceptions.HTTPError:
        error_detail = response.json().get("detail", "Erro na tradução do conteúdo.")
        return jsonify({"error": error_detail}), response.status_code
    except requests.exceptions.RequestException as err:
        return jsonify({"error": f"Falha na comunicação com o servidor backend: {str(err)}"}), 502


if __name__ == "__main__":
    app.run(debug=True)
