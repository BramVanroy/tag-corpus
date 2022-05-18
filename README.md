# Process corpora with spaCy or stanza

## Installation

1. Download or clone this repository.
2. Install it by first entering the cloned repo `cd tag-corpus` and then installing it with `pip install .`
3. Now you can use it with the `parse` command on the command line! Use `parse -h` for instructions.

## Usage

After installation the `parse` command is available on your command line. There are a couple of options available.
To see all of them, use `parse -h`. 

### Language model and vendor (spaCy or stanza)

The tool currently supports spaCy and stanza. To run `parse`, the first two required arguments are a model name and 
vendor. A "vendor" is `spacy` or `stanza`. The model name differs depending on the vendor. Models will be downloaded 
automatically. That means that *a first run for a model is slow* because it is first downloading the model.
Follow-up runs should be considerably faster.

- spaCy models can be found [here](https://spacy.io/usage/models/) (e.g. `en_core_web_sm` or `nl_core_news_sm`)
- [stanza models](https://stanfordnlp.github.io/stanza/available_models.html) are language codes (e.g. `en`)

Some options are available related to the model:

- `-s`, `--disable_sbd`: disable sentence boundary detection (i.e., sentence segmentation)
- `-t`, `--is_tokenized`: disables tokenization (text will be split by white-space). IMPORTANT: for stanza, this will
also disable sentence segmentation
- `-j`, `--n_process`: (spaCy only) number of processes to use. Set this to >1 if you are processing large files. Does
not really affect performance (perhaps even negatively) if you have a lot of small files

### Input

You can choose to process an input file, all files in an input directory (recursive), or text from the command line.

- `-f`, `--input_item`: a file or directory. If a directory, all input files in it will be processed
- `-a`, `--input_encoding`: encoding of the input file(s) (defaults to system default)
- `-b`, `--input_str`: an alternative to `-f`; a string to process directly from the command line
 

### Output

The output can be written to file(s) or just to the command line.

- `-o`, `--output_item`: must be the same type as `--input_item`. If a directory, the same structure as the one in the
input directory will be used. If not given, will only print to stdout
- `-c`, `--output_encoding`: encoding of the output file(s) (defaults to system default)
- `-v`, `--verbose`: if enabled, always prints the output to stdout - even if `--output_item` is given
- `--formatter`: the format of the output tokens. You can add multiple arguments here but have to choose from `text`,
`lemma`, `pos` and `dep`. The order matters! In the output, these properties for each token will be extracted and 
glued together with `formatter_sep`. E.g., for `--formatter text pos dep` the result for a dog as subject could be
`dog|NOUN|nsubj`
- `--formatter_sep`: if you want a different separator than the default `|` (see `--formatter`)

## Examples

---

Process all files in a directory and write output to directory.

- Stanza / English
- Input: directory `dir/with/files/` (all files in it will be recursively processed)
- Output: directory `processed/` (the structure from the input directory will be preserved)
- Formatter: `text` and `pos` with default separator `|`, e.g. `dog|noun`
- Input encoding `-a`: `utf-8-sig`
- Output encoding `-c`: `utf8`

```shell
parse en stanza -f dir/with/files/ -o processed/ --formatter text pos -a utf-8-sig -c utf8
```

---

Process a single file and write to single output file.

- spaCy / Dutch
- Input: single file `-f` with default encoding, input will not be sentence segmented (`-s`)
- Output: write output to single file `-o`
- Formatter: `text` (so just tokenize)

```shell
parse nl_core_news_sm spacy -f my/file.txt -o my/output/file.txt --formatter text -s
```

---

Process string from the command line.

- spaCy / English
- Input: string `-b`, input is pre-tokenized so do not tokenize (`-t`)
- Output: nothing specified, so write to stdout
- Formatter: `text`. `pos`, `dep` in that order with custom separator `-`

```shell
parse en_core_web_sm spacy -b "I like cookies !" --formatter text pos dep -t --formatter_sep -
# I-PRON-nsubj like-VERB-ROOT cookies-NOUN-dobj !-PUNCT-punct
```

# Copyright

Licensed under MIT. See the license attached to this repository.
