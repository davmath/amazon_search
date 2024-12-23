from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import pandas as pd
from time import sleep

# Configurações WebDriver
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Executa o navegador em modo headless (sem interface gráfica)
# Executa o navegador em tela cheia
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)

# Abre site da Amazon
driver.get('https://www.amazon.com.br/ref=nav_logo')
sleep(10)

# Pesquisar por livros sobre automação de processos
select_livro = driver.find_element(By.ID, 'searchDropdownBox')
select = Select(select_livro)
select.select_by_visible_text("Livros")
sleep(1)

search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
search_box.send_keys('livro automação de processos')
search_box.send_keys(Keys.RETURN)
sleep(10)

# Inicializar lista para armazenar os dados
livros = []

# Coletar dados de até 3 páginas
for page in range(1, 4):
    sleep(2)  # Aguardar carregamento da página

    # Localizar livros na página do site
    books = driver.find_elements(
        By.XPATH, ".//div[@data-component-type='s-search-result']")

    for book in books:
        try:
            # Nome do livro
            titulo = book.find_element(
                By.XPATH, './/span[@class="a-size-medium a-color-base a-text-normal"]').text
            # Nome dos autores (manejo de múltiplos autores)
            try:
                autores_spans = book.find_elements(
                    By.XPATH, ".//div[@class='a-row']/span[@class='a-size-base' and not(text()='por ') and not(contains(text(), ' | ')) and not(contains(text(), ' e outros.')) and not(contains(text(), 'jul.'))]")
                autores = ", ".join([autor.text for autor in autores_spans])
            except:
                autores = "Autor não disponível"

            # Preço (ajustando para captar livros sem desconto)
            # Preço Capa
            try:
                preco_capa_whole = book.find_element(
                    By.XPATH, ".//span[@class='a-price'][1]//span[@class='a-price-whole']").text
                preco_capa_fraction = book.find_element(
                    By.XPATH, ".//span[@class='a-price'][1]//span[@class='a-price-fraction']").text
                preco_capa = f"{preco_capa_whole},{preco_capa_fraction}".replace(
                    "R$", "").strip()  # Remove 'R$' e concatena
            except:
                preco_capa = "Preço Capa não disponível"

            '''# Preço Kindle
            try:
                preco_kindle_whole = book.find_element(By.XPATH, ".//span[@class='a-price'][2]//span[@class='a-price-whole']").text
                preco_kindle_fraction = book.find_element(By.XPATH, ".//span[@class='a-price'][2]//span[@class='a-price-fraction']").text
                preco_kindle = f"{preco_kindle_whole},{preco_kindle_fraction}".replace("R$", "").strip()  # Remove 'R$' e concatena
            
            except:
                preco_kindle = "Preço Kindle não disponível"
            '''
            # Nota média
            try:
                nota_media_element = book.find_element(
                    By.XPATH, ".//span[@aria-label]")
                nota_media_texto = nota_media_element.get_attribute(
                    "aria-label")  # Captura o valor do atributo aria-label
                nota_media = nota_media_texto.split(
                    " ")[0]  # Pega apenas a parte da nota

            except:
                nota_media = "Nota não disponível"

            # Número de avaliações
            try:
                num_avaliacoes = book.find_element(
                    By.XPATH, './/span[@class="a-size-base s-underline-text"]').text
            except:
                num_avaliacoes = "Avaliações não disponíveis"

            livros.append({
                "Nome do Livro": titulo,
                "Autores": autores,
                "Preço Capa": preco_capa,
                # "Preço Kindle": preco_kindle,
                "Nota Média": nota_media,
                "Número de Avaliações": num_avaliacoes
            })

        except Exception as e:
            print("Erro ao coletar dados: ", e)
            continue

driver.quit()

df = pd.DataFrame(livros)

# Ordenar alfabeticamente pelo nome do livro
df.sort_values(by="Nome do Livro", inplace=True)

# Salvar em um arquivo Excel
df.to_excel("livros_automacao.xlsx", index=False)

print(df)
