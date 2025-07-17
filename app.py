import os
from flask import Flask, request
from dotenv import load_dotenv
import openai

load_dotenv()
app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.json.get("Body", "").strip()
    if not incoming_msg:
        return {"message": "No se recibió ningún mensaje"}, 400

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente útil que responde con jerga semiformal colombiana."},
            {"role": "user", "content": incoming_msg}
        ]
    )

    reply = response.choices[0].message.content.strip()
    return {"message": reply}

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=puerto)


