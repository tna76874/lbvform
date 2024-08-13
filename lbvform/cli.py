#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import argparse

from lbvform.module import *

def main():
    parser = argparse.ArgumentParser(description="Reisekosten Management CLI")
    parser.add_argument('--config', default='config.yml', type=str, help='Path to the configuration file (YAML format)')
    parser.add_argument('-r', '--render', action='store_true', help='Render the ReisekostenFrame')
    parser.add_argument('-f', '--fillable', action='store_false', help='PDF are not fillable')

    args = parser.parse_args()

    
    data_parser = DatenParser(args.config)
    reisekosten_frame = ReisekostenFrame(data=data_parser, fillable=args.fillable)
    
    if args.render==True:
        reisekosten_frame.render()

if __name__ == "__main__":
    main()