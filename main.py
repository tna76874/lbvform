#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 14:02:47 2024

@author: lukas
"""

from module import *

class ReisekostenFrame:
    def __init__(self, **kwargs):
        self.data = kwargs.get('data')
        if not isinstance(self.data,DatenParser):
            raise ValueError("Wring data class")
        
        self.antraege = [Reisekostenantrag(data=self.data, key=k) for k in self.data.get_all_lehrer().keys()]
        
        self.genemigung = Reisekostengenemigung(data=self.data)
        
    def render(self):
        for a in self.antraege:
            a.render()
        
        self.genemigung.render()
        
        
if __name__ == "__main__":
    self = ReisekostenFrame(data=DatenParser('config.yml'))
    self.render()
