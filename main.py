import argparse
from analisador import AnalisadorLexico
from er import ER
from glc import GLC
from automatofinito import AutomatoFinito


#Retorna argumentos da linha da comando
def getArgumentos():
        parser = argparse.ArgumentParser(prog='ANALISADOR')
        subparsers = parser.add_subparsers(metavar='subcomando', title='subcommands', help='help',dest='subcomando')

        

        #Cria 'parser' para o sub-command 'lexico' 
        descricao_lexema = """
########################## ANALISADOR LÉXICO ##########################
PROJETO:
   Busca por expressões regulares em um arquivo de texto e gera
   AFD das mesmas. Faz a união dos autómatos e gera AFND e AFD.
 
   Necessário:
       --expressoes #Arquivo de texto contendo as expressões regulares.
 
EXECUCAO:  
   Le programa texto e valida cada lexema encontrado. Para cada lexema válido,
   imprime no arquivo tokens.txt junto com seu token. Lexemas não validos são
   apresentados no terminal.
 
   Necessário:
       --automato  #Arquivo que descreve o AF.
       --programa  #Arquivo com programa texto.
       --palavras  #Arquivo com palavras reservadas.              
        """
        descricao_ll = """
########################## ANALISADOR SINTÁTICO ##########################
EXECUCAO:  
    Le gramatica e verifica e valida se é Livre de Contexto e se é LL(1),
    elimina a recursão à esquerda e fatora quando necessário, além disso
    calcula first e follow e utilizando a tabela de analise sintatica e simulação da pilha. 
   Necessário:
       --gramatica  #Arquivo que descreve a gramática livre de contexto.
        """
        parser_lexico = subparsers.add_parser('lexico', help='lexico -h', description = descricao_lexema, formatter_class=argparse.RawTextHelpFormatter)
        parser_lexico.add_argument('opcao', metavar='opcao', choices=['PROJETO', 'EXECUCAO'], help='choices: {PROJETO,EXECUCAO}')
        parser_lexico.add_argument('-e','--expressoes', metavar='',type=str,help='arquivo de entrada (default: ./data/er.txt)')
        parser_lexico.add_argument('-a','--automato', metavar='',type=str,help='arquivo de entrada (default: ./data/AFD.txt)')
        parser_lexico.add_argument('-p','--programa', metavar='',type=str,help='arquivo de entrada (default: ./data/program.txt)')
        parser_lexico.add_argument('-w','--palavras', metavar='',type=str,help='arquivo de entrada (default: ./data/palavras_reservadas.txt)')
        parser_lexico.add_argument('-o','--output', metavar='',type=str,help='diretorio de saida (default: ./data)')

        #Cria 'parser' para o sub-command 'sintatico' 
        parser_sintatico = subparsers.add_parser('sintatico', help='sintatico -h', description = descricao_ll, formatter_class=argparse.RawTextHelpFormatter)
        parser_sintatico.add_argument('opcao', metavar='opcao', choices=['EXECUCAO'], help='choices: {EXECUCAO}')
        parser_sintatico.add_argument('-g','--gramatica', metavar='',type=str, help='arquivo de entrada (default: ./data/gramatica.txt)')
        parser_sintatico.add_argument('-s','--sentenca', metavar='',type=str, help='arquivo de entrada (default: ./data/sentenca.txt)')
        parser_sintatico.add_argument('-t','--tokens', metavar='',type=str, help='arquivo de entrada')
        parser_sintatico.add_argument('-o','--output', metavar='',type=str,help='diretorio de saida (default: ./data)')

        return  parser.parse_args()

#Retorna lista de ojetos ER
def lerERs(input):
        ref_arquivo = open(input,"r")

        ers = []
        #Ajusta as ERs e cria objeto ER
        for linha in ref_arquivo:
            valores = linha.replace("\n", "")
            valores = valores.replace(' ', '')
            valores = valores.split(":")
            
            ers.append(ER(valores[0], valores[1]))

        ref_arquivo.close()
        return ers

#Retorna lista de string
def lerLexemas(input):     
        ref_arquivo = open(input,"r")

        lexemas = []
        #Ajusta as ERs e cria objeto ER
        for linha in ref_arquivo:
            valores = linha.replace("\n", '')
            valores = valores.strip()
            if valores != '':
                for lexema in valores.split(' '):
                    if lexema != '':
                        lexemas.append(lexema)
            
        ref_arquivo.close()

        return lexemas

#Retorna lista de sentencas
def lerSentencas(input):     
        ref_arquivo = open(input,"r")

        sentencas = []
        #Ajusta as ERs e cria objeto ER
        for linha in ref_arquivo:
            if linha != '':
                sentencas.append(linha)
            
        ref_arquivo.close()

        return sentencas

#Retorna AFD
def LerAutomato(input):
        ref_arquivo = open(input,"r")
        n_estados = ref_arquivo.readline()
        estado_inicial = ref_arquivo.readline().rstrip('\n')
        estados_finais = ref_arquivo.readline().rstrip('\n').split(',')
        simbolos_entrada = ref_arquivo.readline().rstrip('\n').split(',')
        todos_estados = []
        transicoes = []

        for value in ref_arquivo:
            value = value.rstrip('\n').split(',')
            transicoes.append(value)

            if value[0] not in todos_estados:
                todos_estados.append(value[0])

            if value[2] not in todos_estados:
                todos_estados.append(value[2])


        return  AutomatoFinito(todos_estados, simbolos_entrada, transicoes, estado_inicial, estados_finais, 'Meu Automato')

#Retorna dicionario
def LerPalavrasReservadas(input):
    ref_arquivo = open(input,"r")
    dic = {}
    for value in ref_arquivo:
        value = value.rstrip('\n').strip().split(':')
        dic[value[0]] = value[1].replace(' ','').split(',')

    ref_arquivo.close()
    return dic

#Retorna tokens
def lerTokens(input):
    ref_arquivo = open(input,"r")
    string = ''
    for value in ref_arquivo:
        value = value.rstrip('\n').strip().split(':')
        string += str(value[0]) + ' '

    ref_arquivo.close()

    return [string.strip() + '\n']

#Retorna lista de ojetos AF
def erParaAFD(ERs, output):
        AFDs = []
        for er in ERs:
            nome = er.getNome()
            er = f"({er.getEr()})"
            tree = AnalisadorLexico.getArvore(er)    
            tree.calcula_followpos()
            AFD = AnalisadorLexico.erParaAFD(nome,tree)
            AFD.ajustarAutomato('Q')
            AFD.exporta(f'{output}/AFD-{nome}.txt')
            AFDs.append(AFD)

        return AFDs

#Retorna objeto AutomatoFinito
def AFDAnalisadorLexico(AFDs, output):
       
        af_uniao = AFDs[0]
        for i in range(1, len(AFDs)):
            af_uniao = AnalisadorLexico.uniao(af_uniao, AFDs[i])

        af_uniao.ajustarAutomato('Q')
        af_uniao.exporta(f'{output}/AFND.txt')
        af_uniao.determinizar()
        af_uniao.ajustarAutomato('Q')
        af_uniao.exporta(f'{output}/AFD.txt')

        return af_uniao

#Retorna lexemas validados 
def verificarLexemas(af,l):
     lexemas = []
     for lexema in l:
          if af.computar(lexema):
               lexemas.append(lexema)
          else:
               print(f'lexema não valido: {lexema}')
               
     return lexemas

#Retorna tokens e lexemas encontrados
def buscarTokens(lexemas, tokens_lexemas):
    tokens = []
    for lexema in lexemas:  
        id = True
        for token in tokens_lexemas:
           if lexema in tokens_lexemas[token]:
                tokens.append(f'{token}: {lexema}')
                id = False
                break
           
        if id: tokens.append(f'id: {lexema}')
             
    return tokens

#Escreve arquivo com tokens e lexemas:
def escreverTokens(tokens_lexemas, output):
    ref_arquivo = open(f'{output}/tokens.txt', "w")

    for token in tokens_lexemas:
        ref_arquivo.write(str(token) + "\n")
    
    
    ref_arquivo.close()
               
     
def main():
    #Pega os argumentos da linha de comando
    args = getArgumentos()
    #default --output 
    if not args.output: args.output = './data'

    #Verifica subcomando
    if args.subcomando == 'lexico':
        if args.opcao == 'PROJETO':
            #default --exprecao 
            if not args.expressoes: args.expressoes = './data/er.txt'

            #Lê ERs do arquivo 
            ERs = lerERs(args.expressoes)
            #ER -> AFD
            AFDs = erParaAFD(ERs, args.output)
            #Gera AFD para Analise léxica
            AFD = AFDAnalisadorLexico(AFDs, args.output)
           
        if args.opcao == 'EXECUCAO':
            #default --automato
            if not args.automato: args.automato = './data/AFD.txt'
            #default --programa
            if not args.programa: args.programa = './data/programa.txt'
            #default --palavras
            if not args.palavras: args.palavras = './data/palavras_reservadas.txt'

            #Ler lexemas
            lexemas = lerLexemas(args.programa)
            #Testar todos os lexemas no AFD
            AFD = LerAutomato(args.automato)
            lexemas = verificarLexemas(AFD,lexemas)
            #Buscar tokens dos lexemas em palavras_reservadas.txt
            tokens_lexemas = LerPalavrasReservadas(args.palavras) #Dic
            tokens_lexemas = buscarTokens(lexemas, tokens_lexemas) #Dic
            #Imprime arquivo tokens.txt
            escreverTokens(tokens_lexemas, args.output)

    elif args.subcomando == 'sintatico':
        if args.opcao == 'EXECUCAO':
            #default --gramatica
            if not args.gramatica: args.gramatica = './data/gramatica.txt'
            if not args.sentenca: args.sentenca = './data/sentenca.txt'

            #Lê Gramática do arquivo
            gramatica = GLC.lerGramatica(args.gramatica)

            #Fatora gramática
            gramatica = GLC.fatora(gramatica)
            
            #Elimina recursão a esquerda
            gramatica = GLC.eliminaRecursaoEsquerda(gramatica)
            
            sentencas = None
            #Ler sentencas
            if args.tokens:
                sentencas = lerTokens(args.tokens)
            else:
                sentencas = lerSentencas(args.sentenca)

            for sentenca in sentencas:
                print(f"Sentença: {sentenca}")
                print('\nEntrada válida!\n\n' if gramatica.lerEntradaLL(sentenca) else '\nEntrada inválida!\n\n')

    else:
        print('Subcomando invalido')

main()

