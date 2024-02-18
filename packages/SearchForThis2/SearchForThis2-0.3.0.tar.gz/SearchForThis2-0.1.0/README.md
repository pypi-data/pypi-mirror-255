# Descrição
A `SearchForThis` é uma biblioteca que efetua pesquisas em motores de busca na web.

# Funcionalidades
* Realizar buscas por conteúdos desejados
* Acessar links retornados

# Biblioteca
### Instalação
```python
pip install SearchForThis
```

### Importação
```python
import SearchForThis
```
### Formas de utilização
```python
search = SearchForThis.Searchft
```
`Ou`
```python
from SearchForThis import Searchft
``` 

### Acessando métodos
Uma das formas de acessar os métodos da classe, é a seguinte:
```python
Searchft.method()
```
Onde `method`, é o nome método que você deseja utilizar.

### Realizando buscas:
Use o método `buscar` da classe, da seguinte forma:
```python
resultado = Searchft.buscar(conteúdo_da_busca, size)
```
A variável size, armazena a quantidade de links que você deseja buscar. O conteúdo da busca deve ser uma string.

### Visitando links
Use o método `visitarLink`, da seguinte forma:
```python
Searchft.visitarLink(link)
```
O link deve ser uma string.

# Exemplos de uso

### Buscar
<img src="exemplo-busca.png">
<img src="terminal-busca.png">

### VisitarLink
<img src="exemplo-visitarlink.png">
<img src="python-org.png">


Link dos exemplos com imagens: https://github.com/Liedsonfsa/pacote-poo2/blob/master/README.md
