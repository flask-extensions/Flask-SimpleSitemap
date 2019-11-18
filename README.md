# Flask Simple Sitemap

Esta extensão adiciona a funcionalidade de geração de sitemap ao seu app flask.

## Como instalar?

Para instalar basta clonar o repositório e executar:

    $ python setup.py install

Ou via `pip install flask_simple_sitemap`

## Como usar?

Basta importar e inicializar:

    from flask import Flask
    from flask_simple_sitemap import SimpleSitemap

    app = Flask(__name__)
    SimpleSitemap(app)

    @app.route('/)
    def index():
        return 'Hello World'

Como em toda extensão Flask também é possível inicializar no modo Lazy chamando
o método `init_app`

## Opções de configuração:

esta extensão utiliza o namespace de configuração `SIMPLE_SITEMAP_`

- **SIMPLE_SITEMAP_BLUEPRINT** define o nome do blueprint e do url prefix (default: `'simple_sitemap'`)
- **SIMPLE_SITEMAP_URL** define a url que irá renderizar o sitemap (default: `'/sitemap.xml'`)
- **SIMPLE_SITEMAP_PATHS** dicionário de URLs a serem adicionadas ao sitemap (exemplo: URLs criadas a partir de posts em bancos de dados)


# alternatives
[https://github.com/inveniosoftware/flask-sitemap](https://github.com/inveniosoftware/flask-sitemap)
