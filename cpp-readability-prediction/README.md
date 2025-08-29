# Readability for C++

Readability for C++ is a simple CLI tool for extracting readability metrics (features) from
and predicting the readability for the given code snippets.

## Features

- **Extract metric**: Calculate the BuseAndWeimer's, Dorn's, Posnett's,
  and Scalabrino's code readability features of the given directory of code snippets.
- **Compute readability**: Calculate the readability of a given C++ project directory.

## Getting started

To install dependencies, run the following command:

```
python -m venv venv
venv/bin/pip install -r requirements.txt -r requirements-dev.txt
```

The tool extracts metrics from a given code snippet or a directory that contains a list of snippets (no recursive)
and output to a csv file.

To start extracting, run the following command:

```
venv/bin/python readability_for_c/cli.py metrics \
    -i <path-to-snippet-or-directory> \
    -o metrics.csv
```

```
venv/bin/python readability_for_c/cli.py extract-readability    \
    -i <path-to-C++-project-directory>  \ 
    -o readability.csv   \
    -m open_source  \
    -fs bw
```

_Notice: It's required to download some packages (punkt, words, stopwords, wordnet)
so that nltk library can work.
This download will be executed automatically.
However, you can also download those packages in advance and put them inside **$HOME/nltk_data**_

## Command options

### 1. metrics

Calculate the BuseAndWeimer's, Dorn's, Posnett's, and Scalabrino's code readability features
of the given directory of code snippets and save the result to a csv file.

| Option                | Values    | Description                                        |
|:----------------------|:----------|:---------------------------------------------------|
| -i --input (Required) | Path      | Path to a snippet or a directory contains snippets |
| -o --output           | File path | Path to output csv file. Default is "output.csv".  |

### 2. extract-readability

Calculate the readability of a given C++ project directory.

| Option                | Values                                                | Description                                                     |
|:----------------------|:------------------------------------------------------|:----------------------------------------------------------------|
| -i --input (Required) | Dir path                                              | Path to a snippet or a directory contains snippets              |
| -o --output           | File path                                             | Path to output csv file. Default is "output.csv".               |
| -m --model (Required) | open_source, all_merged, space_merged, and space_only | The dataset that model was trained on.                          |
| -fs --feature-set     | all, posnett , scalabrino, dorn , and bw              | The feature set used for prediction. Default depends on --model |
