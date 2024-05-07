from flask import Flask, redirect, request, url_for ,render_template ,session
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
YOUR_CHANNEL_ID = os.environ.get("YOUR_CHANNEL_ID")
YOUR_REDIRECT_URI = os.environ.get("YOUR_REDIRECT_URI")
YOUR_CHANNEL_SECRET = os.environ.get("YOUR_CHANNEL_SECRET")

@app.route('/')
def index():
    user_name = session.get('user_name')
    user_logged_in = 'access_token' in session
    return render_template('index.html', user_logged_in=user_logged_in, user_name=user_name)


@app.route('/login')
def login():
    return redirect(f'https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={YOUR_CHANNEL_ID}&redirect_uri={YOUR_REDIRECT_URI}&state=12345abcde&scope=profile%20openid')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "認証コードがありません。"
    token_url = 'https://api.line.me/oauth2/v2.1/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': YOUR_REDIRECT_URI,
        'client_id': YOUR_CHANNEL_ID,
        'client_secret': YOUR_CHANNEL_SECRET  
    }
    response = requests.post(token_url, headers=headers, data=data)
    token_info = response.json()
    if 'access_token' in token_info:
        session['access_token'] = token_info['access_token']
        
        # ユーザーの情報
        profile_url = 'https://api.line.me/v2/profile'
        profile_headers = {'Authorization': f'Bearer {token_info["access_token"]}'}
        profile_response = requests.get(profile_url, headers=profile_headers)
        profile_info = profile_response.json()
        session['user_name'] = profile_info.get('displayName', '名無し')
        return redirect(url_for('index'))
    else:
        return "アクセストークンの取得に失敗しました。"

if __name__ == "__main__":
    app.run(debug=True)
