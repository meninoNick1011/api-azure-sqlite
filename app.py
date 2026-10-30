import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

# No Azure App Service (Linux), /home é persistente entre reinícios
DB_PATH = os.path.join(os.environ.get("HOME_DIR", "."), "itens.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS itens ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "nome TEXT NOT NULL, "
            "descricao TEXT)"
        )


init_db()


@app.route("/")
def home():
    return jsonify({"status": "API no ar", "rotas": ["/itens"]})


@app.route("/itens", methods=["GET"])
def listar():
    with get_db() as conn:
        linhas = conn.execute("SELECT * FROM itens").fetchall()
    return jsonify([dict(l) for l in linhas])


@app.route("/itens", methods=["POST"])
def criar():
    dados = request.get_json(silent=True) or {}
    if not dados.get("nome"):
        return jsonify({"erro": "campo 'nome' é obrigatório"}), 400
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO itens (nome, descricao) VALUES (?, ?)",
            (dados["nome"], dados.get("descricao")),
        )
    return jsonify({"id": cur.lastrowid, "nome": dados["nome"]}), 201


@app.route("/itens/<int:item_id>", methods=["DELETE"])
def deletar(item_id):
    with get_db() as conn:
        conn.execute("DELETE FROM itens WHERE id = ?", (item_id,))
    return jsonify({"removido": item_id})


if __name__ == "__main__":
    app.run(debug=True)
