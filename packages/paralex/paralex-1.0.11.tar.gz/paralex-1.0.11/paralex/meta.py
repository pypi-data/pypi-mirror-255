#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module manipulates frictionless metadata.
"""
import frictionless as fl
from pathlib import Path
import json
from . import standard_path
import inspect
import logging
import collections.abc
from collections import defaultdict
import re

relations = ["isCitedBy", "cites", "isSupplementTo", "isSupplementedBy", "isContinuedBy", "continues", "isDescribedBy",
             "describes", "hasMetadata", "isMetadataFor", "isNewVersionOf", "isPreviousVersionOf", "isPartOf",
             "hasPart", "isReferencedBy", "references", "isDocumentedBy", "documents", "isCompiledBy", "compiles",
             "isVariantFormOf", "isOriginalFormof", "isIdenticalTo", "isAlternateIdentifier", "isReviewedBy", "reviews",
             "isDerivedFrom", "isSourceOf", "requires", "isRequiredBy", "isObsoletedBy", "obsoletes"]
resource_name_pattern = re.compile(r'^([-a-z0-9._/])+$')




def _to_pattern(iterable, sep="", diacritics=None):
    iterable = sorted(iterable, key=len, reverse=True)
    items = "|".join(iterable)
    if diacritics is None or not diacritics:
        char = f"({items})"
    else:
        diacs = "|".join(diacritics)
        char = f"(({diacs})*({items})({diacs})*)"

    if sep == "":
        return f"{char}+"
    else:
        return f"{char}({sep}{char})*"

def _get_default_package():
    """ Instantiate a default paralex frictionless package

    This uses the paralex json file, removing specific instance information
    (version, name, contributors, related_identifiers).

    Returns (fl.Package): a default package for paralex lexicons

    """
    default_to_remove = ["version", "name", "contributors", "related_identifiers"]
    default = json.load((standard_path / "paralex.package.json").open("r", encoding="utf-8"))

    # Remove default dummy values in package
    for key in default_to_remove:
        del default[key]
    return fl.Package(default)


def default_update(specific, default):
    """ Update a default package with specific information.

    The behaviour is as follows:
        - For the "Fields" list, append any extra column from default
         which are not already specified in the specific information
        - Otherwise for all mappings: recursively update
        - Otherwise add information from default if it does not exist in specific.

    Args:
        specific (dict): specific information (user specified)
        default (dict): default information (from paralex standard)

    Returns:
        a dictionary of the default information, updated with the specific information.

    """
    for k, v in default.items():
        if isinstance(v, list) and k == "fields":
            cols = specific.get(k, [])
            specific[k] = cols + list(filter(lambda c: c not in cols, v))
        if isinstance(v, collections.abc.Mapping):
            specific[k] = default_update(specific.get(k, {}), v)
        elif specific.get(k, None) is None:
            specific[k] = v
    return specific


def package_from_kwargs(**kwargs):
    # Separate kwargs between pre-defined ones and custom ones
    defined = {x.name: kwargs[x.name] for x in fl.Package.__attrs_attrs__ if x.name in kwargs}
    custom = {k: kwargs[k] for k in kwargs if k not in defined}
    p = fl.Package(**defined)
    p.custom.update(custom)
    return p

def paralex_factory(title, resources_infos, **kwargs):
    """ Generate frictionless metadata for this paralex lexicon.

    Use the default package, fillin-in user specified information.
        Keeps only existing tables,
        updates foreign keys and table relations according to which tables are
        declared.

    Args:
        title (str): a title for the package
        resources_infos (dict): dictionary of table names to resource information
        **kwargs:

    Returns:

    """
    ## Update package infos
    kwargs["title"] = title
    if "basepath" not in kwargs:
        # Get the path of the calling file
        # -- assuming the data files reside at the same location
        kwargs["basepath"] = str(Path(inspect.stack()[1].filename).parent)

    # Get a frictionless package instantiated from the standard json
    default_package = _get_default_package()
    default_package_infos = default_package.to_dict()
    del default_package_infos["resources"]
    default_update(kwargs, default_package_infos)

    p = package_from_kwargs(**kwargs)

    ## Update resources infos
    default_resources = set(default_package.resource_names)
    resources = set(resources_infos)
    added_resources = resources - default_resources
    missing_resources = default_resources - resources

    for table in resources_infos:
        if resource_name_pattern.match(table) is None:
            suggested = re.sub("[^-a-z0-9._/]","", table.lower())
            raise ValueError(f"Table name {repr(table)} is invalid. "
                             "\nTable names can only contain '-', '_', '.', "
                             "numbers or lowercase latin letters. "
                             f"Try instead something like:\n\tparalex_factory({title}, "
                             "{"
                             f" ... '{suggested}': {resources_infos[table]} ... "
                             "} ... )")
        table_infos = resources_infos[table]
        table_infos["name"] = table

        if table in added_resources:
            logging.warning(f"Adding a table which is not "
                            f"specified in the standard: {repr(table)}.\n\t"
                            f"Did you mean one of: `{'`, `'.join(missing_resources)}`?")
        else:
            default_table = default_package.get_resource(table)
            default_update(table_infos, default_table.to_dict())

        ## Adjust foreign keys according to existing tables
        fkeys = list(filter(lambda k: k["reference"]["resource"] in resources,
                            table_infos.get("schema", {}).get("foreignKeys", [])))
        if fkeys:
            table_infos["schema"]["foreignKeys"] = fkeys
        elif "schema" in table_infos and "foreignKeys" in table_infos["schema"]:
            del table_infos["schema"]["foreignKeys"]

        r = fl.Resource(table_infos, detector=fl.Detector(schema_sync=True))
        r.infer()
        p.add_resource(r)

    ## Set Foreign keys for tags

    taggable_tables = {"forms", "lexeme", "frequency"} & resources

    for tab_name in taggable_tables:
        table = p.get_resource(tab_name)
        tag_cols = {col for col in table.schema.field_names
                    if col.endswith("_tag")}
        if tag_cols:
            if "tags" not in resources:
                logging.warning(f"You have tag columns ({', '.join(tag_cols)}) "
                                f"in table {tab_name},"
                                f"but no tags table.")
            else:
                by_tag = defaultdict(list)
                for r in p.get_resource("tags").read_rows():
                    by_tag[r["tag_column_name"]].append(r["tag_id"])
                for col in tag_cols:
                    if col not in by_tag:
                        logging.warning(f"No tags defined for column {col} in table {tab_name}. "
                                        f"Please edit the tags table.")
                    else:
                        col_def = table.schema.get_field(col)
                        constraints = col_def.constraints
                        constraints["pattern"] = _to_pattern(by_tag[col], sep="\|")
                        col_def.constraints = constraints

    forms_table = p.get_resource("forms")

    # Set pattern for orth_form
    if {"graphemes", "forms"} <= resources \
            and forms_table.schema.has_field("orth_form"):
        graphemes = [r["grapheme_id"] for r in p.get_resource("graphemes").read_rows()]
        form = forms_table.schema.get_field("orth_form")
        constraints = getattr(form,"constraints")
        constraints["pattern"] = _to_pattern(graphemes, sep="")
        form.constraints = constraints

    # Set pattern for phon_form
    if {"sounds", "forms"} <= resources \
            and forms_table.schema.has_field("phon_form"):
        seg = []
        supra_seg = []
        for row in p.get_resource("sounds").read_rows():
            s = row["sound_id"]
            if s.startswith("#") or s.endswith("#"):
                continue
            if row.get("tier", "segmental") == "segmental":
                seg.append(s)
            else:
                supra_seg.append(s)
        form = forms_table.schema.get_field("phon_form")
        constraints = form.constraints
        constraints["pattern"] = _to_pattern(seg, diacritics=supra_seg, sep=" ")

    # Set pattern for cells identifiers (combinations of features)
    if {"cells", "features-values"} <= resources:
        features = [r["value_id"] for r in p.get_resource("features-values").read_rows()]
        cell_id = p.get_resource("cells").schema.get_field("cell_id")
        constraints = cell_id.constraints
        constraints["pattern"] = _to_pattern(features, sep=r"\.")

    p.infer()
    return p
