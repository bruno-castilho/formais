import argparse
from analisador import AnalisadorLexico
from er import ER

#Retorna argumentos da linha da comando
def getArgumentos():
        parser = argparse.ArgumentParser(prog='ANALISADOR')
        subparsers = parser.add_subparsers(metavar='subcomando', title='subcommands', help='help',dest='subcomando')


        #Cria 'parser' para o sub-command 'lexico' 
        parser_lexico = subparsers.add_parser('lexico', help='lexico -h')
        parser_lexico.add_argument('opcao', metavar='opcao', choices=['projeto', 'execucao'], help='choices: {projeto,execucao}')
        parser_lexico.add_argument('-i','--input', metavar='',type=str,help='arquivo de entrada (default: ./)')
        parser_lexico.add_argument('-o','--output', metavar='',type=str,help='diretorio de saida (default: ./)')

        #Cria 'parser' para o sub-command 'sintatico' 
        parser_sintatico = subparsers.add_parser('sintatico', help='sintatico -h')
        parser_sintatico.add_argument('-i','--input', metavar='',type=str, help='arquivo de entrada (default: ./)')
        parser_sintatico.add_argument('-o','--output', metavar='',type=str, help='diretorio de saida (default: ./)')


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

        return ers

#Retorna lista de ojetos AF
def erParaAFD(ERs, output):
        AFDs = []
        for er in ERs:
            nome = er.getNome()
            tree = AnalisadorLexico.getArvore(er.getEr())    
            tree.calcula_followpos()
            AFD = AnalisadorLexico.erParaAFD(nome,tree)
            AFD.exporta(f'{output}/AFD-{nome}.txt')
            AFDs.append(AFD)

        return AFDs

#Retorna objeto AutomatoFinito
def AFDAnalisadorLexico(AFDs, output):
        af_uniao = AFDs[0]
        for i in range(1, len(AFDs)):
            af_uniao = AnalisadorLexico.uniao(af_uniao, AFDs[i])
            af_uniao.determinizar()

        af_uniao.ajustaEstados()
        af_uniao.exporta(f'{output}/AFD-ERs.txt')

        return af_uniao

def main():
    #Pega os argumentos da linha de comando
    args = getArgumentos()

    #Verifica subcomando
    if args.subcomando == 'lexico':
        if args.opcao == 'projeto':
            #default --input 
            if not args.input: args.input = './data/er.txt'
            #default --output 
            if not args.output: args.output = './data'

            #Lê ERs do arquivo 
            ERs = lerERs(args.input)
            #ER -> AFD
            AFDs = erParaAFD(ERs, args.output)
            #Gera AFD para Analise léxica
            AFD = AFDAnalisadorLexico(AFDs, args.output)
           
        if args.opcao == 'execucao':
            print('"Lexico execucao" em construção')

    elif args.subcomando == 'sintatico':
         print('"Sintatico" em construção')
    else:
        print('Subcomando invalido')

main()

