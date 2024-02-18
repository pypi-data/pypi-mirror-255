#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module generates standard files & documentation.
"""
import frictionless as fl
import json
from .paths import docs_path, standard_path
from .markdown import to_markdown
from .meta import package_from_kwargs

def _make_standard_package(*args, **kwargs):
    with (standard_path / "package_spec.json").open('r', encoding="utf-8") as flow:
        package_infos = json.load(flow)

    with (standard_path / "columns_spec.json").open('r', encoding="utf-8") as flow:
        columns = json.load(flow)

    with (standard_path / "tables_spec.json").open('r', encoding="utf-8") as flow:
        tables = json.load(flow)["tables"]

    resources = []
    for table in tables:
        # replace column names by their full definition
        table["schema"]["fields"] = [columns[f] for f in table["schema"]["fields"]]
        resources.append(fl.Resource(table))

    package = package_from_kwargs(resources=resources, **package_infos)

    package.to_json(str(standard_path / "paralex.package.json"))



def _write_doc(*args, **kwargs):
    to_markdown(fl.Package(standard_path / "paralex.package.json"),
                docs_path / "specs.md")


