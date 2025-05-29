from flask import Flask, render_template, request, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
import os

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_super_secreta")

# Permitir OAuth em HTTP apenas em desenvolvimento (não use em produção sem HTTPS)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configurar blueprint do Google OAuth
google_bp = make_google_blueprint(
    client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
    redirect_url="/login/google/authorized",
    scope=["profile", "email"],
)
app.register_blueprint(google_bp, url_prefix="/login")

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    # Obter dados do usuário autenticado
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Erro ao autenticar com Google", 500

    email = resp.json().get("email", "")
    if not email.endswith("@leveros.com.br"):
        return "Acesso restrito a usuários @leveros.com.br", 403

    # Se for GET, mostrar formulário de seleção de fornecedor
    fornecedores = ['LG', 'Fujitsu', 'Daikin', 'TCL', 'Gree']
    if request.method == 'POST':
        fornecedor_escolhido = request.form.get('fornecedor', 'LG')
        session['fornecedor'] = fornecedor_escolhido
        return redirect(url_for('simulador'))

    return render_template('login.html', fornecedores=fornecedores)

@app.route('/simulador')
def simulador():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok or not resp.json().get("email", "").endswith("@leveros.com.br"):
        return "Acesso não autorizado", 403

    fornecedor = session.get('fornecedor', 'LG')
    caminho_json = f'/static/data/{fornecedor}/'
    return render_template('simulador.html', caminho_json=caminho_json, fornecedor=fornecedor)

if __name__ == "__main__":
    app.run(debug=True)
