import unidecode
import string
from joblib import dump, load
from sklearn.feature_extraction.text import CountVectorizer
from spacy.lang.en import English


class Pipe:
    """
    Pipe class for TokenEase.
    choices in the pipeline:
    - 'strip_accents' : remove accents from the text (default: True)
    - 'lowercase' : convert text to lowercase (default: True)
    - 'remove_stop_words' : remove_stop_words text (default: False)
    - 'max_df' : remove tokens that appear in more than max_df documents (default: 1.0)
    - 'min_df' : remove tokens that appear in less than min_df documents (default: 1)
    - 'max_token_length' : remove tokens that are longer than max_token_length (default: 15)
    - 'doc_start_token' : start of document token.
    - 'doc_end_token' : end of document token.
    - 'unk_token' : replace unknown tokens with unk_token (default: None)
    - 'email_token' : replace emails with email_token (default: None)
    - 'url_token' : replace urls with url_token (default: None)
    - 'number_token' : replace numbers with number_token (default: None)
    - 'alpha_num_token' : replace alpha-numeric tokens with alpha_num_token (default: None)
    - 'seperator' : seperator for the tokens (default: "||--sep--||")
    """

    def __init__(
        self,
        strip_accents: bool = True,
        lowercase: bool = True,
        remove_stop_words: bool = False,
        max_df: float = 1.0,
        min_df: float = 1,
        max_token_length: int = 15,
        doc_start_token: str = "[DOC_START]",
        doc_end_token: str = "[DOC_END]",
        unk_token: str = "[UNK]",
        email_token: str = "[EMAIL]",
        url_token: str = "[URL]",
        number_token: str = "[NUMBER]",
        alpha_num_token: str = "[ALPHA_NUM]",
        seperator: str = "||--sep--||",
    ) -> None:
        self.strip_accents = strip_accents
        self.lowercase = lowercase
        self.remove_stop_words = remove_stop_words
        self.max_df = max_df
        self.min_df = min_df
        self.max_token_length = max_token_length
        self.doc_start_token = doc_start_token
        self.doc_end_token = doc_end_token
        self.unk_token = unk_token
        self.email_token = email_token
        self.url_token = url_token
        self.number_token = number_token
        self.alpha_num_token = alpha_num_token
        self.seperator = seperator

        # spacy init
        self.nlp = English()

        if self.remove_stop_words:
            stop_words = list(self.nlp.Defaults.stop_words)  # get spacy stopwords
            # add punctuation to stop words
            stop_words.extend(list(string.punctuation))
            # special tokens
            special_tokens = [
                self.doc_start_token,
                self.doc_end_token,
                self.unk_token,
                self.email_token,
                self.url_token,
                self.number_token,
                self.alpha_num_token,
            ]
            stop_words.extend([token for token in special_tokens if token is not None])
        else:
            stop_words = None

        # count vectorizer
        self.vectorizer = CountVectorizer(
            tokenizer=self._tokenizer,
            token_pattern=None,
            lowercase=False,
            stop_words=stop_words,
            min_df=min_df,
            max_df=max_df,
        )
        self.trained = False

        # return variables
        self.vocab = None

    def fit_transform(self, docs: list[str]):
        """
        This method is used to register and fit the data to the pipeline. It also returns the bag of words for the data.
        """
        # normalizing all the document strings.
        docs = self.__normalize(docs)
        docs = self.__tokenize_data(docs)
        bow = self.vectorizer.fit_transform(docs).toarray()
        self.vocab = self.vectorizer.vocabulary_
        self.trained = True
        return bow, docs

    def transform(self, docs: list[str]):
        """
        This method is used to get the bag of words for a document.
        """
        if self.trained is False:
            raise Exception(
                "No data has been registered yet. Please use fit_transform method first."
            )
        docs = self.__normalize(docs)
        docs = self.__tokenize_data(docs)
        bow = self.vectorizer.transform(docs).toarray()
        return bow, docs

    def _tokenizer(self, doc: str):
        """
        Tokenizes the given document based on the specified separator.

        Args:
            doc (str): The document to be tokenized.

        Returns:
            list: A list of tokens extracted from the document.
        """
        return doc.split(self.seperator)

    def __tokenize_data(self, docs: list[str]):
        """
        Tokenizes a list of documents.

        Args:
            docs (list[str]): The list of documents to be tokenized.

        Returns:
            list[str]: The tokenized documents.
        """

        tokenizer = self.nlp.tokenizer
        new_docs = []
        for doc in tokenizer.pipe(docs):
            a_doc = []
            if self.doc_start_token is not None:
                a_doc.append(self.doc_start_token)
            for token in doc:
                if token.is_space:
                    continue
                if len(token.text) > self.max_token_length:
                    continue
                if token.is_alpha:
                    a_doc.append(token.text)
                elif self.number_token is not None and token.is_digit:
                    a_doc.append(self.number_token)
                elif self.email_token is not None and token.like_email:
                    a_doc.append(self.email_token)
                elif self.url_token is not None and token.like_url:
                    a_doc.append(self.url_token)
                elif self.alpha_num_token is not None and token.text.isalnum():
                    a_doc.append(self.alpha_num_token)
                elif self.unk_token is not None and token.is_oov:
                    a_doc.append(self.unk_token)
                else:
                    a_doc.append(token.text)
            if self.doc_end_token is not None:
                a_doc.append(self.doc_end_token)
            new_docs.append(self.seperator.join(a_doc))
        return new_docs

    def __normalize(self, docs: list[str]):
        """
        Normalize the given list of documents.

        Args:
            docs (list[str]): The list of documents to be normalized.

        Returns:
            list[str]: The normalized list of documents.
        """
        new_docs = []
        for doc in docs:
            if self.strip_accents:
                doc = unidecode.unidecode(doc)
            if self.lowercase:
                doc = doc.lower()
            new_docs.append(unidecode.unidecode(doc))
        return new_docs

    @classmethod
    def from_pretrained(cls, filename):
        """
        Load a pipeline from a file.

        Parameters:
        filename (str): The name of the file (path) to load the pipeline from.

        Returns:
        Pipe: The loaded pipeline object.
        """
        return load(filename)

    def save(self, filename):
        """
        Save the pipeline to a file.

        Parameters:
        filename (str): The name of the file to save the pipeline to.
        """
        dump(self, filename)

    @property
    def vocabulary(self):
        """
        Get the vocabulary.

        Returns:
            The vocabulary if it has been registered, otherwise raises an exception.
            The vocabulary is in the form of a dictionary where the keys are the tokens (words) and the values are the indices.
        """
        if self.vocab is None:
            raise Exception("No data has been registered yet.")
        return self.vocab

    @vocabulary.setter
    def vocabulary(self, value):
        raise AttributeError("Vocabulary cannot be set directly")

    @vocabulary.deleter
    def vocabulary(self):
        raise AttributeError("Vocabulary cannot be deleted")
