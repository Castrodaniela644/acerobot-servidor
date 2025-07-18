import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get('Body')
    sender = request.form.get('From')

    if not incoming_msg or not sender:
        return jsonify({"error": "Faltan datos"}), 400

    try:
        # Nueva forma de generar respuestas con OpenAI >=1.0.0
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente de ventas experto en materiales para construcción. Responde de forma clara, semiformal y con un emoji."},
                {"role": "user", "content": incoming_msg}
            ]
        )

        response_text = completion.choices[0].message.content.strip()

        return jsonify({"respuesta": response_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return "🟢 AceroBot activo."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
