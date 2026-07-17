from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def extrair_preco(driver):
    # Busca qualquer elemento na tela que contenha a classe de preço do Mercado Livre
    elementos_preco = driver.find_elements(By.CLASS_NAME, "andes-money-amount__fraction")
    
    if elementos_preco:
        texto_preco = elementos_preco[0].text
        
        # Limpa pontos e converte para número
        preco_limpo = texto_preco.replace('.', '').replace(',', '.')
        return float(preco_limpo)
    else:
        # Alternativa baseada na sua ideia: buscar pelo texto "R$" na página inteira
        corpo_site = driver.find_element(By.TAG_NAME, "body").text
        # Expressão regular para capturar padrões como R$ 1.299,00 ou R$150
        padrao_preco = re.findall(r'R\$\s?([0-9.,]+)', corpo_site)
        
        if padrao_preco:
            primeiro_preco = padrao_preco[0].split(',')[0]  # ignora centavos para simplificar
            return float(primeiro_preco.replace('.', ''))
    
    return None

def enviar_alerta(preco_atual):
    subject = "Preço Baixado!"
    body = f'O preço do produto foi baixado para R$ {preco_atual:.2f}.'
    # Aqui você pode adicionar a lógica para enviar o alerta, por exemplo, via email ou mensagem de texto
    print(body)

def monitorar_preco():
    url = 'https://www.google.com/search?q=ecoflow+delta+3+site%3Amercadolivre.com.br&oq=ec&gs_lcrp=EgZjaHJvbWUqBggAEEUYOzIGCAAQRRg7MggIARBFGCcYOzIICAIQRRgnGDsyBggDEEUYOTIGCAQQRRg8MgYIBRBFGDwyBggGEEUYPDIGCAcQRRg80gEIMTAzMGowajeoAgCwAgA&sourceid=chrome&source=chrome.ob&ie=UTF-8https://lista.mercadolivre.com.br/ecoflow-delta-3?sb=all_mercadolibre#D[A:ecoflow%20delta%20%203]'
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
        driver.get(url)
        time.sleep(5)  # Aguarda 5 segundos para garantir que o JavaScript carregou o preço
        
        preco_atual = extrair_preco(driver)
        
        if preco_atual:
            print(f"Preço atual localizado: R$ {preco_atual:.2f}")

            if preco_atual <= preco_desejado:
                enviar_alerta(preco_atual)
                print("Alerta: O preço baixou!")
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