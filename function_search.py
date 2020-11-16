import requests
import string
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import logging


stop_wrods = [
    'alors', 'au', 'aucuns', 'aussi', 'autre', 'avant', 'avec', 'avoir', 'bon',
    'car', 'ce', 'cela', 'ces', 'ceux', 'chaque', 'ci', 'comme', 'comment',
    'dans', 'des', 'du', 'dedans', 'dehors', 'depuis', 'devrait', 'doit',
    'donc', 'dos', 'début', 'elle', 'elles', 'en', 'encore', 'essai', 'est',
    'et', 'eu', 'fait', 'faites', 'fois', 'font', 'hors', 'ici', 'il', 'ils',
    'je', 'juste', 'la', 'le', 'les', 'leur', 'là', 'ma', 'maintenant', 'mais',
    'mes', 'mien', 'moins', 'mon', 'mot', 'même', 'ni', 'nommés', 'notre',
    'nous', 'ou', 'où', 'par', 'parce', 'pas', 'peut', 'peu', 'plupart',
    'pour', 'pourquoi', 'quand', 'que', 'quel', 'quelle', 'quelles', 'quels',
    'qui', 'sa', 'sans', 'ses', 'seulement', 'si', 'sien', 'son', 'sont',
    'sous', 'soyez', 'sur', 'ta', 'tandis', 'tellement', 'tels', 'tes', 'ton',
    'tous', 'tout', 'trop', 'très', 'tu', 'voient', 'vont', 'votre', 'vous',
    'vu', 'ça', 'étaient', 'état', 'étions', 'été', 'être', 'meteo', 'météo'
    'à', '?', '!', '.', '', 'à'
]

HEADERS = {
    'Accept':
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'Accept-Encoding': "gzip, deflate, br",
    'Connection': "keep-alive",
    'TE': "Trailers",
    'Upgrade-Insecure-Requests': "1",
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0",
    'Referer': "www.google.com"
}


# fonction qui va réaliser nos requetes (urllib/gsearch)
def bot_request(query):
    fail = 'Désolé je n\'ai pas de réponses à votre question .'
    resultat = ''
    try:
        """ cas ou l'utilisateur veut connaitre la météo,
         on va filtrer sa question pour extraire le nom de la ville
         pour l'utiliser dans une requete avec l'api openweathermap"""
        if 'meteo' in query or 'temp' in query or 'météo' in query:
            req = list(
                filter(
                    lambda x: x not in stop_wrods and bool(
                        re.search(r'[A-Z]', x)), query.split(' ')))

            if not req:
                ville = 'Lille'
            else:
                ville = req[0]
            api_meteo = url_weather = "http://api.openweathermap.org/data/2.5/weather?q=" + ville + "&APPID=beb97c1ce62559bba4e81e28de8be095&lang=fr&units=metric"
            r_weather = requests.get(url_weather)
            data = r_weather.json()
            try:
                temp = data.get('weather', None)[0].get('description', None)
                temperature = data.get('main', None).get('temp', None)
                ressenti = data.get('main', None).get('feels_like', None)
            except:
                print('probleme lors de la récupération des donénes méteo')

            resultat = f'Actuellement sur la ville de {ville}, l\'état du ciel: {temp} et la temperature est de: {temperature}°, ressenti: {ressenti}°'

        elif "heure" in query or 'date' in query:
            """ cas heure est demandé dans la requete"""
            resultat = f'{str(datetime.now())}'
        else:
            """ toute autre question posé par l'utilisateur,
             on va faire une requete avec google search pour avoir une liste d'urls et on va les requeter ensuite
             puis extraire des paragraphes et en afficher le résultat"""
            search_result_list = list(
                search(query, tld="co.in", num=10, stop=3, pause=1))
            i = 0
            for i in range(3):
                page = requests.get(search_result_list[i], headers=HEADERS)
                if page.status_code == 200:
                    tree = html.fromstring(page.content)
                    soup = BeautifulSoup(page.content, features="lxml")
                    paragraphe = ''
                    all_infos = soup.findAll('p')
                    for element in all_infos[:2]:
                        paragraphe += '\n' + ''.join(
                            element.findAll(text=True))
                    paragraphe = paragraphe.replace('\n', '')
                    if paragraphe:
                        paragraphe = paragraphe[:round((
                            len(paragraphe) * 90 / 100))] if len(
                                paragraphe
                            ) > 1000 else paragraphe[:round(len(paragraphe))]
                        break
            resultat = paragraphe if len(paragraphe) > 3 else fail

        return resultat
    except Exception as e:
        logging.warning(e)
        if len(resultat) == 0: resultat = fail
        return resultat
