import csv
import os

from flask import Flask, flash, abort, render_template

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
