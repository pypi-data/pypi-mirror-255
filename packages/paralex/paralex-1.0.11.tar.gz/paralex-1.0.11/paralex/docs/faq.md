## What size should a lexicon be ?

The standard does not impose constraints on the size of the lexicon. The number of 
cells is dependent on the language and the analysis. The number of lexemes is dependent on the
language, part of speech, and available documentation. The number of forms in the end
is roughly the product of the number of cells and lexemes (though overabundance,
defective, and other variations can have an impact on this). The more lexemes
documented the better. In less documented languages, it might be useful to create a
lexicon with less than 100 lexemes, or a few hundred. In well-documented languages,
one might aim for a few thousand. Above this, it is useful to use frequency information to filter out or annotate very rare lexemes.

## Is it necessary to include all the information described in the standard?

Minimally, a valid paralex lexicon includes a `forms` table with just a few columns: `form_id`, `lexeme`, `cell`, and either `phon_form` or `orth_form`; as well as a `.package.json` metadata file. Adding tables for `sounds`, `cells` and `feature-values` is highly recommended in order to make the conventions used in the forms table explicit.

Furthermore, the standard provides optional ways to encode much richer lexicons (accounting for variation, overabundance, defectivity, frequency information, inflection classes, etc.).


## How should one choose a license ?

In choosing licenses, be very careful of respecting existing licenses of material used,
and to respect the [CARE](https://www.gida-global.org/care) principles where relevant. 
When possible, we recommend the usage of open licenses. Some tools exist to help 
choose a specific license, for example [choose a license . com](https://choosealicense.
com/), or the [Creative commons license chooser](https://creativecommons.org/choose/).

## Is it necessary to write python code to use the standard ?

To follow this standard, a dataset only needs to use frictionless metadata (the 
`package.json` file), fit the obligations in the [standard](standard.md) and use the 
[specifications](specs.md). One could perfectly well use other tools and programming 
languages to do this, relying on the default [`paralex.package.json`](https://gitlab.com/sbeniamine/paralex/-/blob/main/paralex/standard/paralex.package.json) which defines 
the standard specifications. 

Writing the metadata `json` file by hand is not a good solution: it is very boring, not a 
very human friendly format, and very easy to make mistakes. Thus, we provide a python package to help out.

We understand that not all dataset creators have someone in their team with the 
relevant expertise to make use of the python package. However, at the end of projects, it 
is common to contract web developers to create a showcase site for the dataset. Our 
suggestion is to use some of this budget to hire someone to do the (very little) 
coding, validation, and writing of tests for the data.

## What is a word ?

Rows of the `forms` table document word forms. But what is a word ? Do clitic 
pronouns, pre-verbs, converbs, etc. belong in the paradigm ? Again, this is a 
matter of analysis, and different choices might be valid for a same set of data. 
Dataset authors are responsible for these analytic choices, and should document them 
explicitly.

If choosing an extensive approach (eg. including material which other analyses might 
separate from the word), we recommend making use of the `segmented_orth_form` and 
`segmented_phon_form` or custom columns to mark the boundaries, making it possible for 
data users to filter them out as needed.

## How is this different from Unimorph ?

Paralex lexicons aim to fill a need for more flexible and precise annotation of 
morphological systems. While we recommend to also provide morphological cells 
using the UNIMORPH schema, many linguistic analyses, 
whether synchronic or diachronic, 
quantitative or qualitative, benefit from also expressing these in other annotation 
scheme, such as Universal Dependency, or language-specific tags. UNIMORPH 
lexicons provide orthographic inflected forms, which is crucial for any applications 
which make use of corpora. However, we find that for linguistic purposes, a phonemic 
or phonetic representation is also important. Furthermore, we provide 
conventions to add rich, linguistically relevant information such as variation (see the [tags 
table](standard.md#tags)), [frequency information](standard.md#frequency), glosses 
(see the [lexeme](standard.md#lexeme) table), comments or alternate notations at 
any level (forms, cells, features, lexemes, frequency, tags) and more.
In order to improve the 
FAIRness and CAREness of datasets, Paralex lexicons add rich 
[frictionless](https://frictionlessdata.io/) metadata and custom [data sheets](https://cacm.acm.org/magazines/2021/12/256932-datasheets-for-datasets/fulltext).

UNIMORPH lexicons can often serve as the basis for Paralex lexicons, with the main 
processing step being to transcribe the orthographic forms into some phonemic or 
phonetic notation; and to carefully add linguistically relevant information.
In the other direction, Paralex lexicons, if they provide an equivalent for each cell in the UNIMORPH schema, 
can easily be exported into valid UNIMORPH lexicons.


## How is this related to CLDF ?

The Paralex standard owes a lot to [CLDF](https://cldf.clld.org/): it is our attempt to apply to inflectional lexicons the data practices disseminated by the [Cross-Linguistic Linked Data project (CLLD)](https://clld.org/). Although the type of datasets, the analyses which can be made of them, and the details of the standard are distinct, Paralex follows the same design principles. Like CLDF datasets, Paralex lexicons are constituted of relational databases written as sets of csv files, and accompanied by metadata in json format. Both also refer (and delegate meaning) to other vocabularies such as Glottolog, CLTS, etc. 
