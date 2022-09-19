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
            for state in self.K:
                for s in self.sigma:
                    if len(self.getTransicao(state, s)) > 1:
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
        for state in self.getEpsilon([self.s]):
            s += f"{state}, "
        s = s[:-2] + f"{'}'}"
        F = []

        # Obtém transições por epsilon para o estado inicial
        K[0] = self.getEpsilon(K[0])

        # Calcula o novo estado
        for k in K:
            for symbol in self.sigma:
                if symbol == '&':
                    continue

                newState = []
                for state in k: 
                    for t in self.getTransicao(state, symbol):
                        if t not in newState:
                            newState.append(t)

                # Obtém transições por epsilon para o novo estado
                newState = self.getEpsilon(newState)

                if not len(newState):
                    continue

                # Insere transição em string
                strk = str(k).replace("'", '').replace('[', '{').replace(']', '}')
                strNewState = str(newState).replace("'", '').replace('[', '{').replace(']', '}')
                delta.append((strk, symbol, strNewState))

                # Insere novo estado se ele ainda não existir
                for k0 in K:
                    if set(newState) == set(k0):
                        break
                    if k0 == K[-1]:
                        K.append(newState)

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
    pass