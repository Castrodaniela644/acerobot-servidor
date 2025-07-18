import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()

# Inicializar cliente OpenAI moderno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body", "").strip()

    if not incoming_msg:
        return jsonify({"error": "Falta el campo Body con el mensaje del usuario"}), 400

    try:
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres AceroBot, asesor experto en ventas de materiales de construcción. "
                        "Responde de forma clara, amigable y semiformal. Agrega un emoji al final."
                    )
                },
                {"role": "user", "content": incoming_msg}
            ],
            temperature=0.7,
            max_tokens=250
        )

        mensaje = respuesta.choices[0].message.content.strip()

        return jsonify({"respuesta": mensaje})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return "🟢 AceroBot está en línea. ¡Listo para responder!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
