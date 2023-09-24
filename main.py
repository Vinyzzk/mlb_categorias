import requests
import pandas as pd
import openpyxl
import time
import os


def get_categories():
    url = "https://api.mercadolibre.com/sites/MLB/categories"
    response = requests.get(url)
    response = response.json()

    categories = []

    for category in response:
        category_id = category["id"]
        categories.append({'ID Categoria': category_id})
        print(f"[+] Adicionado: {category_id}")

    for category in categories:
        category_id = category["ID Categoria"]
        url = f"https://api.mercadolibre.com/categories/{category_id}"
        response = requests.get(url)
        category_data = response.json()

        for child_category in category_data.get("children_categories", []):
            child_category_id = child_category["id"]
            categories.append({'MLB': child_category_id})
            print(f"[+] Adicionado: {child_category_id}")

        time.sleep(0.75)

    df = pd.DataFrame(categories)
    excel_name = "Categorias"
    df.to_excel(f"{excel_name}.xlsx", index=False, engine="openpyxl")
    print(f"[+] Planilha \"{excel_name}\" gerada")
    print("[+] Pressione ENTER para sair")


def get_categories_fee():
    time_control = 0

    data = []

    df = pd.read_excel("Categorias.xlsx")
    column = df["ID Categoria"]
    categories = column.values

    categories_qty = len(categories)
    categories_logs = 0

    for mlb in categories:
        url = f"https://api.mercadolibre.com/sites/MLB/listing_prices?price=100&category_id={mlb}"
        response = requests.get(url)
        response = response.json()

        # Verifica se a lista tem elementos suficientes antes de acessar o índice
        if len(response) > 2:
            taxa_classico = str(response[2].get("sale_fee_amount", "N/A")) + "%"
            taxa_classico = taxa_classico.replace(".", ",")
        else:
            taxa_classico = "N/A"

        if len(response) > 0:
            taxa_premium = str(response[0].get("sale_fee_amount", "N/A")) + "%"
            taxa_premium = taxa_premium.replace(".", ",")
        else:
            taxa_premium = "N/A"

        url = f"https://api.mercadolibre.com/categories/{mlb}"
        response = requests.get(url)
        response = response.json()

        paths = ">".join([path["name"] for path in response.get("path_from_root", [])])

        data.append({'ID Categoria': mlb, 'Caminho': paths, 'Clássico': taxa_classico, 'Premium': taxa_premium})

        time_control += 1

        if time_control % 10 == 0:
            print("[+] 0.5 Break time")
            time.sleep(0.5)

        categories_qty -= 1
        categories_logs += 1
        print(f"[+] Gerados: {categories_logs} | Faltam: {categories_qty}")

    df = pd.DataFrame(data)
    excel_name = "Categorias + Taxas"
    df.to_excel(f"{excel_name}.xlsx", index=False, engine="openpyxl")
    print(f"[+] Planilha \"{excel_name}\" gerada")
    print("[+] Pressione ENTER para sair")


def get_categories_requirements():
    data = []

    df = pd.read_excel("result.xlsx")
    column = df["ID Categoria"]
    categories = column.values

    categories_qty = len(categories)
    categories_logs = 0
    time_control = 0

    for category in categories:

        variations = 0
        custom_fields = 0

        url = f"https://api.mercadolibre.com/categories/{category}/attributes"
        response = requests.get(url)
        if response.status_code == 200:
            category_raw = response.json()

            variations_list = []
            custom_fields_list = []
            gtin_list = []

            for i in category_raw:
                try:
                    if i["tags"]["allow_variations"]:
                        variations_list.append(i["name"])
                        variations += 1
                except KeyError:
                    continue

            for i in category_raw:
                try:
                    if i["tags"]["required"]:
                        custom_fields_list.append(i["name"])
                        custom_fields += 1
                except KeyError:
                    continue

            for i in category_raw:
                try:
                    if i["tags"]["conditional_required"]:
                        gtin_list.append("Sim")
                except KeyError:
                    continue

            data.append({'ID Categoria': category, 'Var1': variations_list[0] if len(variations_list) > 0 else "N/A",
                         'Var2': variations_list[1] if len(variations_list) > 1 else "N/A",
                         'CF1': custom_fields_list[0] if len(custom_fields_list) > 0 else "N/A",
                         'CF2': custom_fields_list[1] if len(custom_fields_list) > 1 else "N/A",
                         'GTIN': gtin_list[0] if len(gtin_list) > 0 else "N/A"})

            time_control += 1

            if time_control % 10 == 0:
                print("[+] 0.5 Break time")
                time.sleep(0.5)

            categories_qty -= 1
            categories_logs += 1
            print(f"[+] Gerados: {categories_logs} | Faltam: {categories_qty}")

    df = pd.DataFrame(data)
    excel_name = "Categorias + Campos obrigatórios"
    df.to_excel(f"{excel_name}.xlsx", index=False, engine="openpyxl")
    print(f"[+] Planilha \"{excel_name}\" gerada")
    print("[+] Pressione ENTER para sair")


def get_fee_per_mlb():
    time_control = 0

    data = []

    try:
        df = pd.read_excel("mlbs.xlsx")

        column = df["MLB"]
        mlbs = column.values

        mlbs_qty = len(mlbs)
        mlbs_logs = 0

        for mlb in mlbs:
            url = f"https://api.mercadolibre.com/items/{mlb}"
            response = requests.get(url)
            response = response.json()
            category_id = response["category_id"]

            url = f"https://api.mercadolibre.com/sites/MLB/listing_prices?price=100&category_id={category_id}"
            response = requests.get(url)
            response = response.json()

            # Verifica se a lista tem elementos suficientes antes de acessar o índice
            if len(response) > 2:
                taxa_classico = str(response[2].get("sale_fee_amount", "N/A")) + "%"
                taxa_classico = taxa_classico.replace(".", ",")
            else:
                taxa_classico = "N/A"

            if len(response) > 0:
                taxa_premium = str(response[0].get("sale_fee_amount", "N/A")) + "%"
                taxa_premium = taxa_premium.replace(".", ",")
            else:
                taxa_premium = "N/A"

            url = f"https://api.mercadolibre.com/categories/{category_id}"
            response = requests.get(url)
            response = response.json()

            paths = ">".join([path["name"] for path in response.get("path_from_root", [])])

            data.append({'MLB': mlb, 'Caminho': paths, 'Clássico': taxa_classico, 'Premium': taxa_premium})
            print(f"[+] {mlb}|{paths}|{taxa_classico}|{taxa_premium}")

            time_control += 1

            if time_control % 10 == 0:
                print("[+] 0.5 Break time")
                time.sleep(0.5)

            mlbs_qty -= 1
            mlbs_logs += 1
            print(f"[+] Gerados: {mlbs_logs} | Faltam: {mlbs_qty}")

        df = pd.DataFrame(data)
        excel_name = "MLBs + Taxas"
        df.to_excel(f"{excel_name}.xlsx", index=False, engine="openpyxl")
        print(f"[+] Planilha \"{excel_name}\" gerada")
        print("[+] Pressione ENTER para sair")

    except FileNotFoundError:
        print("[!] É preciso criar uma planilha chamada \"mlbs.xlsx\"")
        print("[!] A primeira coluna precisa chamar \"MLB\"")
        input("[!] Pressione ENTER para finalizar")
        quit()


def get_requirements_per_mlb():
    data = []

    try:
        df = pd.read_excel("mlbs.xlsx")
        column = df["MLB"]
        mlbs = column.values

        mlbs_qty = len(mlbs)
        mlbs_logs = 0

        for mlb in mlbs:
            url = f"https://api.mercadolibre.com/items/{mlb}"
            response = requests.get(url)
            response = response.json()
            category_id = response["category_id"]

            url = f"https://api.mercadolibre.com/categories/{category_id}"
            response = requests.get(url)
            response = response.json()
            paths = ">".join([path["name"] for path in response.get("path_from_root", [])])

            variations = 0
            custom_fields = 0

            url = f"https://api.mercadolibre.com/categories/{category_id}/attributes"
            response = requests.get(url)
            category_raw = response.json()

            variations_list = []
            custom_fields_list = []
            gtin_list = []

            for i in category_raw:
                try:
                    if i["tags"]["allow_variations"]:
                        variations_list.append(i["name"])
                        variations += 1
                except KeyError:
                    continue

            for i in category_raw:
                try:
                    if i["tags"]["required"]:
                        custom_fields_list.append(i["name"])
                        custom_fields += 1
                except KeyError:
                    continue

            for i in category_raw:
                try:
                    if i["tags"]["conditional_required"]:
                        gtin_list.append("Sim")
                except KeyError:
                    continue

            data.append({'MLB': mlb,
                         'Categoria': paths,
                         'Var1': variations_list[0] if len(variations_list) > 0 else "N/A",
                         'Var2': variations_list[1] if len(variations_list) > 1 else "N/A",
                         'CF1': custom_fields_list[0] if len(custom_fields_list) > 0 else "N/A",
                         'CF2': custom_fields_list[1] if len(custom_fields_list) > 1 else "N/A",
                         'GTIN': gtin_list[0] if len(gtin_list) > 0 else "N/A"})

            mlbs_qty -= 1
            mlbs_logs += 1
            print(f"[+] Gerados: {mlbs_logs} | Faltam: {mlbs_qty}")

        df = pd.DataFrame(data)
        excel_name = "MLBs + Campos obrigatórios"
        df.to_excel(f"{excel_name}.xlsx", index=False, engine="openpyxl")
        print(f"[+] Planilha \"{excel_name}\" gerada")
        print("[+] Pressione ENTER para sair")

    except FileNotFoundError:
        print("[!] É preciso criar uma planilha chamada \"mlbs.xlsx\"")
        print("[!] A primeira coluna precisa chamar \"MLB\"")
        input("[!] Pressione ENTER para finalizar")
        quit()


if __name__ == "__main__":
    options = [1, 2, 3, 4, 5]
    option = 0
    while option not in options:
        print("-----------------------------------------------")
        option = int(input(
            "[1] Refaz a planilha com todos os IDs\n"
            "[2] Refaz a planilha com as taxas (usa a opçao 1 como base)\n"
            "[3] Refaz a planilha com os campos obrigatorios\n"
            "[4] Gera uma planilha com taxas por anúncio (MLB)\n"
            "[5] Gera uma planilha com campos obrigatorios por anúncio\n"
            "R: "))

    if option == 1:
        os.system('cls')
        get_categories()
    if option == 2:
        os.system('cls')
        get_categories_fee()
    if option == 3:
        os.system('cls')
        get_categories_requirements()
    if option == 4:
        os.system('cls')
        get_fee_per_mlb()
    if option == 5:
        os.system('cls')
        get_requirements_per_mlb()
