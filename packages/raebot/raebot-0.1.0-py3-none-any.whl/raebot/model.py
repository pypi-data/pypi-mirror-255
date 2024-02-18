

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional

from bs4 import ResultSet, SoupStrainer, Tag


def is_abbr(tag):
    return tag.name == 'abbr'


@dataclass()
class Definition:
    types: [str]
    definition: str
    examples: Optional[List[str]]
    def __init__(self, soup: Tag):
        self.synonyms = []
        self.antonyms = []
        ordinal = soup.find('span', {'class': 'n_acep'})
        types = ordinal.find_next_siblings('abbr', {'class': ['d', 'g']})
        ordinal.decompose()
        self.types = [t.text for t in types]
        for t in types:
            t.decompose()
        examples = soup.find_all('span', {'class': 'h'})
        self.examples = [sp.text for sp in examples]
        for ex in examples:
            ex.decompose()
        self.definition = soup.text.strip()

@dataclass()
class DefinitionX:
    types: [str]
    definition: str
    examples: Optional[List[str]]
    synonyms: Optional[List[str]]
    antonyms: Optional[List[str]]
    def __init__(self, soup: Tag):
        self.synonyms = []
        self.antonyms = []
        ordinal = soup.find('span', {'class': 'n_acep'})
        types = ordinal.find_next_siblings('abbr', {'class': ['d', 'g']})
        ordinal.decompose()
        self.types = [t.text for t in types]
        for t in types:
            t.decompose()
        examples = soup.find_all('span', {'class': 'h'})
        self.examples = [sp.text for sp in examples]
        for ex in examples:
            ex.decompose()
        table = soup.find('table', {'class': 'sinonimos'})
        if table is not None:
            rows = table.find_all("tr")
            self.synonyms = [s.text for s in rows[0].find_all("td")[1].find_all("span", {"class": 'sin'})]
            if (len(rows)) == 2:
                self.antonyms = [s.text for s in rows[1].find_all("td")[1].find_all("span", {"class": 'sin'})]
            if table:
                table.decompose()
        self.definition = soup.text.strip()


@dataclass()
class Phrase:
    phrase: str
    definition: [Definition]


@dataclass()
class Word:
    word: str
    etymology: str
    definitions: [DefinitionX]
    phrases: Optional[List[Phrase]]

    def __init__(self, soup: Tag):
        header = soup.find('header')
        sub = header.find("sup")
        if sub:
            sub.decompose()
        self.word = header.text
        self.etymology = soup.find('p', {'class': 'n2'}).text
        self.definitions = [DefinitionX(sp) for sp in soup.find_all('p', {'class': 'j'})]
        phrases: List[Tag] = [ph for ph in soup.find_all('p', {'class': ['k5', 'k6', 'm']})]
        defs = []
        phr = None
        self.phrases = []
        for ph in phrases:
            if ph.attrs['class'] == ['k5'] or ph.attrs['class'] == ['k6']:
                if phr and defs:
                    self.phrases.append(Phrase(phr, defs))
                phr = ph.text.strip()
                defs = []
                continue
            if ph.attrs['class'] == ['m']:
                defs.append(Definition(ph))
                continue
