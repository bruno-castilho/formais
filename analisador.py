from no import No
from automatofinito import AutomatoFinito


data = {}


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
                    transicoes_desmarcadas.append([S, simbolo_entrada, D]) # Cria transição

    
        
        # Cria automato
        K = [f"Q{i}" for i in range(len(estados_desmarcados))]
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
                newTransition = [estado_string, simbolo, K[estados_desmarcados.index(seguinte)]]
                delta.append(newTransition)
                if seguinte == set() and K[estados_desmarcados.index(seguinte)] not in F:
                    F.append(K[estados_desmarcados.index(seguinte)])


        sigma = list(todos_simbolos) # Converte conjunto de símbolos para lista
        sigma.remove('#') # Remove símbolo vazio

        return AutomatoFinito(K,sigma,delta,S,F,nome)

    @staticmethod #Retorna AFND
    def uniao(af1, af2):

        af1.ajustarAutomato('Q')
        af2.ajustarAutomato('S')

        # Novo automato
        todos_estados = ['T0'] + af1.K + af2.K
        simbolos_entrada = list(dict.fromkeys(af1.sigma + af2.sigma + ['&']))
        transicoes = [['T0', '&', af1.s], ['T0', '&', af2.s]] + af1.delta + af2.delta
        estado_inicial = 'T0'
        estados_finais = af1.F + af2.F 
        nome = af1.nome + 'U' + af2.nome
        

        return AutomatoFinito(todos_estados, simbolos_entrada, transicoes, estado_inicial, estados_finais, nome)


        
    




