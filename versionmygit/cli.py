#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import argparse

from versionmygit.version import *

def main():
    parser = argparse.ArgumentParser(description='Get Git version information for a given path')
    parser.add_argument('path', help='Path to the directory to get Git version information for')
    
    # Adding optional arguments
    parser.add_argument('--minor', type=int, help='Set the minor version')
    parser.add_argument('--major', type=int, help='Set the major version')
    parser.add_argument('--commit', help='Set the last minor commit hash', default=None)

    args = parser.parse_args()
    
    try:
        # Create GitVersion instance with optional parameters
        version_info = GitVersion(args.path, 
                                   minor=args.minor, 
                                   major=args.major, 
                                   minor_commit=args.commit)
        
        # Check if any of the versioning options are set
        if args.minor is not None or args.major is not None or args.commit is not None:
            # Print semantic versioning information
            print(version_info._get_semantic_version())
        else:
            # Print the simple version information
            print(version_info.version())

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()