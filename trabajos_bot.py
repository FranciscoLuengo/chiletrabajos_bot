import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DS_WEBHOOK")
CHILETRABAJOS_URL = os.getenv("URL_TRABAJO")
ARCHIVO_VISTOS = "vistos.json"


def cargar_vistos():
    try:
        with open(ARCHIVO_VISTOS, "r") as f:
            return json.load(f)
    except:
        return []


def guardar_vistos(lista):
    with open(ARCHIVO_VISTOS, "w") as f:
        json.dump(lista, f)


def enviar_discord(mensaje):
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": mensaje})
    if response.status_code != 204:
        print("Error al enviar mensaje a Discord:", response.text)


def scrapear():
    print("🔍 Buscando nuevas ofertas de trabajo...")
    vistos = cargar_vistos()

    r = requests.get(CHILETRABAJOS_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    nuevas = []
    trabajos = soup.select("div.job-item")

    for trabajo in trabajos:
        titulo_tag = trabajo.select_one("h2.title a")
        # descripcion_tag = trabajo.select_one("p.description")
        fecha_tag = trabajo.select("h3.meta")

        if not titulo_tag:
            continue

        titulo = titulo_tag.text.strip()
        url = titulo_tag["href"]
        # descripcion = descripcion_tag.text.strip().replace(
        #     "\n", " ") if descripcion_tag else "Sin descripción"
        fecha = fecha_tag[1].text.strip() if len(
            fecha_tag) > 1 else "Fecha no disponible"

        if titulo not in vistos:
            mensaje = (
                f"💼 **{titulo}**\n"
                f"📅 Publicado: {fecha}\n"
                # f"📝 {descripcion}\n"
                f"🔗 [Ver oferta]({url})"
            )
            enviar_discord(mensaje)
            nuevas.append(titulo)
            print("✅ Enviado:", titulo)

    if not nuevas:
        print("🚫 No hay nuevas ofertas nuevas.")

    guardar_vistos(vistos + nuevas)


if __name__ == "__main__":
    scrapear()
