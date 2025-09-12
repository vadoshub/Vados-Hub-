import http.server
import socketserver
import os
import json
from urllib.parse import parse_qs

WEB_DIR = r'/storage/emulated/0/VadosHub_Project/VadosHub'
ACCOUNTS_FILE = os.path.join(WEB_DIR, 'accounts.json')
PORT = 8000  # ✅ Defined at top-level

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        post_data = parse_qs(body)
        with open(ACCOUNTS_FILE, 'r') as f:
            accounts = json.load(f)
        response_page = ''

        if self.path == '/signup':
            email = post_data.get('email',[''])[0]
            password = post_data.get('password',[''])[0]
            fullname = post_data.get('fullname',[''])[0]
            if any(acc['email']==email for acc in accounts):
                response_page = "<h2>Email exists. Go back.</h2>"
            else:
                accounts.append({'email':email,'password':password,'fullname':fullname,'balance':0})
                with open(ACCOUNTS_FILE,'w') as f:
                    json.dump(accounts,f)
                response_page = "<h2>Account created! <a href='/login.html'>Login here</a></h2>"

        elif self.path == '/login':
            email = post_data.get('email',[''])[0]
            password = post_data.get('password',[''])[0]
            user = next((acc for acc in accounts if acc['email']==email and acc['password']==password), None)
            if user:
                response_page = f"""<!DOCTYPE html>
<html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>Dashboard - Vados Hub</title><link rel='stylesheet' href='style.css'></head>
<body>
<div class='hero-logo-container'>
<img src='images/logo.png' alt='Vados Hub Logo'>
<h1>Welcome, {user['fullname']}</h1>
<p>Balance: ${user['balance']}</p>
<form method='POST' action='/fund'>
<input type='hidden' name='email' value='{email}'>
<input type='number' name='amount' placeholder='Amount to fund' required>
<button type='submit'>Fund Account</button>
</form><br>
<button onclick="window.location.href='index.html'">Home</button>
</div></body></html>"""
            else:
                response_page = "<h2>Login failed. <a href='/login.html'>Try again</a></h2>"

        elif self.path == '/fund':
            email = post_data.get('email',[''])[0]
            amount = float(post_data.get('amount',['0'])[0])
            user = next((acc for acc in accounts if acc['email']==email), None)
            if user:
                user['balance'] += amount
                with open(ACCOUNTS_FILE,'w') as f:
                    json.dump(accounts,f)
                response_page = f"<h2>Fund successful! New balance: ${user['balance']}</h2><a href='/index.html'>Home</a>"
            else:
                response_page = "<h2>User not found.</h2>"

        elif self.path == '/reset_password':
            email = post_data.get('email',[''])[0]
            user = next((acc for acc in accounts if acc['email']==email), None)
            if user:
                user['password'] = '123456'
                with open(ACCOUNTS_FILE,'w') as f:
                    json.dump(accounts,f)
                response_page = "<h2>Password reset! New password: 123456<br><a href='/login.html'>Back to login</a></h2>"
            else:
                response_page = "<h2>Email not found. <a href='/reset_password.html'>Try again</a></h2>"

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(response_page.encode('utf-8'))

os.chdir(WEB_DIR)
with socketserver.TCPServer(('', PORT), MyHandler) as httpd:
    print(f'Serving Vados Hub at http://localhost:PORT = 8000 )
    httpd.serve_forever()
