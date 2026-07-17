#
# funcionando para a web

from flask import Flask, render_template_string
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)


def normalize_price_text(texto):
    if not texto:
        return None

    texto = texto.strip().replace("R$", "").replace(".", "").replace(" ", "")
    if "," in texto:
        partes = texto.split(",")
        if len(partes) > 1:
            texto = partes[0] + "." + partes[1]
    return float(texto)


def monitorar_preco(url='https://lista.mercadolivre.com.br/ecoflow-delta-3?sb=all_mercadolibre#D[A:ecoflow%20delta%20%203]'):
    preco_desejado = 7500.00
    preco_atual = None

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico, options=chrome_options)

    try:
        print(f"Iniciando monitoramento em: {url}")
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(3)

        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'aceitar') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]"))
            )
            cookie_button.click()
            time.sleep(2)
        except Exception:
            print("Botão de cookies não encontrado ou já estava fechado.")

        time.sleep(5)

        elementos_preco = driver.find_elements(By.XPATH, "//*[contains(@class, 'andes-money-amount__fraction') or contains(@class, 'price-tag-fraction') or contains(@class, 'price-tag')]")
        print(f"Número de elementos encontrados: {len(elementos_preco)}")

        for elem in elementos_preco:
            texto_preco = elem.text
            if not texto_preco:
                continue
            preco_atual = normalize_price_text(texto_preco)
            if preco_atual is not None:
                print(f"Preço encontrado: {texto_preco} -> {preco_atual}")
                break

        if preco_atual is None:
            corpo_site = driver.find_element(By.TAG_NAME, "body").text
            print("Conteúdo da página recebido:")
            print(corpo_site[:2000])
            padrao_preco = re.findall(r'R\$\s?([0-9.,]+)', corpo_site)
            if padrao_preco:
                preco_atual = normalize_price_text(padrao_preco[0])
                print(f"Preço encontrado via texto: {padrao_preco[0]} -> {preco_atual}")

        if preco_atual is None:
            print("Erro: O preço não foi encontrado de nenhuma forma na página.")
            return "Preço não encontrado. A página pode estar bloqueando o acesso automatizado."

        if preco_atual <= preco_desejado:
            return f"Alerta: O preço baixou! Atualmente é R$ {preco_atual:.2f}"

        return f"Preço atual: R$ {preco_atual:.2f}"

    except Exception as e:
        print(f"Erro ao processar com Selenium: {e}")
        return "Erro ao processar com Selenium"

    finally:
        driver.quit()

@app.route('/')
def index():
    preco = monitorar_preco()
    return render_template_string('''
    <html>
    <head>
        <title>Monitoramento de Preço</title>
    </head>
    <body>
        <h1>{{ preco }}</h1>
    </body>
    </html>
    ''', preco=preco)

if __name__ == '__main__':
    app.run(debug=True)