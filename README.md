# Sevilla
Program na monitorování inzerátu podle klíčových slov z SBazaru.

## Prerekvizity
Python 3

## Konfigurace
Klicová slova pro vyhledávání lze upravit v souboru `klicovaslova.txt`.
Klíčová slova je lepší zadávat bez přípon (např. místo 'rozbitý' jenom 'rozbit').

V souboru 'config.json' lze nastavit příjemce, odesílatele a heslo k emailu odesílatele.

## Spuštění
```
python run.py
```
## Proces Diagram
![SevillaProcesDiagram](pictures/SevillaProcesDiagram.png "Sevilla Proces Diagram")

## Class Diagram
![SevillaClassDiagram](pictures/SevillaClassDiagram.png "Sevilla Class Diagram")
