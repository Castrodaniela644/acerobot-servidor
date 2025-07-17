import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import requests

load_dotenv()

app = Flask(__name__)

# Clave de API de OpenAI y URL de precios desde entorno
openai.api_key = os.getenv("OPENAI_API_KEY")
SHEETBEST_URL = os.getenv("SHEETBEST_URL")

def obtener_precios():
    try:
        respuesta = requests.get(SHEETBEST_URL)
        if respuesta.status_code == 200:
            return respuesta.json()
        return []
    except Exception as e:
        print("Error al obtener precios:", e)
        return []

@app.route("/webhook", methods=["POST"])
def webhook():
    mensaje_entrante = request.values.get("Body", "").strip()

    if not mensaje_entrante:
        return jsonify({"mensaje": "No se recibió ningún mensaje"}), 400

    try:
        precios = obtener_precios()

        contexto = ""
        for i, producto in enumerate(precios[:3]):
            nombre = producto.get("producto", "Producto")
            precio = producto.get("precio", "Precio no disponible")
            contexto += f"{nombre}: {precio}\n"

        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Eres un asistente de ferretería colombiano que responde con jerga semiformal. Aquí tienes los precios más recientes:\n{contexto}"
                },
                {"role": "user", "content": mensaje_entrante}
            ]
        )

        salida = respuesta["choices"][0]["message"]["content"].strip()
        return jsonify({"mensaje": salida}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=puerto)
