import requests

response = requests.get('http://localhost:8080/products')
print(response.text)  # Stampa il testo della risposta
print(response.json())  # Stampa il contenuto della risposta come JSON