from automato_finito import AutomatoFinito, uniao

automatos = []
gramaticas = []

while True:
    print("### Analisador Léxico e Sintático ###")
    print("1 - Importar autômato")
    print("2 - Visualizar autômato")
    print("3 - Exportar autômato")
    print("4 - Remover autômato")
    print("5 - Determinizar autômato")
    print("6 - Minimizar autômato")
    print("7 - Unir autômatos")
    print("8 - Converter ER para AFD")
    print("0 - Encerrar execução")
    opcao = input("\nEntre com uma opção: ")

    if opcao == '1':
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

    elif opcao == '2':
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

    elif opcao == '3':
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

    elif opcao == '4':
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

    elif opcao == '5':
        print("### Determinizar autômato ###")
        for i, a in enumerate(automatos):
            print(f"{i + 1} - {a.nome}")

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

    elif opcao == '6':
        print("### Minimizar autômato ###")
        for i, a in enumerate(automatos):
            print(f"{i + 1} - {a.nome}")

        try:
            id = int(input("Escolha o autômato: ")) - 1
            assert (id in range(0, len(automatos)))
        except:
            print("Valor inválido")
            continue

        afd = automatos[id].minimiza()

        print(f"Autômato {automatos[id].nome} minimizado:\n")
        afd.visualiza()

        salvar = input("Salvar resultado (s/n)? ").strip()

        if salvar == 's':
            afd.nome = input("Nome do novo autômato: ")
            automatos.append(afd)

            print(f"Autômato {afd.nome} inserido")

    elif opcao == '7':
        print("### Unir autômatos ###")

        for i, a in enumerate(automatos):
            print(f"{i + 1} - {a.nome}")
        try:
            id1 = int(input("Escolha primeiro o autômato: ")) - 1
            assert (id1 in range(0, len(automatos)))
        except:
            print("Valor inválido")
            continue

        for i, a in enumerate(automatos):
            if i == id1: continue
            print(f"{i + 1}- {a.nome}")
        try:
            id2 = int(input("Escolha segundo o autômato: ")) - 1
            assert (id2 in range(0, len(automatos)))
        except:
            print("Valor inválido")
            continue

        print(f"{automatos[id1].nome}:\n")
        automatos[id1].visualiza()
        print(f"{automatos[id2].nome}:\n")
        automatos[id2].visualiza()

        print("Resultado da união:")
        af_uniao = uniao(automatos[id1], automatos[id2])
        af_uniao.visualiza()

        salvar = input("Salvar resultado (s/n)? ").strip()

        if salvar == 's':
            af_uniao.nome = input("Nome do novo autômato: ")
            automatos.append(af_uniao)

            print(f"Autômato {af_uniao.nome} inserido")

    elif opcao == '8':
        print(f"### Converter expressão regular para autômato finito determinístico ###")

        er = input("Digite a expressão regular: ").strip()

        af = AutomatoFinito()
        # af.leitura_er(er)

        print("\nConversão para autômato finito: ")
        # af.visualiza()

        save = input("Deseja salvar o autômato (s/n)? ").strip()

        if save == 's':
            af.nome = input("Digite o nome do novo autômato: ").strip()
            automatos.append(af)

    elif opcao == '0':
        break

    else:
        continue