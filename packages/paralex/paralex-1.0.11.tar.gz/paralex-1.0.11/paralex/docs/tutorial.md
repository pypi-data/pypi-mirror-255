This workflow tutorial takes you through the steps in order to create a paralex lexicon.

## Creating

Creating the data is of course the hardest task. You have full freedom to do this in whatever way feels most practical or convenient for you and your team.
This might mean editing csv files directly in LibreOffice Calc or Microsoft Excel,
manipulating raw data using a programming language like R or Python, relying on some sort of database manager with a graphical interface, or anything else you can think of.
Before publication, you need to be able to export each table in `csv` format with a
utf-8 character encoding.

The python package `paralex` allows you to then generate
additional [metadata](metadata.md) in accordance with the standard automatically.

### Tables

The set of expected tables are described in the [description of the standard](standard.md).
Minimally, you should
have a forms table which documents forms, and has at least the three columns
`form_id`, `lexeme`, `cell` and `phon_form` (or `orth_form`). The standard also specified
the
following tables:

- a `lexemes` table to document lexeme-level information such as inflection class.
- a `cells` table to document the meaning of each cell identifier,
- a `features` table to document the meaning of each feature in the each cell,
- a `sounds` table to document the conventions used to write the `phon_form`,
- a `grapheme` table to document the conventions used to write the `orth_form`,
- a `tags` table to document the labels for sets of forms related by properties such
  as overabundant series, defectivity type, dialectal variants, or data quality.

See [specs](specs.md) for the detail of expected tables and columns. Any additional
ad-hoc tables and columns can be added as necessary.

## Documenting

## Adding Metadata

The python package `paralex` can generate metadata automatically, filling-in default
information whenever the standard conventions are used. Technically speaking, it will
create a single metadata file with a name ending in *.package.json*. You should then
see all of your dataset and associated metadata as a single "package" described by the
metadata file.

First, you need to install `paralex`. This can be done from the command line, for example as follows:

```bash title="Installing paralex"
pip3 install paralex
```

Let's assume you have a single table of data, documenting Vulcan verbal paradigms. You can generate the metadata, to be placed in a file `vulcan.package.json` automatically. To do so you will need to prepare a python script within a text document as follows:

```python title="gen-metadata.py"
from paralex import paralex_factory

package = paralex_factory("Vulcan Verbal Paradigms",
                          {
                              "forms": {"path": "vulcan_v_forms.csv"},
                          }
                          )
package.to_json("vulcan.package.json")
```

This script states the title of your package and that you will be using a single table
which documents forms, currently located in your file `vulcan_v_forms.csv`. Paralex
will create metadata for your package, using information from the standard whenever you used standard columns, and inferring it from the data elsewhere.

The example above is minimal: a title for the package and at least a paradigm table
with a specific path is necessary. However, we recommend you add more information in
your script. In particular, provide a full text citation specifying how you wish your
dataset to be cited, a list of collaborators following the [frictionless specification]
(https://specs.frictionlessdata.io/), a license, a DOI identifier:

```python title="gen-metadata.py"
from paralex import paralex_factory

package = paralex_factory("Vulcan Verbal Paradigms",
                          {
                              "forms": {"path": "vulcan_v_forms.csv"},
                          },
                          citation="Spock (2258). Vulcan Verbal Paradigms dataset. Online.",
                          version="1.0.2",
                          keywords=["vulcan", "paradigms"],
                          id="http://dx.doi.org/S.179-276.SP",
                          contributors=[{'title': 'Spock', 'role': 'author'},
                          licenses=[{'name': 'CC-BY-SA-4.0',
                                     'title': 'Creative Commons Attribution Share-Alike 4.0',
                                     'path': 'https://creativecommons.org/licenses/by-sa/4.0/'}])
package.to_json("vulcan.package.json")
```

If this script is saved under the name `gen-metadata.py` and is placed in the same folder as the csv table, you can run it by typing in the terminal:

```bash title="Generating metadata"
python3 gen-metadata.py
```

The same process applies if you have more tables. Here is an example with a full list of five tables, including `vulcan_v_cells.csv`, `vulcan_v_features.csv`, `vulcan_v_lexemes.csv`, `vulcan_v_sounds.csv`:

```python title="gen-metadata.py"
from paralex import paralex_factory

package = paralex_factory("Vulcan Verbal Paradigms", {
        "cells": {"path": "vulcan_v_cells.csv"},
        "forms": {"path": "vulcan_v_forms.csv"},
        "features-values": {"path": "vulcan_v_features.csv"},
        "lexemes": {"path": "vulcan_v_lexemes.csv"},
        "sounds": {"path": "vulcan_v_sounds.csv"}
    },
  citation = "Spock and al (2258). Vulcan Verbal Paradigms dataset. Online.",
  version = "1.0.2",
  keywords = ["vulcan", "paradigms", "paralex"],
  id = "http://dx.doi.org/S.179-276.SP",
  contributors = [{'title': 'Spock', 'role': 'author'},
  licenses=[{'name': 'CC-BY-SA-4.0',
             'title': 'Creative Commons Attribution Share-Alike 4.0',
             'path': 'https://creativecommons.org/licenses/by-sa/4.0/'}]
)
package.to_json("vulcan.package.json")
```

### Custom columns 

For any columns already defined in the [specification](specs.md), rich metadata is automatically generated, including a column name, title and description, its expected type, and potential constraints. This is nested in the `<dataset>.package.json` file. For example, the metadata for the lexeme column from the forms table looks as follows:

```json
{
  "name": "lexeme",
  "type": "string",
  "title": "Reference to a lexeme identifier",
  "description": "Lexeme identifiers must be unique to paradigms.",
  "constraints": {
    "required": true
  },
  "rdfProperty": "https://www.paralex-standard.org/paralex_ontology.xml#lexeme"
}
```

The Paralex standard accomodates user-defined columns on top of pre-defined ones. For these columns, very little metadata can be inferred automatically. For example, imagine we have a `consonantal` column in the `sounds` table, coding whether each sound is a consonant or not. Since it is not pre-defined in the standard, the only inferred metadata would be:

```json

{
  "name": "consonantal",
  "type": "any"
}
```

It is possible to inject more detailed metadata by modifying the `gen-metadata.py` script. Of course, this needs to be done for each custom column, in each relevant table: 

```python title="gen-metadata.py"
from paralex import paralex_factory

package = paralex_factory("Vulcan Verbal Paradigms", {
              "cells": {"path": "vulcan_v_cells.csv"},
              "forms": {"path": "vulcan_v_forms.csv"},
              "features-values": {"path": "vulcan_v_features.csv"},
              "lexemes": {"path": "vulcan_v_lexemes.csv"},
              "sounds": { "path": "vulcan_v_sounds.csv",
                          "schema": {
                             "fields": [{ "name": "consonantal",
                                          "type": "boolean",
                                          "title": "Whether the segment is a consonant",
                                          "description": "Binary feature (1/0) indicating whether the segment is a consonant",
                                          "type": "boolean",
                                          "trueValues": [ "1"  ],
                                          "falseValues": [ "0"],
                                          "constraints": { "required": true }
                                        },
                                        ]
                           }
                         }
},
citation = "Spock and al (2258). Vulcan Verbal Paradigms dataset. Online.",
version = "1.0.2",
keywords = ["vulcan", "paradigms", "paralex"],
id = "http://dx.doi.org/S.179-276.SP",
contributors = [{'title': 'Spock', 'role': 'author'},
  licenses=[{'name': 'CC-BY-SA-4.0',
             'title': 'Creative Commons Attribution Share-Alike 4.0',
             'path': 'https://creativecommons.org/licenses/by-sa/4.0/'}]
)
package.to_json("vulcan.package.json")
```

To find the definitions and format of the column metadata, see the [fields descriptors](https://specs.frictionlessdata.io/table-schema/#field-descriptors) in the Frictionless specifications.

### Custom tables

Similarly, some metadata will be missing if using custom tables. In particular, one often needs to specify which column is an **identifier** (or **primary key**), and which columns refer to other ones. This is also done by adding to the `gen-metadata.py` script. For example, imagine that in addition to lexemes, we have added a flexeme table, which provides a different partition of forms into paradigms. This is done through a `flexeme` column in the forms table, which refers to identifiers in the `flexeme` table. Thus, we need to add three things in the schemas.

In the forms schema, we need to define the column, as shown above, as well as the foreign key relation to the flexeme table:

```python 
forms_schema = { 
                 "foreignKeys": [{"field": "flexeme",
                                  "reference":
                                    { "resource": "flexemes",
                                     "field":"flexeme_id"
                                     }
                                  }],
                 "fields": [{"name": "flexeme",
                       "title": "reference to a flexeme identifier",
                       "description": "A flexeme to which a form belongs.",
                       "type":"string",
                        "constraints": { "required": true }
                      }]
              }
```

In the flexeme schema, we define the `flexeme_id` column (we would probably need to define more columns), and declare it as the identifier (primary key):


```python

flexemes_schema = {
                   "primaryKey": "flexeme_id"
                   "fields": [{"name": "flexeme_id",
                               "title": "identifier for a flexeme",
                               "description": "the flexeme id identifies a single flexeme",
                               "type":"string",
                               "constraints": { "required": true }
                          }]
                    }

```

This is then passed to the paralex factory as follows:

```python title="gen-metadata.py"
from paralex import paralex_factory

package = paralex_factory("Vulcan Verbal Paradigms", 
            {"forms": {"path": "vulcan_v_forms.csv",
                        "schema": forms_schema,
                        },
              "flexemes": {"path": "vulcan_v_flexemes.csv",
                           "schema": flexemes_schema,
                           },
              "lexemes": {"path": "vulcan_v_lexemes.csv"},
              # etc, for other tables
            },
            citation = "Spock and al (2258). Vulcan Verbal Paradigms dataset. Online.",
            # More metadata here
            )
```

## Ensuring high quality data

### Frictionless validation

The metadata generated above, and saved in the json file `vulcan.package.json` can now be used to [validate the dataset using frictionless](https://frictionlessdata.io/software/#software-toolkit). Frictionless should have been installed as a dependency when you installed `paralex`. You can now run:

```bash title="Checking against the metadata"
frictionless validate vulcan.package.json
```

This will check that all the tables exist and are well formed, and that columns
contain the types and contents declared by the metadata file, and that any constraints
on columns (such as being a value from a specific set of predefined values, being
unique, being obligatory, having maximum or minimum values, etc) are respected. Note that
the following requirements will also be checked for:

- All identifiers MUST be unique, that is to say, no two rows in their table has the
  same value in `form_id`, `cell_id`, `lexeme_id`, `feature_id`, or `sound_id`.
- All values in the `cell` column of the forms MUST correspond to an identifier in
  `cell_id` of the `cells` table if it exists;
- All values in the `lexeme` column of the forms MUST correspond to an identifier
  in `lexeme_id` of the `lexemes` table if it exists
- If there is a `sounds` table, then the `phon_form` in `forms` MUST be
  composed
  only of sound identifiers and spaces.
- If there is a `cells` table and a `features` table, then the `cell_id` in `cells`
  MUST be composed only of feature identifiers found in `feature_id`, separated by dots, following the Leipzig glossing rules convention.

### Paralex validation

Any frictionless dataset can be checked against its metadata. In addition, to check that the dataset is in fact a paralex lexicon, you can use the `paralex validate` command as follows:

```bash title="Checking against the standard itself"
paralex validate vulcan.package.json
```

This attempts to check all of the MUST and SHOULD statements from the [standard](standard.md). 

### Testing

In addition, you might want to check or to constrain additional properties of the data. Some constraints can be expressed in the package metadata, see the [frictionless doc on constraints](https://specs.frictionlessdata.io/table-schema/#constraints).

For more checks, we recommend writing
*tests* in the programming language of your choice, which read the data and automatically verify sets of expected properties. For example, you might want to check:

- That the number of rows in each table conforms to your expectations (thereby checking that you did not add rows anywhere by mistake)
- Complex verifications on the phonological form (this serves to avoid obvious mistakes in the phonemic transcriptions), for example ensuring that every word has a stress marker.
- Logical properties: for example, that defective forms do not have positive frequencies (if that is relevant !)
- etc.

## Publishing

### The raw data files

We recommend publishing the completed dataset as an online repository, such as on github or gitlab.

The repository should contain:

- the data, in the form of csv tables
- the metadata, in the form of a json file (this is a frictionless _package_ file)
- the documentation files, at the minimum a README.md file
- a license file
- the code:
    - the metadata python script `gen-metadata.py`
    - the tests if they exist
    - when possible, legal, and practical: a link to any automated process used to generate the data, or any related repository used to generate it.

When using git, a simple way to do this is the `git archive` command. For example, the following command will create a zip archive for a repository at the current revision (HEAD):

```shell
git archive -o vulcan_verbs.zip HEAD
```

It is possible to include just a sub-folder in the archive, for example if the sub-folder is called `distrib`:

```shell
git archive -o vulcan_verbs.zip HEAD distrib
```

Only files versionned with git will be included, but they will all be included. To exclude some files, use a [`.gitattributes` file](https://git-scm.com/docs/gitattributes). Here is an example:

```gitexclude title=".gitattributes"
.zenodo.json       export-ignore
.gitlab-ci.yml     export-ignore
.gitattributes     export-ignore
.gitignore     export-ignore
mkdocs.yml     export-ignore
```


## Archiving

We recommend archiving the data by creating a record on some archival service, for
example [zenodo](https://zenodo.org/). A good practice would be to set up automatic
archives for new versions. This can be done natively from github, or can be done using
[gitlab2zenodo](https://pypi.org/project/gitlab2zenodo/).

To have a DOI generated by zenodo in the metadata, first make a draft deposit, filling in the metadata, and checking the box for pre-registering a DOI. Then copy this DOI, add it to your README.md file and your metadata, generate an archive, and upload this to zenodo before publishing the record.

To have your dataset officially listed as a paralex lexicon, add it to the [Paralex zenodo community](https://zenodo.org/communities/paralex/)

