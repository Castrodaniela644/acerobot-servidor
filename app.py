import sistema_operativo
from matriz import Matraz, pedido, jsonificar
from dotenv import cargar_dotenv
import openai
import requests  # Para acceder a Sheet.best

cargar_dotenv()

aplicación = Matraz(__name__)

# Cliente OpenAI con clave de entorno
cliente = openai.OpenAI(clave_api=sistema_operativo.obtener_env("OPENAI_API_KEY"))

# URL de Sheet.best (hoja de precios)
SHEETBEST_URL = sistema_operativo.obtener_env("SHEETBEST_URL")


def obtener_precios():
    try:
        respuesta = requests.get(SHEETBEST_URL)
        if respuesta.status_code == 200:
            return respuesta.json()
        else:
            return []
    except Exception as e:
        print("Error al obtener precios:", e)
        return []


@aplicación.ruta("/webhook", métodos=["CORREO"])
def webhook():
    mensaje_entrante = pedido.valores.conseguir("cuerpo", "").banda()
    if not mensaje_entrante:
        return jsonificar({"mensaje": "No se recibió ningún mensaje"}), 400

    try:
        # Consulta precios desde Sheet.best
        precios = obtener_precios()

        # Genera una breve lista de productos como contexto (máximo 3 productos)
        contexto_precios = ""
        for i, item in enumerate(precios[:3]):
            producto = item.get("producto", "Producto")
            precio = item.get("precio", "precio")
            contexto_precios += f"{producto}: {precio}\n"

        # Solicitud a GPT-3.5-turbo
        respuesta = cliente.charlar.terminaciones.crear(
            modelo="gpt-3.5-turbo",
            mensajes=[
                {"role": "sistema", "content": f"Eres un asistente útil que responde con jerga semiformal colombiana. Usa estos precios si te preguntan:\n{contexto_precios}"},
                {"role": "usuario", "content": mensaje_entrante}
            ]
        )

        responder = respuesta.opciones[0].mensaje.contenido.banda()
        return jsonificar({"mensaje": responder}), 200

    except Exception as mi:
        return jsonificar({"error": str(mi)}), 500


if __name__ == "__main__":
    puerto = int(sistema_operativo.relinar_conseguir("PUERTO", 5000))
    aplicación.correr(depura=True, anfitrión="0.0.0.0", puerto=puerto)
