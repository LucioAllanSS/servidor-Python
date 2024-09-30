from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="QuantFactory/Llama-3.2-1B-Instruct-GGUF",
    filename="Llama-3.2-1B-Instruct.Q2_K.gguf",
)

# Crear la respuesta del chat
memory = [
    {
        "role": "system",
        "content": "responde de manera concisa y clara",
    }
]

def message(user_message):
    # Agregar el nuevo mensaje del usuario
    memory.append({'role': 'user', 'content': user_message})

    try:
        # Crear la respuesta del chat
        chat = llm.create_chat_completion(
            messages=memory,
            stream=True
        )
        response = ""
        for word in chat:
            if "content" in word['choices'][0]["delta"]:
                print(word['choices'][0]["delta"]["content"], end="", flush=True)
                response += word['choices'][0]["delta"]["content"]

        # Agregar la respuesta del asistente
        memory.append({'role': 'assistant', 'content': response})
        print()
        print(memory)
        return response  # Asegúrate de devolver la respuesta como cadena de texto
    except Exception as e:
        print(f"Error: {e}")
        return "Error al generar la respuesta"

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            # Aquí puedes procesar los datos recibidos
            print("Datos recibidos:", data)

            # Llamar a la función message y obtener la respuesta
            response_message = message(data["message"])

            # Imprimir la respuesta antes de enviarla
            print("Respuesta generada:", response_message)

            # Responder al cliente
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            response_json = json.dumps({"response": response_message})
            self.send_header('Content-Length', str(len(response_json)))
            self.end_headers()
            print("Respuesta final enviada:", response_json)  # Añadir esta línea para depuración
            self.wfile.write(response_json.encode())
        except Exception as e:
            print(f"Error en do_POST: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_message = json.dumps({"error": str(e)})
            self.wfile.write(error_message.encode())


    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        with open('datos.json', 'r') as file:
            data = json.load(file)
            self.wfile.write(json.dumps(data).encode())

def run(server_class=HTTPServer, handler_class=MyHandler, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Sirviendo en el puerto {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
