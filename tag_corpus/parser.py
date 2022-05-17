from dataclasses import dataclass, field
from typing import List, Optional, Union

from spacy import Language, Vocab
from spacy.tokens import Doc


@dataclass
class Parser:
    vendor: str
    model_or_lang: str
    is_tokenized: bool = False
    disable_sbd: bool = False
    verbose: bool = False
    stanza_processors: Optional[str] = field(default_factory=str)
    exclude_spacy_components: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.vendor == "spacy":
            from spacy_download import load_spacy

            exclude = ["senter", "sentencizer"] if self.disable_sbd else []
            exclude = exclude + self.exclude_spacy_components
            nlp = load_spacy(self.model_or_lang, exclude=exclude)
            if self.is_tokenized:
                nlp.tokenizer = SpacyPretokenizedTokenizer(nlp.vocab)
            if self.disable_sbd:
                try:
                    nlp.add_pipe("disable_sbd", before="parser")
                except ValueError:
                    nlp.add_pipe("disable_sbd", first=True)
        elif self.vendor == "stanza":
            import stanza
            import torch

            is_cuda_available = torch.cuda.is_available()

            stanza.download(self.model_or_lang, verbose=self.verbose)
            nlp = stanza.Pipeline(
                self.model_or_lang,
                processors=self.stanza_processors if self.stanza_processors else {},
                verbose=True,
                tokenize_no_ssplit=self.disable_sbd,
                tokenize_pretokenized=self.is_tokenized,
                use_gpu=is_cuda_available
            )
        else:
            raise ValueError(f"'vendor' must be 'spacy' or 'stanza'")

        self.nlp = nlp

    def __call__(self, *args, **kwargs):
        return self.nlp(*args, **kwargs)

    def pipe(self, *args, **kwargs):
        if self.vendor == "spacy":
            return self.nlp.pipe(*args, **kwargs)
        else:
            raise NotImplemented(f"'pipe()' is not implemented for Stanza")


class SpacyPretokenizedTokenizer:
    """Custom tokenizer to be used in spaCy when the text is already pretokenized."""

    def __init__(self, vocab: Vocab):
        """Initialize tokenizer with a given vocab
        :param vocab: an existing vocabulary (see https://spacy.io/api/vocab)
        """
        self.vocab = vocab

    def __call__(self, inp: Union[List[str], str]) -> Doc:
        """Call the tokenizer on input `inp`.
        :param inp: either a string to be split on whitespace, or a list of tokens
        :return: the created Doc object
        """
        if isinstance(inp, str):
            words = inp.split()
            spaces = [True] * (len(words) - 1) + ([True] if inp[-1].isspace() else [False])
            return Doc(self.vocab, words=words, spaces=spaces)
        elif isinstance(inp, list):
            return Doc(self.vocab, words=inp)
        else:
            raise ValueError("Unexpected input format. Expected string to be split on whitespace, or list of tokens.")


@Language.factory("disable_sbd")
def create_spacy_disable_sentence_segmentation(nlp: Language, name: str):
    return SpacyDisableSentenceSegmentation()


class SpacyDisableSentenceSegmentation:
    """Disables spaCy's dependency-based sentence boundary detection. In addition, senter and sentencizer components
    need to be disabled as well."""

    def __call__(self, doc: Doc) -> Doc:
        for token in doc:
            token.is_sent_start = False
        return doc
