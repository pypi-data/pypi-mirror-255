# Creación de un bot simple para conversar

import os 
import openai

prompt = '''Eres la mejor ia que se dedica a responder de la manera más lógica
y coherente posible a las preguntas que te realizan los usuarios,
'''

class chatea:
      
        def __init__(self, openai_api_key, modelo="gpt-4"):
            self.openai_api_key = openai_api_key
            openai.api_key = openai_api_key
            self.modelo = modelo
            self.prompt = prompt

        def answer(self,mensaje, chat_history=[]):
  
            response = openai.ChatCompletion.create(
                          temperature=0,
                          model=self.modelo,
                          messages=[
                              {
                                  "role": "user",
                                  "content": mensaje
                              },
                              {
                                  "role": "system",
                                  "content": self.prompt
                              },
                          ]
            )

            message = response["choices"][0]["message"]["content"]
      
            return message
    
if __name__ == "__main__":
  
        openai_api_key = ""
      
        modelo = "gpt-4"
      
        # Cargar la clase 
      
        chatea = chatea(openai_api_key = openai_api_key,
                        modelo = modelo)
      
        mensaje = "dame consejos financieros"
      
        answer = chatea.answer(mensaje)
      
        print(answer)
      
        mensaje = "cuales son los puntos mas importantes de la revolución francesa?"
      
        answer = chatea.answer(mensaje)
      
        print(answer)