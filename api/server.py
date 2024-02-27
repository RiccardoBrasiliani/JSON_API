import json
from http.server import BaseHTTPRequestHandler, HTTPServer #importo le librerie 
from product import Product

class RequestHandler(BaseHTTPRequestHandler):
    
    def _set_response(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/products':
            self.get_products()
        elif self.path.startswith('/products/'):
            parts = self.path.split('/')
            product_id = int(parts[2])
            self.get_product(product_id)
        else:
            self.send_error(404, 'Not Found')
            

    def get_products(self):
        records = Product.fetchAll()
        keys = ["id", "nome", "prezzo", "marca"]
        products_list = [{key: value for key, value in zip(keys, record)} for record in records]
        
        self._set_response()
        self.wfile.write(json.dumps({'data': products_list}).encode('utf-8'))



    def get_product(self, product_id):
        product = Product.find(product_id)
        if product is not None:
            product_dict = {
                'id': product.id,
                'nome': product.nome,
                'prezzo': product.prezzo,
                'marca': product.marca
            }
            self._set_response()
            self.wfile.write(json.dumps(product_dict).encode('utf-8'))
        else:
            self.send_error(404, 'Product Not Found')
            
            

    def do_POST(self):
        if self.path == '/products':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self.create_product(post_data)
        else:
            self.send_error(404, 'Not Found')

    def create_product(self, post_data):
        try:
            data = json.loads(post_data.decode('utf-8'))
            if 'nome' not in data or 'prezzo' not in data or 'marca' not in data:
                self.send_error(400, 'Bad Request - Incomplete Data')
                return
            new_product = {
                'nome': data['nome'],
                'prezzo': data['prezzo'],
                'marca': data['marca']
            }
            product = Product.create(new_product)
            self._set_response(status_code=201)
            self.wfile.write(json.dumps(product).encode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, 'Bad Request - Invalid JSON')
            
            
    def do_DELETE(self):
        if self.path.startswith('/products/'):
            parts = self.path.split('/')
            product_id = int(parts[2])
            product = Product.find(product_id)
            if product:
                self.delete_product(product)
            else:
                self.send_error(404, 'Product Not Found')
        else:
            self.send_error(404, 'Not Found')
            

    def delete_product(self, product):
        try:
            product.delete()
            self._set_response(status_code=204)  
        except Exception as e:
            self.send_error(500, f'Internal Server Error: {str(e)}')


    def do_PATCH(self):
        if self.path.startswith('/products/'):
            parts = self.path.split('/')
            product_id = int(parts[2])
            product = Product.find(product_id)
            if product:
                self.update_product(product)
            else:
                self.send_error(404, 'Product Not Found')
        else:
            self.send_error(404, 'Not Found')


            
    def update_product(self, product):
        try:
            content_length = int(self.headers['Content-Length'])
            patch_data = self.rfile.read(content_length)
            data = json.loads(patch_data.decode('utf-8'))
            
            if 'marca' not in data:
                self.send_error(400, 'Bad Request - Incomplete Data')
                return
            new_product = {
                'marca': data['marca']
            }
                
            product.update(new_product)
            self.get_product(product.id)


            #self._set_response(status_code=204)  # No Content
        except Exception as e:
            self.send_error(500, f'Internal Server Error: {str(e)}')
        
        
        

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()