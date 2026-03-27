from flask import Flask, jsonify, request
import json
import os

import psycopg2
import redis

app = Flask(__name__)

DB_HOST = os.environ.get("POSTGRES_HOST", "db")
DB_NAME = os.environ.get("POSTGRES_DB", "testdb")
DB_USER = os.environ.get("POSTGRES_USER", "user")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "password")

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )


def ensure_items_table(conn):
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS items (id SERIAL PRIMARY KEY, name TEXT);")
    conn.commit()
    cur.close()


@app.route("/health")
@app.route("/api/health")
def health():
    return "OK", 200


@app.route("/version")
@app.route("/api/version")
def version():
    return jsonify(
        {
            "version": os.environ.get("APP_VERSION", "dev"),
            "pod": os.environ.get("POD_NAME", os.environ.get("HOSTNAME", "unknown")),
            "node": os.environ.get("NODE_NAME", "unknown"),
        }
    )


@app.route("/items", methods=["GET"])
@app.route("/api/items", methods=["GET"])
def get_items():
    try:
        cached = r.get("items")
        if cached:
            return jsonify(json.loads(cached))

<<<<<<< Updated upstream
    conn = get_db_connection()
    ensure_items_table(conn)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items;")
    data = cur.fetchall()
    cur.close()
    conn.close()
=======
        conn = get_db_connection()
        ensure_items_table(conn)
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM items;")
        data = cur.fetchall()
        cur.close()
        conn.close()
>>>>>>> Stashed changes

        items_list = [{"id": row[0], "name": row[1]} for row in data]
        r.set("items", json.dumps(items_list), ex=60)

        return jsonify(items_list)
    except Exception as error:
        return jsonify({"error": "items_read_failed", "details": str(error)}), 500


@app.route("/items", methods=["POST"])
@app.route("/api/items", methods=["POST"])
def add_item():
    try:
        content = request.json or {}
        name = content.get("name")
        if not name:
            return jsonify({"error": "name is required"}), 400

<<<<<<< Updated upstream
    conn = get_db_connection()
    ensure_items_table(conn)
    cur = conn.cursor()
    cur.execute("INSERT INTO items (name) VALUES (%s) RETURNING id;", (name,))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
=======
        conn = get_db_connection()
        ensure_items_table(conn)
        cur = conn.cursor()
        cur.execute("INSERT INTO items (name) VALUES (%s) RETURNING id;", (name,))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
>>>>>>> Stashed changes

        r.delete("items")

        return jsonify({"id": new_id, "name": name}), 201
    except Exception as error:
        return jsonify({"error": "items_write_failed", "details": str(error)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
