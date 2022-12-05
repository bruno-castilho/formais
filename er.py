class ER:
    def __init__(self, nome, er):
        self.nome = nome
        self.er = er

        self.subistituiSimbulos()
        self.colocarConcatenacao()
        self.er += '.#'

    def subistituiSimbulos(self):
        """Troca operações ? + para seus equivalentes
            a? = (a | &)
            a+ = a.a*
        """
        string = ''
        for i in range(len(self.er)):
            symbol = self.er[i]
            if symbol in ['+', '?']:
                esp = self.parenteseReverse([i - 1])
                if symbol == '+':
                    string = string[:-len(esp)] + esp + esp + '*'
                else:
                    string = string[:-len(esp)] + "(" + esp + '|' + '&' ')'
            else:
                string += symbol
        self.er = string

    def parenteseReverse(self, index):
        if self.er[index[0]] != ')':
            return self.er[index[0]]

        string = self.er[index[0]]
        while index[0] > 0:
            index[0] -= 1
            if self.er[index[0]] == ')':
                string = self.parenteseReverse(index) + string
            else:
                string = self.er[index[0]] + string
                if self.er[index[0]] == '(':
                    return string

        return None

    def colocarConcatenacao(self):
        string = ''
        for i in range(len(self.er) - 1):
            symbol = self.er[i]
            string += symbol
            if symbol not in ['|', '.', '(']:
                if self.er[i + 1] not in ['|', '*', '.', ')']:
                    string += '.'

        string += self.er[-1]

        self.er = string

    def getEr(self):
        return self.er

    def getNome(self):
        return self.nome
