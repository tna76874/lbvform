#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 11:16:32 2024

@author: lukas
"""
import PyPDF2
from PyPDF2.generic import NameObject, TextStringObject
import datetime
import numpy as np
import yaml
import subprocess
import os
import tempfile
import shutil
import sys
from slugify import slugify
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import lbvform

class DatenParser:
    def __init__(self, data):
        if isinstance(data, dict):
            self.data = data
        else:
            self.data = self.load_yaml(data)

    def load_yaml(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def get_all_lehrer(self):
        return self.data.get('lehrer', {})

    def get_schule(self):
        return self.data.get('schule', {})

    def get_klasse(self):
        return self.data.get('klasse', {})

    def get_event(self):
        event = self.parse_event_dates()
        event['days'] = int(np.ceil((event.get('rueck_ende')-event.get('hin_start')).total_seconds()/ (24 * 3600)))
        event['1211'] = ", ".join([k for k in [event.get('name'), event.get('ort'), event.get('land', 'Deutschland')] if k !=None])
        event['1212a'] = ", ".join([k for k in [event.get('name'), event.get('ort'), event.get('land', 'Deutschland')] if k !=None])
        return event

    def get_verantwortlicher(self):
        verantwortlicher_key = self.data.get('verantwortlicher')
        lehrer = self.get_all_lehrer()
        return lehrer.get(verantwortlicher_key, None) if verantwortlicher_key else None

    def parse_datetime(self, date_str):
        """Parses a date string into a datetime object."""
        date_format = "%d.%m.%Y %H:%M"  # Beispiel: 25.12.2023 14:30
        return datetime.datetime.strptime(date_str, date_format)

    def parse_event_dates(self):
        """Parses event date strings into datetime objects."""
        event = self.data.get('event', {})
        for key in ['hin_start', 'hin_ende', 'rueck_start', 'rueck_ende']:
            if key in event:
                if not isinstance(event[key],datetime.datetime):
                    event[key] = self.parse_datetime(event[key])
        return event

    def get_gesamt_kosten(self):
        """Berechnet die Gesamtkosten für Unterkunft und Fahrt aller Lehrer."""
        lehrer = self.get_all_lehrer()
        gesamt_kosten = 0

        for details in lehrer.values():
            unterkunft = details.get('unterkunft', 0)
            fahrt = details.get('fahrt', 0)
            gesamt_kosten += unterkunft + fahrt

        return gesamt_kosten

    def get_begleitlehrer(self):
        """Gibt alle Lehrer zurück, die nicht verantwortlich sind."""
        verantwortlicher_key = self.data.get('verantwortlicher')
        lehrer = self.get_all_lehrer()
        begleitlehrer = {key: details for key, details in lehrer.items() if key != verantwortlicher_key}
        return begleitlehrer

    def get_begleitlehrer_dict(self):
        """Gibt ein Dictionary mit Nachnamen und Vornamen aller Begleitlehrer zurück."""
        verantwortlicher_key = self.data.get('verantwortlicher')
        lehrer = self.get_all_lehrer()
        begleitlehrer_dict = {}

        for key, details in lehrer.items():
            if key != verantwortlicher_key:
                name = details.get('name')
                vorname = details.get('vorname')
                if name and vorname:
                    begleitlehrer_dict[name] = vorname

        return begleitlehrer_dict

    def get_description(self):
        """Generiert eine eindeutige Beschreibung basierend auf dem Start- und Enddatum, dem Ort und dem Klassennamen."""
        event = self.get_event()
        klasse = self.get_klasse()

        description = "_".join([k for k in [
                                            event.get('hin_start').strftime("%Y%m%d") if event.get('hin_start') else None,
                                            event.get('rueck_ende').strftime("%Y%m%d") if event.get('rueck_ende') else None,
                                            event.get('name'),
                                            event.get('ort'),
                                            klasse.get('name', None),
                                            ]
                                if k !=None])


        return slugify(description, separator="_")

def parse_datetime(date_str):
    """Parses a date string into a datetime object."""
    date_format = "%d.%m.%Y %H:%M"  # Beispiel: 25.12.2023 14:30
    return datetime.datetime.strptime(date_str, date_format)

def fill_pdf(input_pdf_path, output_pdf_path, field_values, debug = False, fillable = True, **kwargs):
    # Read the existing PDF
    input_pdf = PyPDF2.PdfReader(open(input_pdf_path, "rb"))
    output_pdf = PyPDF2.PdfWriter()

    # Get the form fields
    fields = input_pdf.get_fields()
    field_values_mapping = {k: f'field{index + 1:03}' for index, k in enumerate(fields.keys())}
    field_inv_values = {v:k for k,v in field_values_mapping.items()}
    

    # Write the filled-in form to a new PDF
    for page_num in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_num]
        if debug==False:
            output_pdf.update_page_form_field_values(page, {field_inv_values.get(key, key): value for key, value in field_values.items()})
        else:
            output_pdf.update_page_form_field_values(page, field_values_mapping)
            print(field_inv_values)
        output_pdf.add_page(page)

    if output_pdf_path!=True:
        with open(output_pdf_path, "wb") as output_stream:
            output_pdf.write(output_stream)
    
    return output_pdf

class Reisekostenantrag:
    def __init__(self, **kwargs):
        self.data = kwargs.get('data')
        if not isinstance(self.data,DatenParser):
            raise ValueError("Wring data class")
            
        self.fillable = kwargs.get('fillable', True)
            
        self.type='1212a'
            
        self.key = kwargs.get('key')
        
        self.rendered = None
        
        if self.key not in self.data.get_all_lehrer().keys():
            raise ValueError("Key not found")
        
        self.is_verantwortlich = self.key == self.data.data.get('verantwortlicher')
            

        self.values = {
            #PERSONALNUMMER
            "field086" : self.data.get_all_lehrer().get(self.key, {}).get('pn',''),
            #Name
            "field001" : self.data.get_all_lehrer().get(self.key, {}).get('name',''),
            #vorname
            "field002" : self.data.get_all_lehrer().get(self.key, {}).get('vorname',''),
        
        
            # Schullandheimaufenthalt
            'field013' : '/On' if self.data.get_event().get('art')=='Schullandheim' else '/Off',
            #JahresausflugWandertag
            'field014' : '/Off' if self.data.get_event().get('art')=='Schullandheim' else '/On',
        
            #Veranstaltungsort (Stadt, Land)
            'field101' : self.data.get_event().get('1212a'),
        
        
            #Zahl der teilnehmenden Schüler/innen
            'field100' : self.data.get_klasse().get('anz'),
            #Zahl der Begleitpersonen (einschl. verantwortliche Lehrkräfte)
            'field033' : self.data.get_klasse().get('anz')+len(self.data.get_all_lehrer()),
            #Unterkunft und Verpflegung: Kosten antragstellende Person
            'field035' : '/On', #CHECKBOX
            'field102' : self.data.get_all_lehrer().get(self.key, {}).get('unterkunft',''),
            # Fahrkosten - einschließlich Ausflugsfahrten -
            'field046' : '/On', #CHECKBOX
            'field126' : self.data.get_all_lehrer().get(self.key, {}).get('fahrt',''),    
        
        
            ### DO NOT EDIT
            #telefon dienstlich
            "field005" : self.data.get_schule().get('tel'),
        
            ## Beginn Hinfahrt
            # Datum
            'field025' : self.data.get_event().get('hin_start').strftime('%d.%m.%Y'),
            # Uhrzeit
            'field028' : self.data.get_event().get('hin_start').strftime('%H:%M'),
            ## Ende Hinfahrt
            # Datum
            'field029' : self.data.get_event().get('hin_ende').strftime('%d.%m.%Y'),
            # Uhrzeit
            'field026' : self.data.get_event().get('hin_ende').strftime('%H:%M'),
            
            ## Beginn Rückfahrt
            # Datum
            'field027' : self.data.get_event().get('rueck_start').strftime('%d.%m.%Y'),
            # Uhrzeit
            'field031' : self.data.get_event().get('rueck_start').strftime('%H:%M'),
            ## Ende Rückfahrt
            # Datum
            'field032' : self.data.get_event().get('rueck_ende').strftime('%d.%m.%Y'),
            # Uhrzeit
            'field030' : self.data.get_event().get('rueck_ende').strftime('%H:%M'),
            #Datum,
            'field082' : datetime.datetime.now().strftime('%d.%m.%Y'),
            #VERANTWORTLICHE LEHRKRAFT
            'field010' : self.data.get_verantwortlicher().get('name',''),
            'field011' : self.data.get_verantwortlicher().get('vorname',''),
            "field012" : self.data.get_schule().get('name',''),
        }
        
        # if self.is_verantwortlich==False:
        #     self.values.update({
        #     # Dienstreisegenehmigung ist dem Antrag von xxx beigefügt
        #     'field089' : '/On',    #checkbox
        #     'field090' : self.data.get_verantwortlicher().get('name',''),    # Name
        #     'field091' : self.data.get_verantwortlicher().get('vorname',''),    # Vorname
        #     'field092' : self.data.get_schule().get('name',''),    # Schule
        #                             })
        # else:
        self.values.update({
        # Dienstreisegenehmigung ist beigefügt.
        'field081' : '/On',    #checkbox
                                })
        
        nebenkosten = {
                        # 'Kaffee' :'2',
                        }
        nebenkosten_fields  = {'field073':'field074',
                               'field075':'field076',
                               'field077':'field078',
                               'field079':'field080',
                               'field081':'field082'}
        
        if len(nebenkosten) < len(nebenkosten_fields):
            self.values.update({
                list(nebenkosten_fields.keys())[i]: key for i, (key, value) in enumerate(nebenkosten.items())
            })
            self.values.update({
                list(nebenkosten_fields.values())[i]: value for i, (key, value) in enumerate(nebenkosten.items())
            })
            
        
        self.input = os.path.join(os.path.dirname(lbvform.__file__), 'forms', "1212a.pdf")
        
        self._lehrer_vorname = self.data.get_all_lehrer().get(self.key, {}).get('vorname','')
        self._lehrer_nachname = self.data.get_all_lehrer().get(self.key, {}).get('name','')
        
        self._filename = slugify( f"{self.data.get_description()}_{self.type}_{self._lehrer_vorname}_{self._lehrer_nachname}", separator="_")+'.pdf'
        
        self.output = kwargs.get('output', False) or self._filename
        self.debug = kwargs.get('debug', False)
    
    def render(self):
        self.rendered = fill_pdf(self.input, self.output, self.values, debug = self.debug, fillable = self.fillable)
        
class Reisekostengenemigung:
    def __init__(self, **kwargs):
        self.data = kwargs.get('data')
        if not isinstance(self.data,DatenParser):
            raise ValueError("Wring data class")

        self.fillable = kwargs.get('fillable', True)

        self.rendered = None

        
        self.type='1211'


        self.values = {
            #PERSONALNUMMER
            "field017" : self.data.get_verantwortlicher().get('pn'),
            #Name
            "field018" : self.data.get_verantwortlicher().get('name'),
            #vorname
            "field034" : self.data.get_verantwortlicher().get('vorname'),
        
            # Art der außerunterrichtlichen Veranstaltung
            'field006' : self.data.get_event().get('art'),
            # Veranstaltungsziel (Ort, Stadt, Land)
            'field022' : self.data.get_event().get('1211'),
        
        
            #Zahl der teilnehmenden Schüler/innen
            'field010' : self.data.get_klasse().get('anz'),
            #Zahl der Aufenthaltstage
            'field046' : self.data.get_event().get('days'),
            # Klasse/Klassenstufe/Kurs
            'field026' : self.data.get_klasse().get('name'),
        
            # Voraussichtliche Kosten
            'field011' : self.data.get_gesamt_kosten(),    
        
        
            ### DO NOT EDIT
        
            ## Beginn Hinfahrt
            # Datum
            'field008' : self.data.get_event().get('hin_start').strftime('%d.%m.%Y'),
            # Uhrzeit
            'field009' : self.data.get_event().get('hin_start').strftime('%H:%M'),
            ## Ende Hinfahrt
            # Datum
            'field032' : self.data.get_event().get('hin_ende').strftime('%d.%m.%Y'),
            # Uhrzeit
            'field007' : self.data.get_event().get('hin_ende').strftime('%H:%M'),
            
            ## Beginn Rückfahrt
            # Datum
            'field029' : self.data.get_event().get('rueck_start').strftime('%d.%m.%Y'),
            # Uhrzeit
            'field030' : self.data.get_event().get('rueck_start').strftime('%H:%M'),
            ## Ende Rückfahrt
            # Datum
            'field031' : self.data.get_event().get('rueck_ende').strftime('%d.%m.%Y'),
            # Uhrzeit
            'field033' : self.data.get_event().get('rueck_ende').strftime('%H:%M'),
            #Datum,
            'field012' : datetime.datetime.now().strftime('%d.%m.%Y'),
        }


        lehrer = self.data.get_begleitlehrer_dict()
        lehrer_fields  = {  'field019':'field002',
                            'field020':'field004',
                            'field035':'field036',
                            'field037':'field038',
                            }


        self.values.update({
            list(lehrer_fields.keys())[i]: key for i, (key, value) in enumerate(lehrer.items())
        })
        self.values.update({
            list(lehrer_fields.values())[i]: value for i, (key, value) in enumerate(lehrer.items())
        })
    
        self.input = os.path.join(os.path.dirname(lbvform.__file__), 'forms', "1211.pdf")       
        self._filename = slugify(f'{self.data.get_description()}_{self.type}_genehmigung', separator="_")+'.pdf'
        self.output = kwargs.get('output', False) or self._filename
        self.debug = kwargs.get('debug', False)
    
    def render(self):
        self.rendered = fill_pdf(self.input, self.output, self.values, debug = self.debug, fillable = self.fillable)

class ReisekostenFrame:
    def __init__(self, **kwargs):
        self.data = kwargs.get('data')
        if not isinstance(self.data,DatenParser):
            raise ValueError("Wrong data class")
        
        self.fillable = kwargs.get('fillable', True)
        
        self.debug = kwargs.get('debug', False)
        
        self.output = kwargs.get('output', False)
        
        self.antraege = [Reisekostenantrag(data=self.data, key=k, output = self.output, debug = self.debug) for k in self.data.get_all_lehrer().keys()]
        
        self.genemigung = Reisekostengenemigung(data=self.data, output = self.output)
        
    def render(self):
        for a in self.antraege:
            a.render()
        
        self.genemigung.render()
        
if __name__ == "__main__":
    yaml_file = '../example/config.yml'
    self = ReisekostenFrame(data=DatenParser(yaml_file), debug=False)
    self.render()



