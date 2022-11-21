from no import No
from automatofinito import AutomatoFinito
from itertools import product

class AnalisadorLexico():
    @staticmethod #Retorna Nó raiz da árvore de sintaxe
    def getArvore(er): 
        # Procura por operador e retorna parte esquerda e direita.
        def procura_operadores(operador): 
            direita, esquerda = '', ''
            parenteses = 0
            for i in range(len(er)-1, -1, -1):   # Varre ER da direita para esquerda
                # Verifica se encontrou o operador fora de qualquer parenteses
                if er[i] == operador and parenteses == 0:
                    esquerda = er[:i]
                    return esquerda, direita[::-1]
                
                # Contagem de parenteses
                if er[i] == ')':
                    parenteses += 1
                elif er[i] == '(':
                    parenteses -= 1

                direita += er[i]
            
            return esquerda, direita[::-1]

        
        esquerda, direita = procura_operadores('|')   # Procura por operador |
        if esquerda != "":
            # Retorna nó | com filhos da esquerda e direita calculados recursivamente
            return No("|", [AnalisadorLexico.getArvore(esquerda), AnalisadorLexico.getArvore(direita)])
        
        esquerda, direita = procura_operadores('.')   # Procura por operador .
        if esquerda != "":
            # Retorna nó . com filhos da esquerda e direita calculados recursivamente
            return No(".", [AnalisadorLexico.getArvore(esquerda), AnalisadorLexico.getArvore(direita)])
        
        esquerda, direita = procura_operadores('*')   # Procura por operador *
        if esquerda != "":
            # Retorna nó * com filho calculado recursivamente
            return No("*", [AnalisadorLexico.getArvore(esquerda)])
        
        # Verifica se a expressão é algo entre parenteses
        if er[0] == "(" and er[-1] == ")":
            # Calcula recursivamente a árvore da expressão entre parenteses
            return AnalisadorLexico.getArvore(er[1:-1])

        return No(er)  # Nó não possui operadores, então é final
    
    @staticmethod #Retorna AFD
    def erParaAFD(nome, arvore):
        estados_desmarcados = [arvore.calcula_firstpos()]
        S = [arvore.calcula_firstpos()]
        transicoes_desmarcadas = []
        todos_simbolos = set()
        desmarcados = [arvore.calcula_firstpos()]

        while len(desmarcados) != 0:  # Enquanto houver um símbolo desmarcado S em estados_desmarcados
            S = desmarcados.pop(0)  # Marca S como marcado

            simbolos = set() # Inicializa conjunto de símbolos
            for a in S:
                simbolos = simbolos.union(set([a.nome]))

            todos_simbolos = todos_simbolos.union(simbolos)

            for simbolo_entrada in simbolos:  # Para cada símbolo de entrada
                D = set()  # Inicializa conjunto de estados D
                for p in S:  # Para cada posição p em S
                    if p.nome == simbolo_entrada:  # Se o símbolo de entrada é igual ao símbolo de p
                        D = D.union(p.followpos)  # União followpos(p) a D
                if D not in estados_desmarcados:  # Se D não está em estados_desmarcados
                    estados_desmarcados.append(D)  # Adiciona D a estados_desmarcados
                    desmarcados.append(D)
                if (S, simbolo_entrada, D) not in transicoes_desmarcadas:  # Se (S, a, D) não está em transicoes_desmarcadas
                    transicoes_desmarcadas.append((S, simbolo_entrada, D)) # Cria transição

        for transicao in transicoes_desmarcadas:  # Remove estado morto
            estado, simbolo, seguinte = transicao
            if simbolo == '#':
                estados_desmarcados.remove(seguinte)
                break

        
        # Cria automato
        K = [f"q{i}" for i in range(len(estados_desmarcados))]
        S = K[0]
        delta = []
        F = []

        for transicao in transicoes_desmarcadas: 
            estado, simbolo, seguinte = transicao # Desempacota transição

            estado_string = K[estados_desmarcados.index(estado)] # Converte estado para string
            if simbolo == '#':
                if estado_string not in F: # Se estado não é final
                    F.append(estado_string) # Adiciona estado como final
            else:
                newTransition = (estado_string, simbolo, K[estados_desmarcados.index(seguinte)])
                delta.append(newTransition)
        sigma = list(todos_simbolos) # Converte conjunto de símbolos para lista
        sigma.remove('#') # Remove símbolo vazio

        return AutomatoFinito(K,sigma,delta,S,F,nome)

    @staticmethod #Retorna AFND
    def uniao(af1, af2):
        def string_tupla(x): 
            return '{' + f'{x[0]},{x[1]}' + '}' # Formata tupla para string

        def produto_formatado(af):
            # Formatação do produto cartesiano

            af.K = list(map(string_tupla, af.K)) 
            af.F = list(map(string_tupla, af.F))
            af.s = string_tupla(af.s)
            delta = list(zip(*af.delta)) # Desempacota delta
            delta[0] = list(map(string_tupla, delta[0]))
            delta[2] = list(map(string_tupla, delta[2]))
            af.delta = list(zip(*delta)) # Empacota delta
                
        def produto_cartesiano(af1, af2, cria_estado_morto=True):
            # É necessário que os automatos de entrada (af1 e af2) sejam determinísticos.

            # Verifica se há estados com mesmo nome
            if len(set(af1.K).intersection(set(af2.K))) > 0:
                estados_iguais = True
                af1_K = [estado + '-1' for estado in af1.K]
                af2_K = [estado + '-2' for estado in af2.K]
                af1_F = [estado + '-1' for estado in af1.F]
                af2_F = [estado + '-2' for estado in af2.F]
                s = (af1.s + '-1', af2.s + '-2') # Sufixo -1 para af1 e -2 para af2
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
                        # Se tamanho > 1, o autômato não é determinístico
                        assert (len(t1) <= 1 and len(t2) <= 1)
                    except AssertionError:
                        print("Um dos autômatos não é determinístico.")

                    # Se não há transição, cria-se estado morto
                    if not t1: 
                        t1 = ['morto-1']
                    if not t2:
                        t2 = ['morto-2']
                    
                    # Adiciona sufixo se estados iguais
                    transicao = (t1[0] + '-1', t2[0] + '-2') if estados_iguais else (t1[0], t2[0])
                    delta.append(((q1, q2), simbolo, transicao))
            af_produto = AutomatoFinito(uniao_K, sigma, delta, s)
            return af1_F, af2_F, af1_K, af2_K, af_produto    

        # União de dois AFDs utilizando o produto cartesiano
        af1_F, af2_F, af1_K, af2_K, af_produto = produto_cartesiano(af1, af2)
        uniao_final = list(set(product(af1_F, af2_K)) | set(product(af1_K, af2_F)))
        af_produto.F = uniao_final
        produto_formatado(af_produto)

        return af_produto




