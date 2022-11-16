class No:
    def __init__(self, nome, filhos=[]):
        self.nome = nome
        self.filhos = filhos
        self.nulo = None
        self.firstpos = None
        self.lastpos = None
        self.followpos = set()

    def visualiza(self):
        if len(self.filhos) == 0:
            return f"{self.nome}"
        elif len(self.filhos) == 1:
            return f"{self.nome} > ({self.filhos[0].visualiza()})"
        else:
            return f"{self.nome} > ({self.filhos[0].visualiza()}, {self.filhos[1].visualiza()})"

    @staticmethod
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
            return No("|", [No.getArvore(esquerda), No.getArvore(direita)])
        
        esquerda, direita = procura_operadores('.')   # Procura por operador .
        if esquerda != "":
            # Retorna nó . com filhos da esquerda e direita calculados recursivamente
            return No(".", [No.getArvore(esquerda), No.getArvore(direita)])
        
        esquerda, direita = procura_operadores('*')   # Procura por operador *
        if esquerda != "":
            # Retorna nó * com filho calculado recursivamente
            return No("*", [No.getArvore(esquerda)])
        
        # Verifica se a expressão é algo entre parenteses
        if er[0] == "(" and er[-1] == ")":
            # Calcula recursivamente a árvore da expressão entre parenteses
            return No.getArvore(er[1:-1])

        return No(er)  # Nó não possui operadores, então é final
    

    # Retorna se nó é nullable.
    def verifica_nulo(self):
        if self.nulo is not None:  # Verifica de nulo já foi calculado
            return self.nulo

        # Calcula nulos
        if self.nome == '&' or self.nome == '*':
            self.nulo = True
        elif self.nome == '|':
            self.nulo = self.filhos[0].verifica_nulo() or self.filhos[1].verifica_nulo()
        elif self.nome == '.':
            self.nulo = self.filhos[0].verifica_nulo() and self.filhos[1].verifica_nulo()
        else:
            self.nulo = False
        
        return self.nulo
    
    # Calcula firstpos
    def calcula_firstpos(self):
        if self.firstpos is not None:  # Verifica de firstpos já foi calculado
            return self.firstpos

        # Calcula firstpos
        if self.nome == '&':
            self.firstpos = set()
        elif self.nome == '|':
            self.firstpos = self.filhos[0].calcula_firstpos().union(self.filhos[1].calcula_firstpos())
        elif self.nome == '.':
            if self.filhos[0].verifica_nulo():
                self.firstpos = self.filhos[0].calcula_firstpos().union(self.filhos[1].calcula_firstpos())
            else:
                self.firstpos = self.filhos[0].calcula_firstpos()
        elif self.nome == '*':
            self.firstpos = self.filhos[0].calcula_firstpos()
        else:
            self.firstpos = set([self])
        
        return self.firstpos
    
    # Calcula lastpos
    def calcula_lastpos(self):
        if self.lastpos is not None:   # Verifica de lastpos já foi calculado
            return self.lastpos

        # Calcula lastpos
        if self.nome == '&':
            self.lastpos = set()
        elif self.nome == '|':
            self.lastpos = self.filhos[0].calcula_lastpos().union(self.filhos[1].calcula_lastpos())
        elif self.nome == '.':
            if self.filhos[1].verifica_nulo():
                self.lastpos = self.filhos[0].calcula_lastpos().union(self.filhos[1].calcula_lastpos())
            else:
                self.lastpos = self.filhos[1].calcula_lastpos()
        elif self.nome == '*':
            self.lastpos = self.filhos[0].calcula_lastpos()
        else:
            self.lastpos = set([self])
        
        return self.lastpos
    
    # Calcula followpos
    def calcula_followpos(self):
        for filhos in self.filhos: # Faz busca em profundidade para calcular followpos
            filhos.calcula_followpos()

        if self.nome == '.': # Se é nó concatenação
            for i in self.filhos[0].calcula_lastpos(): # Para cada posição i em lastpos
                # Todas as posições em firstpos estão em followpos
                i.followpos = i.followpos.union(self.filhos[1].calcula_firstpos())
        elif self.nome == '*':  # Se é nó fechamento
            for i in self.calcula_lastpos():
                # Todas as posições em firstpos estão em followpos
                i.followpos = i.followpos.union(self.calcula_firstpos())