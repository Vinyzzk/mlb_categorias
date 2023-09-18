import requests
import pandas as pd
import openpyxl
import time


def get_categories():
    url = "https://api.mercadolibre.com/sites/MLB/categories"
    response = requests.get(url)
    response = response.json()

    categories = []

    for category in response:
        category_id = category["id"]
        categories.append({'ID Categoria': category_id})
        print(f"Adicionado: {category_id}")

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
        print(f"Categorias: {len(categories)}")

    df = pd.DataFrame(categories)
    df.to_excel("result.xlsx", index=False, engine="openpyxl")
    print("Excel gerado.")
    print("Pressione ENTER para sair")


def get_categories_fee():
    time_control = 0

    data = []

    df = pd.read_excel("result.xlsx")

    column = df["ID Categoria"]

    categories = column.values

    for mlb in categories:
        url = f"https://api.mercadolibre.com/sites/MLB/listing_prices?price=100&category_id={mlb}"
        response = requests.get(url)
        response = response.json()

        # Verifica se a lista tem elementos suficientes antes de acessar o índice
        if len(response) > 2:
            taxa_classico = str(response[2].get("sale_fee_amount", "N/A")) + "%"
        else:
            taxa_classico = "N/A"

        if len(response) > 0:
            taxa_premium = str(response[0].get("sale_fee_amount", "N/A")) + "%"
        else:
            taxa_premium = "N/A"

        url = f"https://api.mercadolibre.com/categories/{mlb}"
        response = requests.get(url)
        response = response.json()

        paths = ">".join([path["name"] for path in response.get("path_from_root", [])])

        data.append({'ID Categoria': mlb, 'Caminho': paths, 'Clássico': taxa_classico, 'Premium': taxa_premium})
        print(f"[+] {mlb}|{paths}|{taxa_classico}|{taxa_premium}")

        time_control += 1

        if time_control % 10 == 0:
            print("[+] 0.5 Break time")
            time.sleep(0.5)

    df = pd.DataFrame(data)
    df.to_excel("categorias.xlsx", index=False, engine="openpyxl")
    print("Excel gerado.")
    print("Pressione ENTER para sair")


def get_categories_requirements():
    data = []

    df = pd.read_excel("result.xlsx")

    column = df["ID Categoria"]

    categories = column.values

    variations = 0
    custom_fields = 0
    gtin = False

    for category in categories:
        url = f"https://api.mercadolibre.com/categories/{category}/attributes"
        response = requests.get(url)
        category_raw = response.json()

        variations_list = []
        custom_fields_list = []

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

    # for i in category_raw:
    #     try:
    #         if i["tags"]["conditional_required"]:
    #             print(f"[>] GTIN Obrigatório")
    #             gtin = True
    #     except KeyError:
    #         continue

        data.append({'ID Categoria': category, 'Var1': variations_list[0] if len(variations_list) > 0 else "N/A",
                     'Var2': variations_list[1] if len(variations_list) > 1 else "N/A",
                     'CF1': custom_fields_list[0] if len(custom_fields_list) > 0 else "N/A",
                     'CF2': custom_fields_list[1] if len(custom_fields_list) > 1 else "N/A"})

    df = pd.DataFrame(data)
    df.to_excel("categorias_campos.xlsx", index=False, engine="openpyxl")
    print("Excel gerado.")
    print("Pressione ENTER para sair")


if __name__ == "__main__":
    options = [1, 2, 3, 4]
    option = 0
    while option not in options:
        option = int(input(
            "[1] Refazer a planilha com todos os IDs\n"
            "[2] Refazer a planilha com todas as informaçoes (usa a opçao 1 como base)\n"
            "[3] Ambos (Recomendado mensalmente)\n"
            "[4] Programando...\n"
            "R: "))

    if option == 1:
        get_categories()
    if option == 2:
        get_categories_fee()
    if option == 3:
        get_categories()
        get_categories_fee()
    if option == 4:
        get_categories_requirements()
