import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pywhatkit

def send_whatsapp_message(message):
    recipient_phone_number = '+5583998230829'  # Número de telefone para receber o WhatsApp (inclua o código do país)
    
    # Enviar mensagem
    pywhatkit.sendwhatmsg_instantly(phone_no=recipient_phone_number, message=message)

def monitorar_preco():
    url = 'https://lista.mercadolivre.com.br/ecoflow-delta-3?sb=all_mercadolibre#D[A:ecoflow%20delta%20%203]'
    preco_desejado = 7500.00 

    # Configurações do Chrome para rodar em segundo plano
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Não abre a janela do navegador
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Inicializa o navegador automaticamente
    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico, options=chrome_options)

    try:
        print(f"Iniciando monitoramento em: {url}")
        driver.get(url)
        time.sleep(5)  # Aguarda 5 segundos para garantir que o JavaScript carregou o preço

        # Busca qualquer elemento na tela que contenha a classe de preço do Mercado Livre
        elementos_preco = driver.find_elements(By.CLASS_NAME, "andes-money-amount__fraction")
        
        if elementos_preco:
            texto_preco = elementos_preco[0].text
            print(f"Preço encontrado via classe: {texto_preco}")
            
            preco_limpo = texto_preco.replace('.', '').replace(',', '.')
            preco_atual = float(preco_limpo)
            
            print(f"Preço atual localizado: R$ {preco_atual:.2f}")

            if preco_atual <= preco_desejado:
                message = f"Alerta: O preço do Ecoflow Delta 3 baixou! Atualmente: R$ {preco_atual:.2f}"
                send_whatsapp_message(message)
        else:
            corpo_site = driver.find_element(By.TAG_NAME, "body").text
            padrao_preco = re.findall(r'R\$\s?([0-9.,]+)', corpo_site)
            
            if padrao_preco:
                primeiro_preco = padrao_preco[0].split(',')[0]
                preco_atual = float(primeiro_preco.replace('.', ''))
                print(f"Preço atual encontrado via texto (R$): R$ {preco_atual:.2f}")
                
                if preco_atual <= preco_desejado:
                    message = f"Alerta: O preço do Ecoflow Delta 3 baixou! Atualmente: R$ {preco_atual:.2f}"
                    send_whatsapp_message(message)
            else:
                print("Erro: O preço não foi encontrado de nenhuma forma na página.")

    except Exception as e:
        print(f"Erro ao processar com Selenium: {e}")
    
    finally:
        driver.quit()  # Fecha o navegador em segundo plano

if __name__ == '__main__':
    while True:
        monitorar_preco()
        time.sleep(3600)  # Executa a cada 1 hora