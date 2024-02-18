# TokenEase
TokenEase is a versatile and efficient tokenizer, designed to streamline the process of converting text into bag-of-words (BoW) vectors for natural language processing tasks. With its customizable options, TokenEase provides a smooth and seamless experience for developers and researchers alike. It is built on top of the popular `spaCy` and CountVectorizer from `scikit-learn` libraries, and is designed to be easy to use and integrate into your existing projects. It only supports English language at the moment. If you are interested in contributing to the project, please make a pull request or open an issue.

## Installation
Installation using pip:
    
```bash
pip install tokenease
```

Installation from source (easy to do if you want to contribute or modify the code!):

Ideally create a virtual environment for Python 3.10+ and install poetry. Then install tokenease with poetry:

```bash
poetry install
```

## Usage
Here's a simple usage guide for the Pipe class that you can include in your README.md:

The `Pipe` class is used to preprocess text data for natural language processing tasks. It provides a pipeline that can perform various transformations on the text data, such as removing accents, converting to lowercase, removing stop words, and tokenizing the text.

Here's a basic example of how to use the `Pipe` class:

```python
from tokenease import Pipe

# Initialize the pipeline with the desired options
pipe = Pipe(strip_accents=True, lowercase=True, remove_stop_words=True)

# Fit the pipeline to your data and transform it into a bag of words representation
bow, docs = pipe.fit_transform(my_data)

# Transform new data using the fitted pipeline
new_bow, new_docs = pipe.transform(new_data)

# bow is a numpy array of shape (n_samples, n_features).
# docs is a list of strings, where each string is a document in the tokenized form with separator.
```

### Saving and Loading the Pipeline
You can save the state of the pipeline to a file and load it later. This is useful if you want to reuse the same pipeline across multiple sessions or scripts.

Here's how you can do it:

```python
# Save the pipeline
pipe.save('my_pipeline.joblib')

# Load the pipeline
loaded_pipe = Pipe.from_pretrained('my_pipeline.joblib')
```

### Accessing the Vocabulary
After fitting the pipeline to your data, you can access the vocabulary (i.e., the set of unique tokens {tokens: indices}) like this:

```python
# Get the vocabulary
vocab = pipe.vocabulary
```

Please note that this is a basic guide and you might need to adjust it based on the specific features and requirements of your project.