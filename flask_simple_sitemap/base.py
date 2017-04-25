from flask import Blueprint, render_template, make_response


class SimpleSitemap(object):
    "Extensão Flask para publicação de sitemap"

    def __init__(self, app=None):
        """Define valores padrão para a extensão
        e caso o `app` seja informado efetua a inicialização imeditatamente
        caso o `app` não seja passado então
        a inicialização deverá ser feita depois (`lazy`)
        """
        self.config = {
            'blueprint': 'simple_sitemap',
            'url': '/sitemap.xml',
            'paths': {}
        }
        self.app = None  # indica uma extensão não inicializada

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Método que Inicializa a extensão e
        pode ser chamado de forma `lazy`.

        É interessante que este método seja apenas o `entry point` da extensão
        e que todas as operações de inicialização sejam feitas em métodos
        auxiliares privados para melhor organização e manutenção do código.
        """
        self._register(app)
        self._load_config()
        self._register_view()

    def _register(self, app):
        """De acordo com as boas práticas para extensões devemos checar se
        a extensão já foi inicializada e então falhar explicitamente caso
        seja verdadeiro.
        Se tudo estiver ok, então registramos o app.extensions e o self.app
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        if 'simple_sitemap' in app.extensions:
            raise RuntimeError("Flask extension already initialized")

        # se tudo está ok! então registramos a extensão no app.extensions!
        app.extensions['simple_sitemap'] = self

        # Marcamos esta extensão como inicializada
        self.app = app

    def _load_config(self):
        """Carrega todas as variaveis de config que tenham o prefixo `SIMPLE_SITEMAP_`
        Por exemplo, se no config estiver especificado:

            SIMPLE_SITEMAP_URL = '/sitemap.xml'

        Podemos acessar dentro da extensão da seguinte maneira:

           self.config['url']

        e isto é possível por causa do `get_namespace` do Flask utilizado abaixo.
        """
        self.config.update(
            self.app.config.get_namespace(
                namespace='SIMPLE_SITEMAP_',
                lowercase=True,
                trim_namespace=True
            )
        )

    def _register_view(self):
        """aqui registramos o blueprint contendo a rota `/sitemap.xml`"""
        self.blueprint = Blueprint(
            # O nome do blueprint deve ser unico
            # usaremos o valor informado em `SIMPLE_SITEMAP_BLUEPRINT`
            self.config['blueprint'],

            # Agora passamos o nome do módulo Python que o Blueprint
            # está localizado, o Flask usa isso para carregar os templates
            __name__,

            # informamos que a pasta de templates será a `templates`
            # já é a pasta default do Flask mas como a nossa extensão está
            # adicionando um arquivo na árvore de templates será necessário
            # informar
            template_folder='templates'
        )

        # inserimos a rota atráves do método `add_url_rule` pois fica
        # esteticamente mais bonito do que usar @self.blueprint.route()
        self.blueprint.add_url_rule(
            self.config['url'],  # /sitemap.xml é o default
            endpoint='sitemap',
            view_func=self.sitemap_view,  # usamos outro método como view
            methods=['GET']
        )

        # agora só falta registar o blueprint na app
        self.app.register_blueprint(self.blueprint)

    @property
    def paths(self):
        """Cria a lista de URLs que será adicionada ao sitemap.

        Esta property será executada apenas quando a URL `/sitemap.xml` for requisitada

        É interessante ter este método seja público pois permite que seja sobrescrito
        e é neste método que vamos misturar as URLs especificadas no config com
        as urls extraidas do roteamento do Flask (Werkzeug URL Rules).

        Para carregar URLs dinâmicamente (de bancos de dados) o usuário da extensão
        poderá sobrescrever este método ou contribur com o `SIMPLE_SITEMAP_PATHS`

        Como não queremos que exista duplicação de URLs usamos um dict onde
        a chave é a url e o valor é um dicionário completando os dados ex:

        app.config['SIMPLE_SITEMAP_PATHS'] = {
            '/artigos': {
                'lastmod': '2017-01-01'
            },
            ...
        }

        # OBS: Não tenha medo de repetir os dados! tem horas que o DRY não se
        aplica! lembre-se do Zen do Python: `praticidade vence a pureza` :)
        """

        paths = {}

        # 1) Primeiro extraimos todas as URLs registradas na app
        for rule in self.app.url_map.iter_rules():
            # Adicionamos apenas GET que não receba argumentos
            if 'GET' in rule.methods and len(rule.arguments) == 0:
                # para urls que não contém `lastmod` inicializamos com
                # um dicionário vazio
                paths[rule.rule] = {}

        # caso existam URLs que recebam argumentos então deverão ser carregadas
        # de forma dinâmica pelo usuário da extensão
        # faremos isso na hora de usar essa extensão no CMS de notícias.

        # 2) Agora carregamos URLs informadas na config
        # isso é fácil pois já temos o config carregado no _load_config
        paths.update(self.config['paths'])

        # 3) Precisamos sempre retornar o `paths` neste método pois isso permite
        # que ele seja sobrescrito com o uso de super(....)
        return paths

    def sitemap_view(self):
        "Esta é a view exposta pela url `/sitemap.xml`"
        # geramos o XML através da renderização do template `sitemap.xml`
        sitemap_xml = render_template('sitemap.xml', paths=self.paths)
        response = make_response(sitemap_xml)
        response.headers['Content-Type'] = 'application/xml'
        return response
