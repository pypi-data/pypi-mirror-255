# PySpedFiscal

Lê e serializa um arquivo do tipo Sped Fiscal

### Instalação

- `pip install pyspedfiscal`

### Dependencias

- Pydantic

### Como Usar

#### Lendo um arquivo:

```python
# Importe a classe SpedFiscal
from pyspedfiscal import SpedFiscal

# Utilize o metodo da classe `importar` para carregar um arquivo sped
sped_fiscal = SpedFiscal.importar('caminho_arquivo')

# Utilize a hierarquia do arquivo para percorrer os registros
registros_0200 = sped_fiscal.bloco_0.resgistro_0001.registros_0200

for registro in registros_0200:
  ...

```

#### Lendo um bloco:

```python

from pyspedfiscal.bloco_0 import Bloco0

bloco = """
|0000|016|0|01072022|31072022|EMPRESA TESTE|14028298000152||SP|009371438460|3550308|||A|0|
|0001|0|
|0002|00|
|0005|EMPRESA TESTE|25821270|RUA EMPRESA TESTE|1111||BAIRRO EMPRESA TESTE|2499999999|||
...
"""

registros = bloco.splitlines()

bloco_0 = Bloco0.ler_registros(registros)
```

#### Lendo um Registro

```python
from pyspedfiscal.bloco_0.registro_0000 import Registro0000

registro = "|0000|016|0|01072022|31072022|EMPRESA TESTE|14028298000152||SP|009371438460|3550308|||A|0|"

registro_0000 = Registro0000.ler_registro(registro)
```

### Registros Implementados

| Bloco 0 | Bloco B | Bloco C | Bloco D | Bloco E | Bloco G | Bloco H | Bloco G | Bloco K | Bloco 1 | Bloco 9 |
| ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- |
| 0000    | B001    | C001    |         | E001    |         |         |         |         |         | 9001    |
| 0001    | B020    | C100    |         | E100    |         |         |         |         |         | 9900    |
| 0002    | B025    | C101    |         | E110    |         |         |         |         |         | 9990    |
| 0005    | B030    | C105    |         | E115    |         |         |         |         |         | 9999    |
| 0015    | B035    | C110    |         |         |         |         |         |         |         |         |
| 0100    | B350    | C111    |         |         |         |         |         |         |         |         |
| 0150    | B420    | C112    |         |         |         |         |         |         |         |         |
| 0175    | B440    | C113    |         |         |         |         |         |         |         |         |
| 0190    | B460    | C114    |         |         |         |         |         |         |         |         |
| 0200    | B470    | C115    |         |         |         |         |         |         |         |         |
| 0205    | B500    | C116    |         |         |         |         |         |         |         |         |
| 0206    | B510    | C120    |         |         |         |         |         |         |         |         |
| 0210    | B990    | C130    |         |         |         |         |         |         |         |         |
| 0220    |         | C140    |         |         |         |         |         |         |         |         |
| 0221    |         | C160    |         |         |         |         |         |         |         |         |
| 0300    |         | C170    |         |         |         |         |         |         |         |         |
| 0305    |         | C180    |         |         |         |         |         |         |         |         |
| 0400    |         | C190    |         |         |         |         |         |         |         |         |
| 0450    |         | C195    |         |         |         |         |         |         |         |         |
| 0460    |         | C197    |         |         |         |         |         |         |         |         |
| 0500    |         |         |         |         |         |         |         |         |         |         |
| 0600    |         |         |         |         |         |         |         |         |         |         |
| 0990    |         |         |         |         |         |         |         |         |         |         |
