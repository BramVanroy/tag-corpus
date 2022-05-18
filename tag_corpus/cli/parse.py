from argparse import Namespace
from locale import getpreferredencoding
from pathlib import Path
from sys import stdout

from tqdm import tqdm

from tag_corpus.parser import Parser


def process_docs(docs, vendor, formatter, formatter_sep):
    # Collect required information and write to file or stdout
    data = []
    for doc in docs:
        sentences = doc.sents if vendor == "spacy" else doc.sentences
        for sent in sentences:
            sent_repr = []
            tokens = sent if vendor == "spacy" else sent.words
            for t in tokens:
                sent_repr.append(formatter_sep.join([getattr(t, attr) for attr in formatter]))
            data.append(" ".join(sent_repr))

    return "\n".join(data) + "\n"


def get_docs(lines, parser, n_process):
    if parser.vendor == "spacy":
        docs = parser.pipe(lines, n_process=n_process)
    else:
        import stanza
        in_docs = [stanza.Document([], text=d) for d in lines]
        docs = parser(in_docs)

    return docs

def parse(args: Namespace):
    if not args.input_str and not args.input_item:
        raise ValueError("'input_str' or 'input_item' must be given")

    # Only select the required components for optimal speed
    exclude_spacy_components = ["ner"]
    stanza_processors = {}
    if args.vendor == "spacy":
        if "lemma" not in args.formatter:
            exclude_spacy_components.append("lemmatizer")
        if "pos" not in args.formatter:
            exclude_spacy_components.append("tagger")
        if "dep" not in args.formatter and args.disable_sbd:
            exclude_spacy_components.append("parser")
    else:
        stanza_processors = ["tokenize"]
        if "lemma" in args.formatter:
            stanza_processors.append("lemma")
        if "pos" in args.formatter:
            stanza_processors.append("pos")
        if "dep" in args.formatter:  # depparse requires pos and lemma components
            stanza_processors.extend(["pos", "lemma", "depparse"])

        stanza_processors = ",".join(set(stanza_processors))

    parser = Parser(args.vendor, args.model_or_lang, args.is_tokenized, args.disable_sbd,
                    stanza_processors=stanza_processors,
                    exclude_spacy_components=exclude_spacy_components)

    # Convert formatter attrs to vendor-specific ones
    if args.vendor == "spacy":
        args.formatter = ["text" if attr == "text" else f"{attr}_" for attr in args.formatter]
    else:
        mapping = {"text": "text", "lemma": "lemma", "pos": "upos", "dep": "deprel"}
        args.formatter = [mapping[attr] for attr in args.formatter]

    # Prepare data and run parser
    files = []
    if args.input_item:
        pin = Path(args.input_item).resolve()
        input_is_dir = pin.is_dir()
        files = [pin] if not input_is_dir else [f for f in pin.rglob("*") if f.is_file()]

        for pfin in tqdm(files, desc="File"):
            text = pfin.read_text(encoding=args.input_encoding)
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            docs = get_docs(lines, parser, args.n_process)
            data = process_docs(docs, args.vendor, args.formatter, args.formatter_sep)

            if args.output_item is not None:
                pfout = Path(args.output_item) / pfin.relative_to(pin)
                pfout.parent.mkdir(exist_ok=True, parents=True)
                pfout.write_text(data, encoding=args.output_encoding)
                if args.verbose:
                    print(data)
            else:
                stdout.write(data)
    else:
        text = args.input_str
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        docs = get_docs(lines, parser, args.n_process)
        data = process_docs(docs, args.vendor, args.formatter, args.formatter_sep)

        if args.output_item is not None:
            pfout = Path(args.output_item)
            pfout.parent.mkdir(exist_ok=True, parents=True)
            pfout.write_text(data, encoding=args.output_encoding)
            if args.verbose:
                print(data)
        else:
            stdout.write(data)


def main():
    import argparse

    cparser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Sentence and token segment, and parse and tag an input string or input file with spaCy or stanza",
    )

    # Input arguments
    cparser.add_argument(
        "-f",
        "--input_item",
        default=None,
        help="Path to directory or file with sentences to parse. Has precedence over 'input_str'. If a directory,"
             " all files in it will be processed recursively.",
    )
    cparser.add_argument(
        "-a",
        "--input_encoding",
        default=getpreferredencoding(),
        help="Encoding of the input file. Default value is system default.",
    )
    cparser.add_argument("-b", "--input_str", default=None, help="Input string to parse.")

    # Output arguments
    cparser.add_argument(
        "-o",
        "--output_item",
        default=None,
        help="Path to output file or directory if input_item is also a directory. If input_item is a directory and"
             " this is a directory, then the structure of the input directory will be maintained in this new directory."
             " If not specified, the output will be printed on standard output.",
    )
    cparser.add_argument(
        "-c",
        "--output_encoding",
        default=getpreferredencoding(),
        help="Encoding of the output file. Default value is system default.",
    )

    cparser.add_argument("--formatter",
                         nargs="+",
                         choices=["text", "pos", "dep", "lemma"],
                         default=["text"],
                         help="The properties of tokens to write to the output file, separate by 'formatter_sep'."
                              " So for instance, for '--formatter text pos dep' -> 'dog|noun|subj. By default, it only"
                              " tokenizes, e.g. 'dog'")
    cparser.add_argument("--formatter_sep", default="|", help="The separator to use in conjunction with 'format'.")

    cparser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="Whether to always print the output to stdout, regardless of 'output_item'.",
    )

    # Model/pipeline arguments
    cparser.add_argument(
        "model_or_lang",
        help="Model or language to use. SpaCy models must be pre-installed, stanza and udpipe models will be"
             " downloaded automatically",
    )
    cparser.add_argument(
        "vendor",
        choices=["spacy", "stanza"],
        help="Which parser to use. Parsers other than 'spacy' or 'stanza'",
    )
    cparser.add_argument(
        "-s",
        "--disable_sbd",
        default=False,
        action="store_true",
        help="Whether to disable automatic sentence boundary detection. In practice, disabling means that"
             " every line will be parsed as one sentence, regardless of its actual content.",
    )
    cparser.add_argument(
        "-t",
        "--is_tokenized",
        default=False,
        action="store_true",
        help="Whether your text has already been tokenized (space-seperated). IMPORTANT: for stanza, this will also"
             " disable sentence segmentation",
    )

    # Additional arguments
    cparser.add_argument(
        "-j",
        "--n_process",
        type=int,
        default=1,
        help="Number of processes to use in nlp.pipe(). -1 will use as many cores as available. Only works for spaCy",
    )

    cargs = cparser.parse_args()
    parse(cargs)


if __name__ == "__main__":
    main()
