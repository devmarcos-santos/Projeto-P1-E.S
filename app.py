import csv
import os
from datetime import datetime
from threading import Lock

from flask import Flask, flash, abort, redirect, render_template, request, url_for

app = Flask(__name__)
# A sessão do Flask (usada pelas mensagens flash) precisa de uma chave secreta.
app.secret_key = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento")

CSV_IMOVEIS = os.path.join(app.root_path, "data", "imoveis.csv")
CSV_CONTATOS = os.path.join(app.root_path, "data", "contatos.csv")
CAMPOS_CONTATO = ["data", "imovel_id", "nome", "email", "telefone", "mensagem"]
# Evita que dois envios ao mesmo tempo escrevam no CSV de contatos juntos.
trava_csv = Lock()
CAMPOS_IMOVEL = ["id", "titulo", "tipo", "bairro", "cidade", "preco",
                 "quartos", "banheiros", "area", "imagem", "destaque"]



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

@app.route("/enviar_dados", methods=["POST"])
def enviar_dados():
  # O próximo id é o maior id que já existe + 1.
  novo_id = str(max((int(imovel["id"]) for imovel in IMOVEIS), default=0) + 1)

  imovel = {
    "id": novo_id,
    "titulo": request.form.get("anuncio_titulo", "").strip(),
    "tipo": request.form.get("imovel_tipo", "").strip(),
    "bairro": request.form.get("imovel_bairro", "").strip(),
    "cidade": request.form.get("imovel_cidade", "").strip(),
    "preco": request.form.get("anuncio_preco", "").strip(),
    "quartos": request.form.get("imovel_quartos", "").strip(),
    "banheiros": request.form.get("imovel_banheiros", "").strip(),
    "area": request.form.get("imovel_area", "").strip(),
    "imagem": "",
    "destaque": "nao",
  }

  with trava_csv:
    with open(CSV_IMOVEIS, "a", newline="", encoding="utf-8") as arquivo:
      writer = csv.DictWriter(arquivo, fieldnames=CAMPOS_IMOVEL)
      writer.writerow(imovel)
    # O CSV só é lido quando o app abre, então atualizamos a lista na memória também.
    IMOVEIS.append(imovel)

  flash("Imóvel publicado com sucesso!", "sucesso")
  return redirect(url_for("detalhes_imovel", id_imovel=novo_id))

@app.route("/financiamento")
def financiamento():
  return render_template("financiamento.html")

@app.route("/empreendimentos")
def empreendimentos():
  return render_template("empreendimentos.html")

@app.route("/imoveis")
def listar_imoveis():
  if ERRO_IMOVEIS:
    flash(ERRO_IMOVEIS, "erro")
  return render_template("imoveis.html", imoveis=IMOVEIS)

@app.route("/imoveis/<id_imovel>")
def detalhes_imovel(id_imovel):
  imovel = buscar_imovel(id_imovel)
  if imovel is None:
    abort(404)
  return render_template("detalhes_imovel.html", imovel=imovel)

@app.route("/contato", methods=["POST"])
def enviar_contato():
  imovel_id = request.form.get("imovel_id", "").strip()
  nome = request.form.get("nome", "").strip()
  email = request.form.get("email", "").strip()
  telefone = request.form.get("telefone", "").strip()
  mensagem = request.form.get("mensagem", "").strip()

  # Validação no servidor.
  if buscar_imovel(imovel_id) is None:
    abort(404)
  if not nome or "@" not in email:
    flash("Preencha o nome e um e-mail válido.", "erro")
    return redirect(url_for("detalhes_imovel", id_imovel=imovel_id))

  # Limita o tamanho para ninguém lotar o arquivo.
  nome, email = nome[:100], email[:150]
  telefone, mensagem = telefone[:20], mensagem[:1000]

  with trava_csv:
    novo = not os.path.exists(CSV_CONTATOS)
    with open(CSV_CONTATOS, "a", newline="", encoding="utf-8") as arquivo:
      writer = csv.DictWriter(arquivo, fieldnames=CAMPOS_CONTATO)
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

  return redirect(url_for("obrigado", id_imovel=imovel_id))

@app.route("/obrigado/<id_imovel>")
def obrigado(id_imovel):
  imovel = buscar_imovel(id_imovel)
  if imovel is None:
    abort(404)
  return render_template("obrigado.html", imovel=imovel)

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
