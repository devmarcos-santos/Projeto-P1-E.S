# Projeto-P1-E.S — Imobiliária P1

Aplicação web de uma imobiliária, desenvolvida no projeto interdisciplinar do 1º período de Engenharia de Software (Programação Web 1, Introdução à Programação e Introdução à Engenharia de Software — 2026.2).

O site permite visualizar imóveis em destaque e, nas próximas entregas, cadastrar, listar, filtrar e ver detalhes de imóveis, além de contatar o anunciante.

## Tecnologias

- Python 3 e Flask
- HTML5, CSS3 e templates Jinja2
- Persistência em arquivo CSV
- Git, GitHub e GitHub Projects

## Como executar

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
python app.py
```

Depois, acesse http://127.0.0.1:5000 no navegador.

## Estrutura

```
projeto/
├── app.py              # aplicação Flask (rotas, leitura do CSV, filtros)
├── data/
│   └── imoveis.csv     # dados dos imóveis
├── static/
│   ├── css/style.css
│   └── images/logo.svg
├── templates/
│   ├── base.html       # layout comum (cabeçalho, navegação, mensagens, rodapé)
│   ├── index.html      # página inicial
│   └── erro.html       # páginas de erro
├── requirements.txt
└── README.md
```

## Gestão do projeto

- Board: [Projeto P1 E.S](https://github.com/users/devmarcos-santos/projects/1)
- Fluxo de branches: `main` (estável), `develop` (integração) e `feature/nome-da-feature`
- Commits no padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/)

## Diagramas

- Casos de uso (draw.io): _a adicionar_
- Arquitetura (cliente, servidor Flask, armazenamento CSV): _a adicionar na entrega final_
