#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Handles command line interface
"""
import argparse
from .gendoc import _make_standard_package, _write_doc
from .validate import paralex_validation

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands',
                                        description = 'valid subcommands')
    make_std = subparsers.add_parser("make_standard")
    make_std.set_defaults(func=_make_standard_package)
    make_doc = subparsers.add_parser("make_doc")
    make_doc.set_defaults(func=_write_doc)
    validate = subparsers.add_parser("validate")
    validate.add_argument("package")
    validate.set_defaults(func=paralex_validation)
    return parser.parse_args()

def main():
    args = parse_args()
    args.func(args)
