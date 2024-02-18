# Shaped CLI

CLI for interactions with the Shaped API.

## Installing the Shaped CLI

```
pip install shaped
```

## Initialize

```
shaped init --api-key <API_KEY>
```

## Model API

### Create Model (File)

```
shaped create-model --file <PATH_TO_FILE>
```

### Create Model (STDIN)

```
cat $(PATH_TO_FILE) | shaped create-model
```

### List Models

```
shaped list-models
```

### View Model

```
shaped view-model --model-name <MODEL_NAME>
```

## Delete Model

```
shaped delete-model --model-name <MODEL_NAME>
```

## Dataset API

### Create Dataset

```
shaped create-dataset --file <PATH_TO_FILE>
```

### List Datasets

```
shaped list-datasets
```

### Dataset Insert

```
shaped dataset-insert --dataset-name <DATASET_NAME> --file <DATAFRAME_FILE> --type <FILE_TYPE> 
```

## Delete dataset

```
shaped delete-dataset --dataset-name <DATASET_NAME>
```

## Rank API

### Rank

```
shaped rank --model-name <MODEL_NAME> --user-id <USER_ID>
```

### Similar Items

```
shaped similar --model-name <MODEL_NAME> --item-id <ITEM_ID>
```

### Similar Users

```
shaped similar --model-name <MODEL_NAME> --user-id <USER_ID>
```

# Development

## Installing the Shaped CLI from Test PyPI

Upon all pushes to main branch, a new version of the CLI is published to Test PyPI. To install the latest version of the CLI from Test PyPI, run the following commands:

```bash
conda create -n cli-dev python=3.9
conda activate cli-dev
export PACKAGE_VERSION={} # Specify the version you want to install
pip install --extra-index-url https://test.pypi.org/simple/ shaped-cli==$PACKAGE_VERSION
```

## Releasing a new CLI version to PyPI

To release a new version of the CLI to PyPI, open a PR changing the version of the package in `setup.py`, following [Semantic Versioning](https://semver.org) principles, e.g. `0.1.1`.

CircleCI will generate an approval prompt when this branch is merged to main, and upon approval will publish to PyPI.
