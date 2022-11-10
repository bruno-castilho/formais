from itertools import product


class AutomatoFinito:
    def __init__(self, K=[], sigma=[], delta=[], s=None, F=[], nome=''):
        self.K = K
        self.sigma = sigma
        self.delta = delta
        self.s = s
        self.F = F
        self.nome = nome

    def leitura(self, arquivo):
        """Lê os dados do Automato Finito a partir de um arquivo
        
        número de estados
        estado inicial
        estados finais
        alfabeto
        transições (uma por linha)
        """
        with open(arquivo) as arq:
            numero_estados = arq.readline().rstrip('\n')
            estado_inicial = arq.readline().rstrip('\n')
            estados_finais = arq.readline().rstrip('\n').split(",")
            alfabeto = arq.readline().rstrip('\n').split(",")

            todos_estados = []
            transicoes = []
            while True:
                transicao = arq.readline().rstrip('\n')
                if transicao == '':
                    break
                linha = transicao.split(",")
                estado_atual = linha[0]
                todos_estados.append(estado_atual)

                elemento = linha[1]

                proximo_estado = linha[2]
                if("-" in proximo_estado):
                    proximo_estado = proximo_estado.split("-")
                    for proximo in proximo_estado:
                        transicoes.append([estado_atual, elemento, proximo])
                        todos_estados.append(proximo)
                else:
                    transicoes.append([estado_atual, elemento, proximo_estado])
                    todos_estados.append(proximo_estado)

            lista_estados = list(set(todos_estados))
            print(transicoes)
            if(int(numero_estados) == len(lista_estados)):
                self.K = lista_estados
                self.s = estado_inicial
                self.F = estados_finais
                self.sigma = alfabeto
                self.delta = transicoes
            else:
                raise Exception("Número de estados inválido")

    def visualiza(self):
        #Imprime autômato
        conteudo = 'δ'
        # Cabeçalho
        for simbolo in self.sigma:
            conteudo += '|' + simbolo
        conteudo += '\n'

        # Outras linhas
        for estado in self.K:
            estado_inicial = ''
            if estado == self.s:
                estado_inicial += '>'
            if estado in self.F:
                estado_inicial += '*'
            estado_inicial += estado

            conteudo += estado_inicial
            for simbolo in self.sigma:
                transicao = self.getTransicao(estado, simbolo)
                transicao_info = str(transicao).replace("'", '').strip()
                transicao_info = transicao_info.replace('[', '{').replace(']', '}')
                if len(transicao) == 0:
                    conteudo += '|-'
                elif len(transicao) == 1:
                    conteudo += '|' + transicao_info[1:-1]
                else:
                    conteudo += "|" + transicao_info
            conteudo += '\n'

        # Obtém lista de elementos
        linhas = conteudo.split('\n')[:-1]
        for i, linha in enumerate(linhas):
            linhas[i] = linha.split('|')

        # Descobre tamanho máximo de cada coluna
        tamanho_coluna = []
        for i in range(len(linhas[0])):
            coluna_maxima = 0
            for linha in linhas:
                if len(linha[i]) > coluna_maxima:
                    coluna_maxima = len(linha[i])
            tamanho_coluna.append(coluna_maxima + 2)

        # Cria texto com conteudo final com espaçamentos
        conteudo = ''
        for linha in linhas:
            for i, valor in enumerate(linha):
                valor_info = valor
                for j in range(tamanho_coluna[i] - len(valor_info)):
                    if j % 2 == 0:
                        valor_info = valor_info + ' '
                    else:
                        valor_info = ' ' + valor_info
                conteudo += valor_info + '|'
            conteudo = conteudo[:-1] + '\n'

        print(conteudo)

    def getTransicao(self, estado, simbolo):
        transicao = []
        for t in self.delta:
            if t[0] == estado and t[1] == simbolo:
                transicao.append(t[2])
        return transicao

    def salva(self, arquivo):
        print(arquivo)
        """Exporta o Autômato para um arquivo

        número de estados
        estado inicial
        estados finais
        alfabeto
        transições (uma por linha)
        """
        arq = open(arquivo, "w")

        arq.write(str(len(self.K)) + "\n")
        arq.write(str(self.s) + "\n")

        elementos_f = ""
        for f in self.F:
            elementos_f += f + "," 
        arq.write(elementos_f[:-1] + "\n")

        elementos_sigma = ""
        for s in self.sigma:
            elementos_sigma += s + "," 
        arq.write(elementos_sigma[:-1] + "\n")

        transicoes = []
        for i in range(len(self.delta)-1):
            if(self.delta[i][0] == self.delta[i+1][0] and self.delta[i][1] == self.delta[i+1][1] and self.delta[i][2] != self.delta[i+1][2]):
                estado_atual = self.delta[i+1][0]
                elemento = self.delta[i+1][1]
                proximo_estado = self.delta[i][2] + "-" + self.delta[i+1][2]
                transicoes.append([estado_atual, elemento, proximo_estado])
            else:
                transicoes.append(self.delta[i+1])

        for t in transicoes:
            arq.write(f"{t[0]},{t[1]},{t[2]}")
            arq.write("\n")
        arq.close()

    def getAFD(self):
        """A partir de "self", retorna um AFD equivalente"""
        # Verifica se autômato já é determinístico
        breakFor = True
        if '&' not in self.sigma:
            for estado in self.K:
                for s in self.sigma:
                    if len(self.getTransicao(estado, s)) > 1:
                        breakFor = True
                        break
                if breakFor:
                    break
        if breakFor is False:
            return self

        K = [[self.s]]
        sigma = self.sigma.copy()

        # Remove epsilon
        if '&' in sigma:
            sigma.remove('&')

        delta = []
        s = f"{'{'}"
        for estado in self.getEpsilon([self.s]):
            s += f"{estado}, "
        s = s[:-2] + f"{'}'}"
        F = []

        # Obtém transições por epsilon para o estado inicial
        K[0] = self.getEpsilon(K[0])

        # Calcula o novo estado
        for k in K:
            for simbolo in self.sigma:
                if simbolo == '&':
                    continue

                novo_estado = []
                for estado in k: 
                    for t in self.getTransicao(estado, simbolo):
                        if t not in novo_estado:
                            novo_estado.append(t)

                # Obtém transições por epsilon para o novo estado
                novo_estado = self.getEpsilon(novo_estado)

                if not len(novo_estado):
                    continue

                # Insere transição em string
                strk = str(k).replace("'", '').replace('[', '{').replace(']', '}')
                strNewestado = str(novo_estado).replace("'", '').replace('[', '{').replace(']', '}')
                delta.append((strk, simbolo, strNewestado))

                # Insere novo estado se ele ainda não existir
                for k0 in K:
                    if set(novo_estado) == set(k0):
                        break
                    if k0 == K[-1]:
                        K.append(novo_estado)

        # Define estados finais
        for k in K:
            for f in self.F:
                if f in k:
                    F.append(k)
                    break

        # Converte estados para string
        for i, k in enumerate(K):
            K[i] = str(k).replace("'", '').replace('[', '{').replace(']', '}')

        # Converte estados finais para string
        for i, f in enumerate(F):
            F[i] = str(f).replace("'", '').replace('[', '{').replace(']', '}')

        return AutomatoFinito(K, sigma, delta, s, F)

    def getEpsilon(self, estado):
        """Retorna transições por epsilon a partir de 'estado'"""
        for e in estado:
            transicao_epsilon = self.getTransicao(e, '&')
            for t in transicao_epsilon:
                if t not in estado:
                    estado.append(t)
        return estado

    def minimiza(self):
        # Processo para gerar um AutomatoFinito minimizado equivalente
        print("Autômato original:")
        self.visualiza()

        # Determiniza o autômato
        AFD = self.getAFD()

        # Remove estados inalcancaveis
        estados_inalcancaveis = AFD.K.copy()
        estados_inalcancaveis.remove(AFD.s)
        proximos_estados = [AFD.s]
        while proximos_estados:
            estado_atual = proximos_estados.pop()
            for simbolo in AFD.sigma:
                for estado in AFD.getTransicao(estado_atual, simbolo):
                    if estado in estados_inalcancaveis:
                        estados_inalcancaveis.remove(estado)
                        proximos_estados.append(estado)
        estados_alcancaveis = list(set(AFD.K.copy()).difference(set(estados_inalcancaveis)))

        # Remove estados mortos
        estados_vivos = AFD.F.copy()
        proximos_estados = estados_vivos.copy()
        while proximos_estados:
            estado_atual = proximos_estados.pop()
            for simbolo in AFD.sigma:
                for estado in AFD.getTransicaoReversa(estado_atual, simbolo):
                    if estado not in estados_vivos:
                        estados_vivos.append(estado)
                        proximos_estados.append(estado)
        estados_vivos_alcancaveis = list(set(estados_vivos).intersection(set(estados_alcancaveis)))

        # Cria classes de equivalencia
        '''
        Definicao:
        Um conjunto de estados pertencem a memsa classe de equivalencia se
        para cada simbolo, a transicoes de cada estado do conjunto pelo simbolo
        resulta a elementos de uma mesma classe de equivalencia.

        Algoritmo: ToExplain
        '''
        classes_equivalentes = [set(estados_vivos_alcancaveis).difference(set(AFD.F)), set(AFD.F).intersection(set(estados_vivos_alcancaveis))]
        while True:
            classes_novas = []
            particao = [[[] for coluna in range(len(classes_equivalentes))] for coluna in range(len(AFD.sigma))]
            for simbolo_indice, simbolo in enumerate(AFD.sigma):
                for estado in estados_vivos_alcancaveis:
                    existe_equivalencia = AFD.getTransicao(estado, simbolo)
                    if len(existe_equivalencia) == 0:
                        continue
                    existe_equivalencia = existe_equivalencia[0]
                    for classe_indice, classe_equivalente in enumerate(classes_equivalentes):
                        if existe_equivalencia in classe_equivalente:
                            particao[simbolo_indice][classe_indice].append(estado)
                            break
                    else:
                        print("Erro na minimizacao")
            particao_iterador = iter(particao)
            grupo_classe_equivalente = next(particao_iterador)
            for grupo_simbolo in particao_iterador:
                novo_grupo_classe_equivalente = [set(particao_equivalente_a).intersection(set(particao_equivalente_b)) \
                                        for particao_equivalente_a in grupo_simbolo for particao_equivalente_b in grupo_classe_equivalente \
                                        if set(particao_equivalente_a).intersection(set(particao_equivalente_b))]
                grupo_classe_equivalente = novo_grupo_classe_equivalente

            if len(grupo_classe_equivalente) - len(classes_equivalentes) == 0:
                classes_equivalentes = grupo_classe_equivalente
                break
            else:
                classes_equivalentes = grupo_classe_equivalente

        # Cria Automato
        K = [str(classe_equivalente) for classe_equivalente in classes_equivalentes]
        S = ""
        for classe_equivalente in classes_equivalentes:
            if AFD.s in classe_equivalente:
                S = str(classe_equivalente)
                break
        F = [str(classe_equivalente_F) for f in set(AFD.F).intersection(set(estados_vivos_alcancaveis)) \
                for classe_equivalente_F in classes_equivalentes if f in classe_equivalente_F]
        delta = []
        for classe_equivalente in classes_equivalentes:
            for simbolo in AFD.sigma:
                existe_equivalencia = AFD.getTransicao(list(classe_equivalente)[0], simbolo)[0]
                for outras_classes in classes_equivalentes:
                    if existe_equivalencia in outras_classes:
                        transicoes = [str(classe_equivalente), simbolo, str(outras_classes)]
                        delta.append(transicoes)
                        break

        # Correção nomes dos estados
        for estado_nome in [K, F]:
            for i, k in enumerate(estado_nome):
                print(i, k)
                estado_nome[i] = str(k).replace("'", "").replace('"', "")
        for d in delta:
            for i, k in enumerate(d):
                print("-------------")
                print(i, k)
                d[i] = str(k).replace("'", "").replace('"', "")
        S = str(S).replace("'", "").replace('"', "")

        return AutomatoFinito(K, self.sigma, delta, S, F)

    def getTransicaoReversa(self, estado, simbolo):
        """Retorna estados que transitam para 'estado' por 'simbolo'"""
        transicoes = []
        for transicao in self.delta:
            if transicao[2] == estado and transicao[1] == simbolo:
                transicoes.append(transicao[0])
        return transicoes

def uniao(af1, af2):
    """Utiliza o produto cartesiano para gerar a união de dois AFDs"""
    af1_F, af2_F, af1_K, af2_K, af_produto = produto_cartesiano(af1, af2)
    uniao_final = list(set(product(af1_F, af2_K)) | set(product(af1_K, af2_F)))
    af_produto.F = uniao_final
    produto_formatado(af_produto)
    return af_produto

def string_tupla(x): 
    return '{' + f'{x[0]},{x[1]}' + '}'

def produto_formatado(af):
    """Formatador para tuplas usadas no produto cartesiano"""

    af.K = list(map(string_tupla, af.K))
    af.F = list(map(string_tupla, af.F))
    af.s = string_tupla(af.s)
    delta = list(zip(*af.delta))
    delta[0] = list(map(string_tupla, delta[0]))
    delta[2] = list(map(string_tupla, delta[2]))
    af.delta = list(zip(*delta))

def produto_cartesiano(af1, af2, cria_estado_morto=True):
    """
    Calcula o produto cartesiano de dois autômatos finitos.
    Método auxiliar para os algoritmos de construção da união e interseção
    de AFDs por produto cartesiano (Sipser, 1.25).
    Presume-se que os AFs de entrada (af1 e af2) sejam determinísticos.
    """

    # Atualiza nomes de estados, para garantir que não haverão estados com nomes repetidos
    if len(set(af1.K).intersection(set(af2.K))) > 0:
        print('AFDs têm estados com nomes iguais. Renomeando estados.')
        estados_iguais = True
        af1_K = [estado + '-1' for estado in af1.K]
        af2_K = [estado + '-2' for estado in af2.K]
        af1_F = [estado + '-1' for estado in af1.F]
        af2_F = [estado + '-2' for estado in af2.F]
        s = (af1.s + '-1', af2.s + '-2')
    else:
        estados_iguais = False
        af1_K = af1.K
        af2_K = af2.K
        af1_F = af1.F
        af2_F = af2.F
        s = (af1.s, af2.s)

    # Se alguma transição para o morto não for explícita, temos que explicitá-la.
    if not cria_estado_morto:
        af1_K.append('morto-1')
        af2_K.append('morto-2')

    # Cria conjunto de valores de entrada
    sigma = list(set(i for i in af1.sigma + af2.sigma))
    # Cria conjunto de estados possíveis de serem usados
    uniao_K = list(product(af1_K, af2_K))

    # Define transições
    delta = []
    for q1, q2 in uniao_K:
        for simbolo in sigma:
            try:
                if estados_iguais:
                    t1 = af1.getTransicao(q1[:-2], simbolo)
                    t2 = af2.getTransicao(q2[:-2], simbolo)
                else:
                    t1 = af1.getTransicao(q1, simbolo)
                    t2 = af2.getTransicao(q2, simbolo)
                # se len > 1, o autômato não é determinístico; se
                assert (len(t1) <= 1 and len(t2) <= 1)
            except AssertionError:
                print("Ao menos um FA de entrada não era determinístico.")
                print("Use algoritmo de determinização antes de continuar :)")
            # direcionamos para o morto as transições que não forem explícitas
            if not t1:
                t1 = ['morto-1']
            if not t2:
                t2 = ['morto-2']
            transition = (t1[0] + '-1', t2[0] +
                          '-2') if estados_iguais else (t1[0], t2[0])
            delta.append(((q1, q2), simbolo, transition))
    af_produto = AutomatoFinito(uniao_K, sigma, delta, s)
    return af1_F, af2_F, af1_K, af2_K, af_produto

