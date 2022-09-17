from automato_finito import AutomatoFinito

automatos = []
gramaticas = []

while True:
    print("### Analisador Léxico e Sintático ###")
    print("1 - Importar autômato")
    print("2 - Visualizar autômato")
    print("3 - Exportar autômato")
    print("4 - Remover autômato")
    print("5 - Determinizar autômato")
    print("0 - Encerrar execução")
    opcao = int(input("\nEntre com uma opção: "))

    if opcao == 1:
        print("### Importar autômato ###")
        arquivo = input("Nome do arquivo: ")
        nome = input("Nome do novo autômato: ")


        automato_finito = AutomatoFinito(nome=nome)
        try:
            automato_finito.leitura(f"es/{arquivo}")
        except:
            print("Não foi possível importar o autômato")
            continue

        automatos.append(automato_finito)
        print(f"Autômato {automato_finito.nome} importado com sucesso")

    elif opcao == 2:
        print("### Visualizar autômato ###")
        for i, a in enumerate(automatos):
            print(f"{i + 1} - {a.nome}")

        try:
            id = int(input("\nEscolha o autômato: ")) - 1
            assert (id in range(0, len(automatos)))
        except:
            print("Identificador inválido")
            continue

        print(f"\nTabela de transição de {automatos[id].nome}:\n")
        automatos[id].visualiza()

    elif opcao == 3:
        print("### Exportar autômato ###")
        for i, a in enumerate(automatos):
            print(f"{i + 1} - {a.nome}")

        try:
            id = int(input("\nEscolha o autômato: ")) - 1
            assert (id in range(0, len(automatos)))
        except:
            print("Valor inválido")
            continue
        nome = automatos[id].nome
        automatos[id].salva(f"es/{nome}.txt")

        print(f"Autômato {nome} exportado")

    elif opcao == 4:
        print("### Remover autômato ###")
        for i, a in enumerate(automatos):
            print(f"{i + 1}- {a.nome}")

        try:
            id = int(input("\nEscolha o autômato (0 para cancelar): ")) - 1
            assert (id in range(-1, len(automatos)))
        except:
            print("Valor inválido")
            continue

        if id < 0:
            continue

        nome = automatos[id].nome
        del automatos[id]

        print(f"Autômato {nome} removido")

    elif opcao == 5:
        print("### Determinizar autômato ###")
        for i, a in enumerate(automatos):
            print(f"{i + 1}- {a.nome}")

        try:
            id = int(input("\nEscolha o autômato: ")) - 1
            assert (id in range(0, len(automatos)))
        except:
            print("Valor inválido")
            continue

        afd = automatos[id].getAFD()

        print(f"Autômato {automatos[id].nome} determinizado:\n")
        afd.visualiza()

        salvar = input("\nSalvar resultado (s/n)? ").strip()

        if salvar == 's':
            afd.nome = input("\nNome do novo autômato: ")
            automatos.append(afd)
            print(f"Autômato {afd.nome} inserido")

    elif opcao == 0:
        break

    else:
        continue