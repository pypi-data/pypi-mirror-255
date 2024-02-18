# Biblioteca `python-filter`

A biblioteca `python-filter` oferece classes para trabalhar com listas de forma conveniente e eficiente.

## Classes Disponíveis

- `DictListFilter`: Manipula listas de dicionários.
- `TupleListFilter`: Manipula listas de tuplas.

## Instalação

Para instalar a biblioteca, você pode usar pip:

```bash
pip install python-filter
```

## Uso

### `DictListFilter`

Esta classe permite trabalhar com listas de dicionários.

#### Exemplo de Uso:

```python
from pyfilter import DictListFilter

# Criar uma lista de dicionários
data = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"}
]

# Inicializar a classe
dict_items = DictListFilter(data)

# Exemplo de operações disponíveis
result = dict_items.get_with_key_value("id", 2)
print(result)  # Saída: {"id": 2, "name": "Bob"}
```

### `TupleListFilter`

Esta classe permite trabalhar com listas de tuplas.

#### Exemplo de Uso:

```python
from pyfilter import TupleListFilter

# Criar uma lista de tuplas
data = [
    (1, "Alice"),
    (2, "Bob"),
    (3, "Charlie")
]

# Inicializar a classe
tuple_items = TupleListFilter(data)

# Exemplo de operações disponíveis
result = tuple_items.get_with_value("Bob")
print(result)  # Saída: (2, "Bob")
```

## Contribuição

Contribuições são bem-vindas! Para sugestões, melhorias ou relatórios de bugs, sinta-se à vontade para abrir uma issue ou enviar um pull request no [repositório GitHub](https://github.com/1Marcuth/python-filter).

## Licença

Este projeto é licenciado sob a Licença MIT. Consulte o arquivo [LICENSE](https://github.com/1Marcuth/python-filter/blob/main/LICENSE) para obter detalhes.