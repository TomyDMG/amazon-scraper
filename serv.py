import zipfile
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

class myHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-Description', 'File Transfer');
		self.send_header('Content-type','application/octet-stream')
		self.send_header('Content-Disposition', 'attachment; filename=amazon_bad_items.zip')
		self.send_header('Content-Transfer-Encoding', 'binary')
		self.send_header('Expires', '0')
		self.send_header('Cache-Control', 'must-revalidate')
		self.send_header('Pragma', 'public')
		self.end_headers()
		with zipfile.ZipFile('amazon.zip', 'w') as zip:
		    zip.write('cache.db')
		self.wfile.write(open('amazon.zip').read())
		return
