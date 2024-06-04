from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import Binary, ObjectId
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import random
import datetime
import base64

uri = "mongodb+srv://sundowner:sundowner@gustavo.jcjdvok.mongodb.net/?retryWrites=true&w=majority&appName=Gustavo"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['site']
usuarios_collection = db['usuarios']
postagens_colletion = db['postagens']

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def generate_unique_code(collection=None):
    while True:
        code = random.randint(1000000000, 9999999999)
        if collection is None or not collection.find_one({"codigo": code}):
            return code


# LOGIN DO USUÁRIO
@app.route("/login")
def login():
    return render_template("Login.html")

@app.route("/process_login", methods=["POST"])
def process_login():
    email = request.form.get("email")
    senha = request.form.get("password")

    usuario = usuarios_collection.find_one({"email": email})
    if usuario and check_password_hash(usuario["hash"], senha):
        session["user_id"] = str(usuario["_id"])
        session["user_name"] = usuario["nome"]
        return redirect(url_for("inicio"))
    else:
        return redirect(url_for("login"))
    

# LOGOUT DO USUÁRIO
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# CADASTRO DE USUÁRIOS
@app.route("/cadastro")
def cadastro():
    return render_template("Cadastro.html")

@app.route("/process_cadastro", methods=["POST"])
def process_cadastro():
    nome = request.form.get("first_name")
    sobrenome = request.form.get("last_name")
    email = request.form.get("email")
    cep = request.form.get("cep")
    senha = request.form.get("password")
    confirmar_senha = request.form.get("confirm_password")
    bairro = request.form.get("bairro")
    cidade = request.form.get("cidade")
    uf = request.form.get("uf")
    senha_hash = generate_password_hash(senha)

    if senha != confirmar_senha:
        return redirect(url_for("cadastro"))
    
    if usuarios_collection.find_one({"email": email}):
        return redirect(url_for("cadastro"))

    ano_criacao = datetime.datetime.now().year
    codigo = generate_unique_code()

    usuarios_collection.insert_one({
        "nome": nome,
        "sobrenome": sobrenome,
        "email": email,
        "cep": cep,
        "bairro": bairro,
        "cidade": cidade,
        "uf": uf,
        "senha": senha,
        "hash": senha_hash,
        "ano_criacao": ano_criacao,
        "codigo": codigo
    })
    return redirect(url_for("login"))

# RECUPERAÇÃO DE CONTA
@app.route("/recuperar")
def recuperar():
    return render_template("Recuperar.html")

# PÁGINA INICIAL
@app.route("/inicio")
def inicio():
    if "user_id" not in session:
        return redirect(url_for("login"))
    else:
        user_id = session["user_id"]
        usuario = usuarios_collection.find_one({"_id": ObjectId(user_id)})
        anuncios = postagens_colletion.find()
        anuncios_list = []

        for anuncio in anuncios:
            usuario_anuncio = usuarios_collection.find_one({"_id": ObjectId(anuncio["usuario_id"])})
            anuncio['nome_usuario'] = usuario_anuncio['nome'] if usuario_anuncio else "Usuário Desconhecido"
            anuncio['fotousuario'] = base64.b64encode(usuario_anuncio['fotousuario']).decode('utf-8') if 'fotousuario' in usuario_anuncio else None

            if anuncio.get('imagem1'):
                anuncio['imagem1'] = base64.b64encode(anuncio['imagem1']).decode('utf-8')
            if anuncio.get('imagem2'):
                anuncio['imagem2'] = base64.b64encode(anuncio['imagem2']).decode('utf-8')
            anuncios_list.append(anuncio)

        return render_template("Inicio.html", anuncios=anuncios_list)

# PESQUISA DE POSTAGEM
@app.route("/search")
def search():
    title = request.args.get('title', '')
    anuncios = postagens_colletion.find({"titulo": {"$regex": title, "$options": "i"}})
    anuncios_list = []
    for anuncio in anuncios:
        usuario = usuarios_collection.find_one({"_id": ObjectId(anuncio["usuario_id"])})
        anuncio['nome_usuario'] = usuario['nome'] if usuario else "Usuário Desconhecido"
        anuncio['fotousuario'] = base64.b64encode(usuario['fotousuario']).decode('utf-8') if 'fotousuario' in usuario else None
        if anuncio.get('imagem1'):
            anuncio['imagem1'] = base64.b64encode(anuncio['imagem1']).decode('utf-8')
        if anuncio.get('imagem2'):
            anuncio['imagem2'] = base64.b64encode(anuncio['imagem2']).decode('utf-8')
        anuncios_list.append(anuncio)
    return render_template("Inicio.html", anuncios=anuncios_list)

# NOVA POSTAGEM
@app.route("/criar")
def criar():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("Criar.html")

@app.route("/processar_anuncio", methods=["POST"])
def processar_anuncio():
    if "user_id" not in session:
        return redirect(url_for("login"))

    numero_anuncios = postagens_colletion.count_documents({"usuario_id": session["user_id"]})
    if numero_anuncios >= 4:
        return redirect(url_for("inicio"))

    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    categoria = request.form.get("categoria")
    quantidade = request.form.get("quantidade")
    entrega = request.form.get("entrega")
    imagem1 = request.files['imagem1'].read() if 'imagem1' in request.files else None
    imagem2 = request.files['imagem2'].read() if 'imagem2' in request.files else None

    anuncio_id = ObjectId()
    codigo = generate_unique_code(postagens_colletion)
    data_criacao = datetime.datetime.now().strftime("%d/%m/%Y")

    postagens_colletion.insert_one({
        "_id": anuncio_id,
        "titulo": titulo,
        "descricao": descricao,
        "categoria": categoria,
        "quantidade": quantidade,
        "entrega": entrega,
        "usuario_id": session["user_id"],
        "codigo": codigo,
        "imagem1": Binary(imagem1) if imagem1 else None,
        "imagem2": Binary(imagem2) if imagem2 else None,
        "data_criacao": data_criacao
    })
    return redirect(url_for("inicio"))

# VISUALIZAR POSTAGEM
@app.route("/anuncio/<anuncio_id>")
def visualizar_anuncio(anuncio_id):
    anuncio = postagens_colletion.find_one({"_id": ObjectId(anuncio_id)})
    if not anuncio:
        return redirect(url_for("inicio"))
    
    usuario = usuarios_collection.find_one({"_id": ObjectId(anuncio["usuario_id"])})
    anuncio['nome_usuario'] = usuario['nome'] if usuario else 'usuariodesconhecido'
    anuncio['bairro'] = usuario.get('bairro')
    anuncio['cidade'] = usuario.get('cidade')
    anuncio['uf'] = usuario.get('uf')

    if anuncio.get('imagem1'):
        anuncio['imagem1'] = base64.b64encode(anuncio['imagem1']).decode('utf-8')
    if anuncio.get('imagem2'):
        anuncio['imagem2'] = base64.b64encode(anuncio['imagem2']).decode('utf-8')

    is_owner = str(anuncio["usuario_id"]) == session.get("user_id")

    return render_template("Anuncio.html", anuncio=anuncio, is_owner=is_owner)

@app.route("/excluir_anuncio/<anuncio_id>", methods=["DELETE"])
def excluir_anuncio(anuncio_id):
    anuncio = postagens_colletion.find_one({"_id": ObjectId(anuncio_id)})
    if anuncio and str(anuncio["usuario_id"]) == session.get("user_id"):
        postagens_colletion.delete_one({"_id": ObjectId(anuncio_id)})

# PERFIL DO USUÁRIO
@app.route("/perfil")
def perfil():
    if "user_id" not in session:
        return redirect(url_for("login"))

    usuario = usuarios_collection.find_one({"_id": ObjectId(session["user_id"])})
    anuncios = postagens_colletion.find({"usuario_id": session["user_id"]})

    anuncios_list = []
    for anuncio in anuncios:
        if anuncio.get('imagem1'):
            anuncio['imagem1'] = base64.b64encode(anuncio['imagem1']).decode('utf-8')
        if anuncio.get('imagem2'):
            anuncio['imagem2'] = base64.b64encode(anuncio['imagem2']).decode('utf-8')
        anuncios_list.append(anuncio)

    fotousuario = base64.b64encode(usuario['fotousuario']).decode('utf-8') if 'fotousuario' in usuario else None

    return render_template("Usuario.html",
                           nome_usuario=usuario["nome"],
                           sobrenome_usuario=usuario["sobrenome"],
                           ano_criacao=usuario["ano_criacao"],
                           id_usuario=usuario["codigo"],
                           fotousuario=fotousuario,
                           anuncios=anuncios_list)

@app.route("/upload_fotousuario", methods=["POST"])
def upload_fotousuario():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if "file" not in request.files:
        return "No file part"
    file = request.files["file"]
    if file.filename == "":
        return "No selected file"
    if file:
        filename = secure_filename(file.filename)
        file_content = file.read()

        usuarios_collection.update_one(
            {"_id": ObjectId(session["user_id"])},
            {"$set": {"fotousuario": Binary(file_content)}}
        )
        return redirect(url_for("perfil"))

if __name__ == "__main__":
    app.run(host='0.0.0.0')
