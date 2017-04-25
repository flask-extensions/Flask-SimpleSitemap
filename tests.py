# Test Setup
# O ideal é fazer isso em forma de fixture no conftest.py

import xmltodict
from flask import Flask
from flask_simple_sitemap import SimpleSitemap

app = Flask(__name__)
extension = SimpleSitemap()

app.config['SIMPLE_SITEMAP_BLUEPRINT'] = 'test_sitemap'
app.config['SIMPLE_SITEMAP_URL'] = '/test_sitemap.xml'
app.config['SIMPLE_SITEMAP_PATHS'] = {
    '/this_is_a_test': {'lastmod': '2017-04-24'}
}


@app.route('/hello')
def hello():
    return 'Hello'


# assert lazy initialization
extension.init_app(app)

client = app.test_client()

# Testes


def test_custom_url_is_set():
    response = client.get('/test_sitemap.xml')
    assert response.status_code == 200


def test_generated_sitemap():
    response = client.get('/test_sitemap.xml')
    xml = response.data.decode('utf-8')
    result = xmltodict.parse(xml)
    assert 'urlset' in result
    # rules are Ordered
    assert result['urlset']['url'][0]['loc'] == '/test_sitemap.xml'
    assert result['urlset']['url'][1]['loc'] == '/hello'
    assert result['urlset']['url'][2]['loc'] == '/this_is_a_test'

# permite testar manualmente o app
# python tests.py
# acesse localhost:5000/test_sitemap.xml


if __name__ == '__main__':
    app.run(debug=True)
