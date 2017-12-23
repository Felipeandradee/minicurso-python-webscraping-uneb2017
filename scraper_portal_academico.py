import configparser
from time import sleep
from datetime import datetime

import requests
from parsel import Selector

# Carrega o usuario e senha do portal academico
config = configparser.ConfigParser()
config.read('env.ini')
user = config['portal_academico']['user']
password = config['portal_academico']['pass']

# URL base do Portal Academico da UNEB
base_url = 'http://www.portalacademico.uneb.br'

print(f"{datetime.now()} - Acessando pagina de login")
response = requests.get(base_url)

# Pega essas informações da pagina para passar como parametros do POST
view_state = Selector(response.text).xpath(".//*[@id='__VIEWSTATE']/@value").extract_first()
view_state_generator = Selector(response.text).xpath(".//*[@id='__VIEWSTATEGENERATOR']/@value").extract_first()
event_validation = Selector(response.text).xpath(".//*[@id='__EVENTVALIDATION']/@value").extract_first()

# Monta um dict com as informações necessarias para logar no portal
payload = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': view_state,
    '__VIEWSTATEGENERATOR': view_state_generator,
    '__EVENTVALIDATION': event_validation,
    'ctl00$PageContent$LoginPanel$UserName': user,
    'ctl00$PageContent$LoginPanel$Password': password,
    'ctl00$PageContent$LoginPanel$LoginButton': 'Entrar',
}

print(f"{datetime.now()} - Logando no site")

url = base_url + '/PortalSagres/Acesso.aspx'
response = requests.post(url, data=payload, cookies=response.cookies)

n = 0
while True:
    url = base_url + '/PortalSagres/Modules/Diario/Aluno/Relatorio/Boletim.aspx?op=notas'
    n += 1
    print(f"{datetime.now()} - Acessando pagina de boletim, pela {n} vez")

    response = requests.get(url, cookies=response.request._cookies)

    # Pega a div que tem as informações das materias
    materias = Selector(response.text).xpath(".//div[@class='boletim-item']")

    for materia in materias:
        titulo =\
            materia.xpath(".//span[contains(@class,'boletim-item-titulo')]/text()").re('(^.+) - ([\w ]+) \(.+\)$')[1]

        # Pega a média da matéria
        media = materia.xpath(
            ".//span[@id='ctl00_MasterPlaceHolder_ucRepeater_ctl06_ucItemBoletim_lblMedia']/text()").extract_first()

        # Pega todas as notas
        nota = materia.xpath(
            "..//div[@class='boletim-notas']//td[@class='txt-center']/span/text()").extract()

        faltas = materia.xpath(".//span[@class='cabecalho_numero_faltas']/text()").extract_first()
        faltas = int(faltas.split()[0])
        print(titulo)
        print(f"{datetime.now()} - Média: {media}, Notas: " + " - ".join(nota) + f" pode faltar {15-faltas} vezes")

    # Espera 20 minutos(1200 segundos) para verificar novamente.
    sleep(1200)
