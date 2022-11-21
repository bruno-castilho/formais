class AutomatoFinito:
    def __init__(self, K=[], sigma=[], delta=[], s=None, F=[], nome=''):
        self.K = K
        self.sigma = sigma
        self.delta = delta
        self.s = s
        self.F = F
        self.nome = nome
  
    def exporta(self, arquivo):
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

    def getTransicao(self, estado, simbolo):
        transicao = []
        for t in self.delta:
            if t[0] == estado and t[1] == simbolo:
                transicao.append(t[2])
        return transicao

    def determinizar(self):
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
                string_K = str(k).replace("'", '').replace('[', '{').replace(']', '}')
                string_novo_estado = str(novo_estado).replace("'", '').replace('[', '{').replace(']', '}')
                delta.append([string_K, simbolo, string_novo_estado])

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

        self.K = K
        self.sigma = sigma
        self.delta = delta
        self.s = s
        self.F = F

    def getEpsilon(self, estado):
        # Retorna transições por epsilon a partir de estado
        for e in estado: # Para cada estado
            transicao_epsilon = self.getTransicao(e, '&')
            for t in transicao_epsilon: # Para cada transição por epsilon
                if t not in estado: # Se o estado não estiver na lista de estados
                    estado.append(t) # Adiciona o estado na lista
        return estado
    
    def ajustaEstados(self):
        estados_map = {}
        i = 0
        
        for estado in self.K:
            self.s = self.s.replace(estado, 'q' + str(i))
            self.K = list(map(lambda x: x.replace(estado, 'q' + str(i)), self.K))
            self.F = list(map(lambda x: x.replace(estado, 'q' + str(i)), self.F))
            delta = []
            for d in self.delta:
                d = list(map(lambda x: x.replace(estado, 'q' + str(i)), d))
                delta.append(d)
            
            self.delta = delta

            i+=1

