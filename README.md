# LBV Formular ausfüllen

Lehrkräfte sind gesegnet mit den wunderbaren Formularen 1211 und 1212a um alle denkbaren Auswüchse von Reisekostenkonstellationen einzureichen. Es ist nahezu keine Konstellation erdenklich, die nicht beantragt werden kann. Es wird jedoch hinter vorgehaltener Hand gemunkelt, dass für den Fall "Klassenlehrerteam geht mit Klasse auf Klassenfahrt" die Beantragung unnötig kompliziert und die Formulare mit einer nervigen Redundanz ausgefüllt werden müssen. Jeder gute Verwaltungsbeamte distanziert sich jedoch von solchen infamen Aussagen. 

Dieses Stück Software ist dazu da, um den gemeinen Verwaltungsbeamten "Lehrer" um die Freude zu bringen die gleichen Informationen in x-verschiedene Formulare einzutragen. Es wird deutlich angeraten diese Software nur zu benutzen, wenn vorangehend ausreichend stupide, redundante und obsolete Verwaltungsaufgaben ausgeführt wurden um die natürliche Beamtenstaubschicht nicht zu verdünnhäuten (Empfehlung: Dienst-Emails ausdrucken, händisch datieren und zum Schreddern zum Ende der gesetzlichen Löschfrist anmelden).

### Installieren

```bash
pip install git+https://github.com/tna76874/lbvform.git
```

### Kofigurieren

Eine Textdatei (z.B. `config.yml`) erstellen mit den Infos zu der Klassenfahrt. Dabei ist auf die Einrückungen zu achten.

```
event:
  name: Schullandheim 
  land: Deutschland
  ort: Entenhausen
  art: Schullandheim
  hin_start: 04.03.2024 08:00
  hin_ende: 04.03.2024 10:00
  rueck_start: 07.03.2024 10:00
  rueck_ende: 07.03.2024 12:00

klasse:
  anz: 25
  name: 08e

schule:
  name: Dagobert Gymnasium Entenhausen
  tel: 0123456789

lehrer:
  a:
    name: Düsentrieb
    vorname: Daniel
    pn: 12345678
    unterkunft: 100
    fahrt: 20

  b:
    name: Duck
    vorname: Daisy
    pn: 87654321
    unterkunft: 100
    fahrt: 20

verantwortlicher: a
```

### PDF-Formulare generieren

```
lbvform --config config.yml --render
```

In dem Verzeichnis liegen (mit der vorangehenden Beispiel Konfiguration):

```bash
├── 1211_genehmigung.pdf
├── 1212a_Duck_Daisy.pdf
├── 1212a_Düsentrieb_Daniel.pdf
└── config.yml
```

1. Zuerst muss **vor** der Klassenfahrt `1211_genehmigung.pdf` unterschrieben bei der Schulleitung eingereicht werden.
2. **Nach** der Klassenfahrt gegebenenfalls die Konfiguration nochmals anpassen und danach die 1212a Formulare unterschreiben und bei der Schulleitung einreichen. Individuelle Kosten können in dem Formular dann noch nachgetragen werden.

Es sollte darauf geachtet werden, dass bei keinem 1212a die Personalnummer fehlt.

Hier sind die Beispieldateien abgelegt: [Beispiele](example/)

