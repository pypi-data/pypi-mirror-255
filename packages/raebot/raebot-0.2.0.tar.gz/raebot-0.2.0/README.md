# raebot

Search for definitions from the DLE.

This package is inspired by [pyrae](https://github.com/nachocho/pyrae), but is implemented in a way I find more
intuitive. Also, most importantly for me, synonym and antonym support.

## Installation

```bash
pip install raebot
```

## Develop

- Install poetry.
- Create a virtual environment
- run `poetry install` to install the dependencies.

TDD recommended. Add a case, then update the script to make the test pass.

PRs welcome.

## Testing

Run `poetry run pytest` to run the tests.

## Publish

If you are Weiwei or one of his robots, run `poetry publish --build` to publish a new version.

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
