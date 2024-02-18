# raebot

Search for definitions from the DLE.

This package is inspired by [pyrae](https://github.com/nachocho/pyrae), but is implemented in a way I find more
intuitive. Also, most importantly for me, synonym and antonym support.

## Installation

```bash
pip install raebot
```

## Usage

```python
>>> from raebot import search_words
>>> from pprint import pprint

>>> pprint(search_words('hola'))

[Word(word='lindo, da',
      etymology="Del lat. limpĭdus 'limpio', 'puro'.",
      definitions=[DefinitionX(types=['adj.'],
                               definition='Hermoso, bello, grato a la vista.',
                               examples=[],
                               synonyms=['bonito',
                                         'bello',
                                         'hermoso',
                                         'precioso',
                                         'exquisito',
                                         'agraciado',
                                         'guapo',
                                         'majo'],
                               antonyms=['feo']),
                   DefinitionX(types=['adj.'],
                               definition='Perfecto, primoroso y exquisito.',
                               examples=[],
                               synonyms=[],
                               antonyms=[])],
      phrases=[Phrase(phrase='lindo don Diego',
                      definition=[Definition(types=['m. coloq.', 'desus.'],
                                             definition='lindo (‖ hombre que '
                                                        'presume de guapo).',
                                             examples=[])])])]
```

## Warning

For now it is used by me myself and I for generating anki flashcards. It may never be on feature parity with pyrae. But we shall see.
