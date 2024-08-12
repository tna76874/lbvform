#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 14:02:47 2024

@author: lukas
"""

from module import *
import argparse


class ReisekostenFrame:
    def __init__(self, **kwargs):
        self.data = kwargs.get('data')
        if not isinstance(self.data,DatenParser):
            raise ValueError("Wring data class")
        
        self.fillable = kwargs.get('fillable', True)
        
        self.antraege = [Reisekostenantrag(data=self.data, key=k, fillable = self.fillable) for k in self.data.get_all_lehrer().keys()]
        
        self.genemigung = Reisekostengenemigung(data=self.data, fillable = self.fillable)
        
    def render(self):
        for a in self.antraege:
            a.render()
        
        self.genemigung.render()
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reisekosten Management CLI")
    parser.add_argument('--config', default='config.yml', type=str, help='Path to the configuration file (YAML format)')
    parser.add_argument('-r', '--render', action='store_true', help='Render the ReisekostenFrame')
    parser.add_argument('-f', '--fillable', action='store_false', help='PDF are not fillable')

    args = parser.parse_args()

    
    data_parser = DatenParser(args.config)
    reisekosten_frame = ReisekostenFrame(data=data_parser, fillable=args.fillable)
    
    if args.render==True:
        reisekosten_frame.render()

