# aliexpress-api-wrapper

A API AliExpress fornece funcionalidades para buscar produtos na plataforma AliExpress.

## Instalação

Para utilizar a API AliExpress, é necessário ter o Python instalado. Você pode instalar a API através do pip:

```bash
pip install aliexpress-api-wrapper
```

## Uso Básico

### Inicialização

Para começar a usar a API AliExpress, é necessário inicializar a classe `AliExpress`.

```python
from aliexpress_api import AliExpress

aliexpress = AliExpress(currency="USD", language="en")
```

### Métodos

#### fetch_product

Este método permite recuperar informações detalhadas sobre um produto específico. Você pode fornecer o ID do produto ou a URL do produto como entrada.

```python
product_data = aliexpress.fetch_product(id="1234567890")
```

ou

```python
product_data = aliexpress.fetch_product(url="https://www.aliexpress.com/item/1234567890.html")
```

#### search_products

Este método permite pesquisar produtos na plataforma AliExpress com base em uma consulta de pesquisa.

```python
search_results = aliexpress.search_products(query="smartphone", page_number=1)
```

## Parâmetros

### AliExpress

- `currency` (str): A moeda na qual os preços dos produtos serão exibidos. O padrão é `USD`.
- `language` (str): O idioma em que a plataforma AliExpress será exibida. O padrão é `en`.

### fetch_product

- `id` (str, opcional): O ID único do produto. Se fornecido, a URL é ignorada.
- `url` (str, opcional): A URL do produto na plataforma AliExpress. Se fornecido, o ID é ignorado.

### search_products

- `query` (str): A consulta de pesquisa para encontrar produtos na plataforma AliExpress.
- `page_number` (int, opcional): O número da página de resultados de pesquisa. O padrão é `1`.

## Retorno

Ambos os métodos `fetch_product` e `search_products` retornam um dicionário contendo informações sobre os produtos correspondentes ou os resultados da pesquisa.

## Exceções

A API pode levantar exceções em casos de falhas na comunicação com o servidor ou em situações inesperadas. Certifique-se de tratá-las adequadamente em seu código.

## Exemplo Completo

Aqui está um exemplo completo de uso da API:

```python
from minha_api_aliexpress import AliExpress

aliexpress = AliExpress(currency="USD", language="en")

product_data = aliexpress.fetch_product(id="1234567890")
print(product_data)

search_results = aliexpress.search_products(query="smartphone", page_number=1)
print(search_results)
```

Isso é tudo! Esta é a documentação básica para a API AliExpress. Sinta-se à vontade para explorar mais os métodos e personalizar conforme necessário.