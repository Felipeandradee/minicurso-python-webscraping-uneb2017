import requests
from parsel import Selector


url = "http://ba.olx.com.br/animais-de-estimacao?o=2&ot=1&q=poodle"
response = requests.get(url)

itens = Selector(response.text).\
    xpath(".//a[@class='OLXad-list-link']")

for item in itens:
    titulo = item.xpath("@title").extract_first()
    link = item.xpath("@href").extract_first()
    preco = item.xpath(".//p[@class='OLXad-list-price']/text()").extract_first()
    if preco:
        print(f"titulo: {titulo} - preco: {preco} - link: {link}")