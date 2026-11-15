import csv
import os
from datetime import datetime
from threading import Lock

from flask import Flask, flash, abort, render_template, request

app = Flask(__name__)
# A sessão do Flask (usada pelas mensagens flash) precisa de uma chave secreta.
app.secret_key = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento")

CSV_IMOVEIS = os.path.join(app.root_path, "data", "imoveis.csv")


def carregar_imoveis():
  """Lê o CSV de imóveis. Retorna (lista de imóveis, mensagem de erro ou None)."""
  try:
    with open(CSV_IMOVEIS, newline="", encoding="utf-8") as arquivo:
      return list(csv.DictReader(arquivo)), None
  except FileNotFoundError:
    return [], "O arquivo de imóveis não foi encontrado."
  except (csv.Error, UnicodeDecodeError):
    return [], "Não foi possível ler o arquivo de imóveis."


def carregar_destaques(imoveis, limite=4):
  destaques = []
  for imovel in imoveis:
    if len(destaques) == limite:
      break
    if imovel.get("destaque", "").strip().lower() == "sim":
      destaques.append(imovel)
  return destaques

def buscar_imovel(id_imovel):
  for imovel in IMOVEIS:
    if imovel["id"] == id_imovel:
      return imovel
  return None


# Leitura do CSV na inicialização da aplicação.
IMOVEIS, ERRO_IMOVEIS = carregar_imoveis()


@app.template_filter("reais")
def formatar_reais(valor):
  try:
    numero = f"{float(valor):,.0f}".replace(",", ".")
  except (TypeError, ValueError):
    return "Preço sob consulta"
  return f"R$ {numero}"

# Rotas
@app.route("/")
def index():
  if ERRO_IMOVEIS:
    flash(ERRO_IMOVEIS, "erro")
  return render_template("index.html", destaques=carregar_destaques(IMOVEIS))

@app.route("/cadastrar_imovel")
def cadastrar_imovel():
  return render_template("publicar.html")

@app.route("/financiamento")
def financiamento():
  return render_template("financiamento.html")

@app.route("/empreendimentos")
def empreendimentos():
  return render_template("empreendimentos.html")

@app.route("/imoveis/<id_imovel>")
def detalhes_imovel(id_imovel):
  imovel = buscar_imovel(id_imovel)
  if imovel is None:
    abort(404)
  return render_template("detalhes_imovel.html", imovel=imovel)

@app.errorhandler(404)
def pagina_nao_encontrada(erro):
  return render_template(
    "erro.html",
    titulo="Página não encontrada",
    mensagem="A página que você procurou não existe ou ainda está em construção.",
  ), 404


@app.errorhandler(500)
def erro_interno(erro):
  return render_template(
    "erro.html",
    titulo="Algo deu errado",
    mensagem="Ocorreu um erro inesperado. Tente novamente em alguns instantes.",
  ), 500


if __name__ == "__main__":
  app.run(debug=True)

# csv contato

ARQ_IMOVEIS = "imoveis.csv"
ARQ_CONTATOS = "contatos.csv"
CAMPOS_CONTATO = ["data", "imovel_id", "nome", "email", "telefone", "mensagem"]
trava_csv = Lock()


def buscar_imovel(imovel_id):
    with open(ARQ_IMOVEIS, newline="", encoding="utf-8") as f:
        for imovel in csv.DictReader(f):
            if imovel["id"] == str(imovel_id):
                return imovel
    return None


@app.route("/contato", methods=["POST"])
def enviar_contato():
    imovel_id = request.form.get("imovel_id", "").strip()
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    telefone = request.form.get("telefone", "").strip()
    mensagem = request.form.get("mensagem", "").strip()

    # validação no servidor
    if not imovel_id.isdigit() or not buscar_imovel(imovel_id):
        abort(400)
    if not nome or "@" not in email:
        abort(400)

    # limita o tamanho para ninguém lotar o arquivo
    nome, email = nome[:100], email[:150]
    telefone, mensagem = telefone[:20], mensagem[:1000]

    with trava_csv:
        novo = not os.path.exists(ARQ_CONTATOS)
        with open(ARQ_CONTATOS, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_CONTATO)
            if novo:
                writer.writeheader()
            writer.writerow({
                "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "imovel_id": imovel_id,
                "nome": nome,
                "email": email,
                "telefone": telefone,
                "mensagem": mensagem,
            })
@app.route("/obrigado/<int:imovel_id>")
def obrigado(imovel_id):
    return render_template("obrigado.html", imovel=buscar_imovel(imovel_id))