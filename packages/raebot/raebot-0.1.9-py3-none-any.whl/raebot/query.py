import requests
from bs4 import BeautifulSoup
from .model import Definition, Phrase, Word

BASE_URL = "https://dle.rae.es"
session = requests.session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})


def search_words(word: str):
    resp = session.get(f"{BASE_URL}/{word}?m=form")
    soup = BeautifulSoup(resp.text, 'html.parser')
    entries = soup.select('#resultados > article')
    if entries:
        words = []
        for entry in entries:
            try:
                wd = Word(entry)
                words.append(wd)
            except:
                header = entry.find('header')
                linked_entries = header.find_next_siblings('p', {'class': ['l', 'l3', 'b']})
                if linked_entries:
                    # Search for Allen, found "llave Allen"
                    for linked in linked_entries:
                        path = linked.find('a').attrs['href']
                        id = path.split('#')[1]
                        url = f"{BASE_URL}{path}"
                        resp = session.get(url)
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        entries = soup.find_all('p', {'id': id})
                        if entries:
                            if entries[0].attrs['class'] == ['k5'] or entries[0].attrs['class'] == ['k6']:
                                # Entry is a phrase
                                ph = entries[0].text
                                defi = Definition(entries[0].find_next_sibling('p', {'class': 'm'}))
                                # TODO: support multiple defs
                                wd = Phrase(ph, [defi])
                            else:
                                wd = Word(entry[0])
                            words.append(wd)

        return words
    else:
        others = soup.select('#resultados > .otras > .n1 > a')
        if others:
            words = []
            for o in others:
                path = o.attrs['href']
                id = path.split('#')[1]
                url = f"{BASE_URL}{path}"
                resp = session.get(url)
                soup = BeautifulSoup(resp.text, 'html.parser')
                entry = soup.find_all("article", {"id": id})
                wd = Word(entry[0])
                words.append(wd)
        else:
            # Search for fallecio, found fallecer and fallecido
            words = []
            links = soup.select('#resultados > .item-list > .n1 > a')
            for link in links:
                path = link.attrs['href']
                url = f"{BASE_URL}{path}"
                resp = session.get(url)
                soup = BeautifulSoup(resp.text, 'html.parser')
                entry = soup.select(f'article')
                wd = Word(entry[0])
                words.append(wd)
        return words


def search_expressions(expr: str):
    resp = session.get(f"{BASE_URL}/{word}?m=form2")
    soup = BeautifulSoup(resp.text, 'html.parser')
    entries = soup.select('#resultados > article')
    words = []
    for entry in entries:
        wd = Word(entry)
        words.append(wd)
    return words

def exact_match():
    pass

def start_with():
    pass

def end_with():
    pass

def contains():
    pass

def anagrams():
    pass

def random():
    pass



