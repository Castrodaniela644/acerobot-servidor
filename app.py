import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

app = Flask(__name__)

# Clave de API de OpenAI y URL de precios desde entorno
openai_api_key = os.getenv("OPENAI_API_KEY")
SHEETBEST_URL = os.getenv("SHEETBEST_URL")

client = OpenAI(api_key=openai_api_key)

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
            contexto += f"{producto['Producto']}: ${producto['Precio']} COP.\n"

        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres AceroBot, un asesor experto en venta de materiales de construcción "
                        "en Colombia para la empresa DISNACEROS. Responde siempre con un tono amigable, claro "
                        "y directo. Si el cliente no menciona productos específicos, sugiere cemento, malla electrosoldada, "
                        "varilla Diaco y perfilería placa fácil. Muestra precios si están disponibles. "
                        "Incluye un emoji en cada respuesta y motiva al cliente a comprar o visitar la tienda."
                    )
                },
                {"role": "user", "content": f"{mensaje_entrante}\n\nPrecios actuales:\n{contexto}"}
            ]
        )

        mensaje_respuesta = respuesta.choices[0].message.content.strip()
        return jsonify({"respuesta": mensaje_respuesta})

    except Exception as e:
        print("Error al generar respuesta:", e)
        return jsonify({"error": "Ocurrió un error al procesar el mensaje"}), 500

if __name__ == "__main__":
    app.run(debug=True)
