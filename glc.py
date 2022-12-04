import sys
from itertools import chain, groupby, product
from operator import itemgetter
from prettytable import PrettyTable

class GLC:
  """
  Uma classe usada para representar gramáticas

  Attributes
  ----------
  producoes: dict
    dicionário com as produções geradas por cada não-terminal da gramática
  N: list
    lista de itens não-terminais da gramática
  T: list
    lista de itens terminais da gramática
  firsts: dict
    dicionário com o conjunto 'First' de cada item não-terminal
  follows: dict
    dicionário com o conjunto 'Follow' de cada item não-terminal
  tabelaLL: dict
    dicionário contendo a tabela de análise preditivo LL(1)
  """

  def __init__(self, producoes):
    """
    Parameters
    ----------
    producoes: dict
      dicionário com as produções geradas por cada não-terminal da gramática
    """

    self.producoes = producoes
    self.N = [y for x in producoes.keys() for y in x if y[0].isupper()]
    self.T = [y for x in chain.from_iterable(producoes.values()) for y in x if not y in self.N]
    self.T = sorted(set(self.T))
    self.firsts = dict()
    self.follows = dict()
    self.tabelaLL = dict()
    
    if len(list(producoes.keys())[0]) != 1:
      raise Exception('Gramática inválida!')

  def isGLC(self):
    """Verifica se a gramática é livre de contexto"""

    return all([y[0].isupper() and len(x) == 1 for x in self.producoes.keys() for y in x])

  def visualiza(self):
    """Imprime a gramática em formato padrão"""

    for (nt, t) in self.producoes.items():
      print(f'{" ".join(nt)} -> {" | ".join(" ".join(x) for x in t)}')

  def calculaConjuntoFirst(self):
    """Gera o conjunto de 'First' para cada não-terminal da gramática"""

    def calculaFirst(valor):
      """
      Gera o conjunto de 'First' para um não-terminal específico da gramática
      
      Parameters
      ----------
      valor: str
        não-terminal
      """
      if valor in self.T:
        return [valor]

      first = []
      for prod in self.producoes[(valor, )]:
        if all('&' in calculaFirst(p) for p in prod if p != valor) or prod == ['&']:
          first += ['&']

        for p in prod:
          if p == valor: break
          first += [x for x in calculaFirst(p) if x != '&']
          if '&' not in calculaFirst(p): break

      return sorted(set(first))

    if GLC.eliminaRecursaoEsquerda(self).producoes.keys() != self.producoes.keys():
      raise Exception('A gramática não pode ser recursiva à esquerda!')

    self.firsts = dict()
    for n in self.N:
      self.firsts[n] = calculaFirst(n)

  def calculaConjuntoFollow(self):
    """Gera o conjunto de 'Follow' para cada não-terminal da gramática"""

    def insere(n, index):
      """
      Faz a análise de determinada produção e atualiza o conjunto 'Follows' com o resultado
      
      Parameters
      ----------
      n: str
        não-terminal
      index: int
        índice do não terminal na produção
      """

      if index == len(producao) - 1:
        follow[n] = follow.get(n, []) + follow[nt]
      elif producao[index + 1] in self.T:
        follow[n] = follow.get(n, []) + [producao[index + 1]]
      else:
        follow[n] = follow.get(n, []) + [x for x in self.firsts[producao[index + 1]] if x != '&']

        if '&' in self.firsts[producao[index + 1]]:
          insere(n, index + 1)

    self.calculaConjuntoFirst()

    follow = dict.fromkeys(self.N, [])
    follow[self.N[0]] = ['$']
    while True:
      tamanho = len([y for x in follow.values() for y in x])

      for ((nt,), producoes) in self.producoes.items():
        for producao in producoes:
          for index in range(len(producao)):
            if producao[index] in self.N:
              insere(producao[index], index)

      for key in follow.keys():
        follow[key] = sorted(set(follow[key]))

      if len([y for x in follow.values() for y in x]) == tamanho:
        break

    self.follows = follow

  def constroiTabelaLL(self):
    """Gera a tabela de análise preditivo LL(1)"""

    
    gramatica = self
    gramatica.calculaConjuntoFollow()

    
    for n in gramatica.N:
      if any(producao == ['&'] for producao in gramatica.producoes[(n, )]):
        if set(gramatica.firsts[n]) & set(gramatica.follows[n]):
          raise Exception('Interseção entre First e Follow não é vazia!')

    tabela = dict.fromkeys(product(gramatica.N, [x for x in gramatica.T if x != '&'] + ['$']), '')
    for ((nt,), producoes) in gramatica.producoes.items():
      for producao in producoes:
        for p in producao:
          firsts = gramatica.firsts.get(p, [p])

          if '&' in firsts:
            for follow in gramatica.follows[nt]:
              tabela[(nt, follow)] = producao

          for first in [x for x in firsts if x != '&']:
            tabela[(nt, first)] = producao
          
          if '&' not in firsts:
            break
    
    gramatica.tabelaLL = tabela
    cabecalhos = ["  "]
    linhas = []
    for (row, cabecalho) in tabela.keys():
      if str(cabecalho) not in cabecalhos:
        cabecalhos.append(str(cabecalho))
      if str(row) not in linhas:
        linhas.append(str(row))

    elementos = []
    for valor in tabela.values():
        elemento = ' '.join(valor)
        elementos.append(elemento)

    print(f"Tabela de análise:")
    for cabecalho in cabecalhos:
      print(f"| {cabecalho}\t\t", end="")
    print()
    for j in range(len(linhas)):
      linha = []
      linha.append(linhas[j])
      linha.append(elementos[0: len(linhas)])
      del elementos[0: len(linhas)]

      print(f"| {linha[0]}\t\t", end="")
      for i in linha[1]:
        print(f"| {i}\t\t", end="")
      print()

   
    return gramatica

  def lerEntradaLL(self, input):
    """
    Lê uma input, utilizando a tabela de análise preditivo LL(1)
    
    Parameters
    ----------
    input: str
      valor da input
    """
    
    input = input.split()
    input += ['$']

    gramatica = self
    if not self.tabelaLL:
      gramatica = self.constroiTabelaLL()
      

    pilha = ['$', gramatica.N[0]]
    lePilha = input.pop(0)

    print("Pilha:")
    while True:
      print(pilha)
      if lePilha == pilha[-1] and lePilha == '$':
        return True
      elif lePilha == pilha[-1] and lePilha != '$':
        pilha.pop()
        lePilha = input.pop(0)
      elif pilha[-1] in gramatica.N and gramatica.tabelaLL.get((pilha[-1], lePilha), ''):
        aux = gramatica.tabelaLL[(pilha.pop(), lePilha)][::-1]
        if aux != ['&']:
          pilha += aux
      else:
        return False

  def saveToFile(self, arquivo):
    """
    Salva a gramática em um arquivo especificado
    
    Parameters
    ----------
    arquivo: str
      caminho do arquivo
    """

    original_stdout = sys.stdout 
    with open(arquivo, 'w') as f:
      sys.stdout = f
      self.visualiza()
      sys.stdout = original_stdout

  @staticmethod
  def fatora(gramatica):
    
    """
    Remove a ambiguidade em produções da gramática
    
    Parameters
    ----------
    gramatica: GLC object
      instância de uma gramática
    """

    def direto(producoes):
      """
      Remove a ambiguidade direta, em produções
      
      Parameters
      ----------
      producoes: list
        lista de produções de um não terminal
      """

      contador = 1
      novasProducoes = dict()
      for elt, items in groupby(sorted(producoes), itemgetter(0)):
        items = list(items)
        if len(items) > 1:
          novasProducoes[(nt, )] = novasProducoes.get((nt, ), []) + [[elt, f'{nt}{contador}']]
          novasProducoes[(f'{nt}{contador}', )] = novasProducoes.get((f'{nt}{contador}', ), []) + [x[1:] or ['&'] for x in items]
          contador += 1
        else:
          novasProducoes[(nt, )] = novasProducoes.get((nt, ), []) + items
      return novasProducoes

    def indireto(producoes, visitados):
      """
      Deriva produções indiretas em produções diretas
      
      Parameters
      ----------
      producoes: list
        lista de produções de um não terminal
      visitados: list
        lista de não terminais já visitados
      """
      
      while True:
        lr = [prod for prod in producoes if prod[0] in gramatica.N and prod[0] not in visitados] # Produções com ambiguidade indireta
        nr = [prod for prod in producoes if prod[0] not in gramatica.N or prod[0] in visitados]  # Produções sem ambiguidade indireta
        visitados += [prod[0] for prod in lr]

        if lr:
          lr = [([] if y == ['&'] and x[1:] else y) + x[1:] for x in lr for y in producoesAntigas[(x[0],)]]
          return indireto(lr + nr, visitados)
        else:
          break
      return nr
    
    if not gramatica.isGLC():
      raise Exception('A gramática deve ser livre de contexto!')
    
    producoesAntigas = gramatica.producoes
    contador = 0
    limite = 100
    while True:
      novasProducoes = dict()
      for ((nt,), producoes) in producoesAntigas.items():
        novasProducoes.update(direto(producoes))

      contador += 1
      if contador >= limite:
        raise Exception('Limite de execuções atingido! Talvez a gramática seja inerentemente ambígua...')

      if novasProducoes == producoesAntigas:
        break
      else:
        producoesAntigas = novasProducoes
    
    while True:
      novasProducoes = dict()
      for ((nt,), producoes) in producoesAntigas.items():
        indirect = direto(indireto(producoes, [nt]))
        if len(indirect.keys()) > 1:
          novasProducoes.update(indirect)
        else:
          novasProducoes.update({(nt, ): producoesAntigas[(nt, )]})

      contador += 1
      if contador >= limite:
        raise Exception('Limite de execuções atingido! Talvez a gramática seja inerentemente ambígua...')


      if novasProducoes == producoesAntigas:
        break
      else:
        producoesAntigas = novasProducoes
    
    return GLC(novasProducoes)

  @staticmethod
  def eliminaRecursaoEsquerda(gramatica):
    """
    Remove a recursão à esquerda em produções da gramática
    
    Parameters
    ----------
    gramatica: GLC object
      instância de uma gramática
    """

    def eliminateDirectLeftRecursion(producoes):
      """
      Remove a recursão direta, em produções
      
      Parameters
      ----------
      producoes: list
        lista de produções de um não terminal
      """
      
      novasProducoes = dict()
      lr = [prod for prod in producoes if nt == prod[0]]  # Produções com recursão direta à esquerda
      nr = [prod for prod in producoes if nt != prod[0]]  # Produções sem recursão

      if lr:
        lr = [prod[1:] + [f'{nt}\''] for prod in lr] + [['&']]
        nr = [prod + [f'{nt}\''] for prod in nr] or [f'{nt}\'']

      novasProducoes[(nt, )] = nr
      if lr: novasProducoes[(f'{nt}\'', )] = lr

      return novasProducoes

    def eliminaRecursao(producoes, limite=100, contador=0):
      """
      Deriva recursões indiretas em recursões diretas
      
      Parameters
      ----------
      producoes: list
        lista de produções de um não terminal
      limite [default=100]: int
        limite de execuções
      contador [default=0]: int
        contador de execuções
      """
      while True:
        lr = [prod for prod in producoes if prod[0] in visitados]     # Produções com recursão indireta
        nr = [prod for prod in producoes if prod[0] not in visitados] # Produções sem recursão indireta

        if contador >= limite:
          raise Exception('Limite de execuções atingido! Talvez a gramática seja inerentemente recursiva...')

        if lr:
          lr = [(y if y != ['&'] else []) + x[1:] for x in lr for y in novasProducoes[(x[0],)]]
          return eliminaRecursao(lr + nr, limite, contador + 1)
        else:
          break

      return nr

    if not gramatica.isGLC():
      raise Exception('A gramática deve ser livre de contexto!')

    visitados = []
    novasProducoes = dict()
    for ((nt,), producoes) in gramatica.producoes.items():
      novasProducoes.update(eliminateDirectLeftRecursion(eliminaRecursao(producoes)))
      visitados.append(nt)

    return GLC(novasProducoes)

  @staticmethod
  def lerGramatica(arquivo):
    """
    Lê um arquivo e retorna uma gramática
    
    Parameters
    ----------
    arquivo: str
      caminho do arquivo
    """

    try:
      arq = open(arquivo).readlines()
      arq = [linha.strip().split('->') for linha in arq]

      producoes = dict()
      for linha in arq:
        if linha[0] and linha[1:][0]:
          n = linha[0].split()
          T = linha[1].split('|')
          producoes[tuple(n)] = producoes.get(tuple(n), []) + [x.split() for x in T]
    except:
      raise Exception('Arquivo inválido!')
    
    return GLC(producoes)