# decision-utils

![Github CI](https://github.com/justmars/decision-utils/actions/workflows/main.yml/badge.svg)

Preprocess frontmatter-formatted markdown with Philippine artifacts, statutes, citations.

> [!IMPORTANT]
> This is a dependecy of [citelaws-builder](https://github.com/justmars/citelaws-builder).

## Installation

```sh
just start # install .venv
```

## PyPi

```sh
just dumpenv # pypi token
just publish # uses build / twine
```

## Concept

See structured content based on file path:

```py
from decision_utils import Decision

file = next(Path().home().joinpath("corpus-decisions").glob("gr/**/2023*/main*"))
metadata = Decision.from_file(file)
meta.main_opinion.segments
meta.separate_opinions #
```

## Watcher

When modifying files in the corpus-decisions directory (outside of this package), cleaning/modifying the markdown file is implemented by `utils.update_content()`.

```sh
watch # uses default ../corpus-decisions
```

## Components

1. `Decision` - at least consisting of a single main opinion with optional separate opinions

   1. `Writer`- a justice who may pen an opinion (anonymous _per curiam_ opinions are marked as such)

   2. `Voteline` - how the other justices voted in a decision re: each opinion

   3. `Opinion` - authored by a writer, can consist of a _body_ (with or without an _annex_)

      1. `Body` - content of the opinion

         1. `Block` - a body division based on a natural or commented header in the body

            1. `Chunk` - a formula-based division of a block

               1. `Passage` - chunk divided into sentences _which end in footnotes_.

          > [!NOTE]
          > Based on block-chunk setups, it may be
          possible to use FTS only on `ruling` `issue` `preface` `fallo` chunks as searchable segments that can also have embeddings.

      2. `Annex` - if the body contains footnotes, the annex is the reference area of an opinion containing the value of footnotes; it can can be subdivided into the area of each footnote

         1. `Footnote`

   4. `Artifact` - each opinion will contain relevant certain phrases/entities divided into overlapping `ArtifactCategory`:

      1. For "citation"-based artifacts, a `citation` may consist of `vs`, `docket`, and `ref` (aside from the date).

      2. For "statute"-based artifacts, a `statute` may consist of `unit`, `rule`, (aside from the date).

## Limits

### Blocks

- [x] Heading includes footnote

      ## Regional Trial Court[^1]

- [ ] Heading may be prefixed by a Roman Numeral, Number, and/or Letter

      ## I. Facts

- [ ] Heading includes parenthesis

      ## Regional Trial Court (Sample Text)

### Chunks

1. Blocks can only create proper chunks if the block is formatted properly
2. For instance if an ` xxx ` is in between blockquotes and not preceded by a `>` indicator, this will result in multiple chunks rather than a single one.

    >

    xxx xxx xxx

    > As we outlined above, **a temporary total disability only becomes permanent when so declared by the company physician within the periods he is allowed to do so, or upon the expiration of the maximum 240-day medical treatment period without a declaration of either fitness

## Todo

- [ ]`^\*+[^\*]{1,60}(?!\*)\n` detect short strings that ought to be converted into headings
- [ ] The `formatter()` needs to exclude indented enumerations in removing pre-line spaces
- [ ] Create tests per component
