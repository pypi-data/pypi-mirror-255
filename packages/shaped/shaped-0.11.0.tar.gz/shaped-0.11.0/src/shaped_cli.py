import json
import sys
import yaml
from pathlib import Path
from pydantic import BaseModel
import pandas as pd
import pyarrow.parquet as pq
from tqdm import tqdm

import typer
from typing import Optional
import requests


APP_NAME = "SHAPED_CLI"

app = typer.Typer()


class Config(BaseModel):
    api_key: str
    env: str


def _write_config(config: Config):
    app_dir_path = Path(typer.get_app_dir(APP_NAME))
    app_dir_path.mkdir(parents=True, exist_ok=True)
    config_path = app_dir_path / "config.json"
    with open(config_path, "w") as f:
        f.write(config.json())


def _read_config() -> Config:
    app_dir_path = Path(typer.get_app_dir(APP_NAME))
    config_path = app_dir_path / "config.json"
    with open(config_path, "r") as f:
        config = Config.parse_raw(f.read())

    return config


def _get_shaped_url(config: Config) -> str:
    return f"https://api.{config.env}.shaped.ai/v1"


def _parse_file_as_json(file: typer.FileText) -> str:
    """
    Parse file contents as JSON string, converting from YAML if necessary.
    """
    if file.name.endswith(".json"):
        return json.dumps(json.load(file), indent=2)
    elif file.name.endswith(".yml") or file.name.endswith(".yaml"):
        return json.dumps(yaml.load(file, Loader=yaml.FullLoader), indent=2)
    else:
        raise ValueError(
            "Unsupported file type. Must be one of '.json', '.yml', or '.yaml'. "
            f"file_name={file.name}"
        )


def _parse_response_as_yaml(content: str) -> str:
    # Parse JSON response as YAML for pretty printing.
    return yaml.dump(json.loads(content), sort_keys=False)


@app.command()
def init(api_key: str = typer.Option(...), env: str = typer.Option("prod")):
    config = Config(api_key=api_key, env=env)
    _write_config(config)
    typer.echo(f"Initializing with config: {config.dict()}")


@app.command()
def create_model(
    file: typer.FileText = typer.Option(None),
):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/models"
    headers = {"accept": "application/json", "x-api-key": config.api_key}

    if not sys.stdin.isatty():
        payload = sys.stdin.read()
    elif file is not None:
        payload = _parse_file_as_json(file)
    else:
        raise ValueError("Must provide either a '--file' or stdin input.")

    typer.echo(payload)
    response = requests.post(url, headers=headers, data=payload)
    typer.echo(_parse_response_as_yaml(response.text))


@app.command()
def update_model(file: typer.FileText = typer.Option(None)):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/models"
    headers = {"accept": "application/json", "x-api-key": config.api_key}

    if not sys.stdin.isatty():
        payload = sys.stdin.read()
    elif file is not None:
        payload = _parse_file_as_json(file)
    else:
        raise ValueError("Must provide either a '--file' or stdin input.")

    typer.echo(payload)
    response = requests.patch(url, headers=headers, data=payload)
    typer.echo(_parse_response_as_yaml(response.text))


@app.command()
def list_models():
    config = _read_config()
    url = f"{_get_shaped_url(config)}/models"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    response = requests.get(url, headers=headers)
    typer.echo(_parse_response_as_yaml(response.text))


@app.command()
def view_model(model_name: str = typer.Option(...)):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/models/{model_name}"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    response = requests.get(url, headers=headers)
    typer.echo(_parse_response_as_yaml(response.text))


@app.command()
def delete_model(model_name: str = typer.Option(...)):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/models/{model_name}"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    response = requests.delete(url, headers=headers)
    typer.echo(_parse_response_as_yaml(response.text))


@app.command()
def rank(
    model_name: str = typer.Option(...),
    user_id = typer.Option(None),
    limit=typer.Option(15),
    filter_predicate=typer.Option(None),
    text_query: str = typer.Option(None),
    return_metadata: bool = typer.Option(False),
    flush_paginations: bool = typer.Option(False),
    exploration_factor: float = typer.Option(0.0),
    diversity_factor: float = typer.Option(0.0),
    extra_query_args: str = typer.Option(None)
):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/models/{model_name}/rank"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    if exploration_factor < 0.0 or exploration_factor > 1.0:
        raise typer.BadParameter("`exploration_factor` must be between 0.0 and 1.0")

    if diversity_factor < 0.0:
        raise typer.BadParameter("`diversity_factor` must be greater than 0.0")

    query_args = {
        "exploration_factor": exploration_factor,
        "diversity_factor": diversity_factor,
        "limit": str(limit)
    }

    if user_id is not None:
        query_args |= {"user_id": user_id}
    if filter_predicate is not None:
        query_args |= {"filter_predicate": filter_predicate}
    if return_metadata is not None:
        query_args |= {"return_metadata": bool(return_metadata)}
    if text_query is not None:
        query_args |= {"text_query": text_query}
    if flush_paginations is not None:
        query_args |= {"flush_paginations": flush_paginations}
    if extra_query_args is not None:
        extra_query_args = json.loads(extra_query_args)
        query_args |= extra_query_args

    response = requests.post(
        url,
        headers=headers,
        json=query_args
    )
    typer.echo(_parse_response_as_yaml(response.text))


@app.command()
def similar(
    model_name: str = typer.Option(...),
    user_id: Optional[str] = typer.Option(None),
    item_id: Optional[str] = typer.Option(None),
    limit=typer.Option(15),
):
    config = _read_config()
    assert bool(user_id) + bool(item_id) == 1, "Must provide either user_id or item_id."
    url = f"{_get_shaped_url(config)}/models/{model_name}/similar?limit={limit}"
    if user_id is not None:
        url += f"&user_id={user_id}"
    if item_id is not None:
        url += f"&item_id={item_id}"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    response = requests.get(url, headers=headers)
    typer.echo(_parse_response_as_yaml(response.text))

@app.command()
def similar_items(
    model_name: str = typer.Option(...),
    item_id: str = typer.Option(...),
    user_id: Optional[str] = typer.Option(None),
    limit=typer.Option(15),
):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/models/{model_name}/similar_items"
    url += f"?limit={limit}&item_id={item_id}"
    if user_id is not None:
        url += f"&user_id={user_id}"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    response = requests.get(url, headers=headers)
    typer.echo(_parse_response_as_yaml(response.text))

@app.command()
def similar_users(
    model_name: str = typer.Option(...),
    user_id: str = typer.Option(...),
    limit=typer.Option(15),
):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/models/{model_name}/similar_users"
    url += f"?limit={limit}&user_id={user_id}"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    response = requests.get(url, headers=headers)
    typer.echo(_parse_response_as_yaml(response.text))


@app.command()
def create_dataset_from_uri(
    name: str = typer.Option(...),
    path: str = typer.Option(...),
    type: str = typer.Option(...)
):
    chunks = _read_chunks(path, type, chunk_size=1)
    chunk = next(iter(chunks))
    if chunk is None:
        raise ValueError("No data found in file.")

    chunk_columns = list(chunk.columns)
    if chunk_columns == 0:
        raise ValueError("No columns found.")

    chunk_column_definitions = {col: "String" for col in chunk_columns}
    dataset_definition = {
        "dataset_name": name,
        "schema_type": "CUSTOM",
        "schema": chunk_column_definitions,
    }
    _create_dataset_from_payload(json.dumps(dataset_definition))
    dataset_insert(name, path, type)



@app.command()
def create_dataset(file: typer.FileText = typer.Option(None)):
    if not sys.stdin.isatty():
        payload = sys.stdin.read()
    elif file is not None:
        payload = _parse_file_as_json(file)
    else:
        raise ValueError("Must provide either a '--file' or stdin input.")

    _create_dataset_from_payload(payload)


def _create_dataset_from_payload(payload: str):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/datasets"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    typer.echo(payload)
    response = requests.post(url, headers=headers, data=payload)
    typer.echo(_parse_response_as_yaml(response.text))


@app.command()
def list_datasets():
    config = _read_config()
    url = f"{_get_shaped_url(config)}/datasets"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    response = requests.get(url, headers=headers)
    typer.echo(_parse_response_as_yaml(response.text))

@app.command()
def view_dataset(dataset_name: str = typer.Option(...)):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/datasets/{dataset_name}"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    response = requests.get(url, headers=headers)
    typer.echo(_parse_response_as_yaml(response.text))

@app.command()
def dataset_insert(
    dataset_name: str = typer.Option(...),
    file: str = typer.Option(...),
    type: str = typer.Option(...),
):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/datasets/{dataset_name}/insert"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    bar = tqdm(unit=" Records")

    def _write_chunk(chunk: pd.DataFrame):
        bar.update(len(chunk))
        payload = json.dumps({"data": json.loads(chunk.to_json(orient="records"))})
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            typer.echo(response.text)
            return

        _parse_response_as_yaml(response.text)

    # Chunk read and upload.
    for chunk in _read_chunks(file, type, chunk_size=1000):
        _write_chunk(chunk)


def _read_chunks(file: str, type: str, chunk_size: int) -> pd.DataFrame:
    if type == "parquet":

        # Note this only works for parquet partitions (i.e. single binary files).
        parquet = pq.ParquetFile(file)
        for chunk in parquet.iter_batches(batch_size=chunk_size):
            yield chunk.to_pandas()

    elif type == "csv":
        with pd.read_csv(file, chunksize=chunk_size) as reader:
            for chunk in reader:
                yield chunk

    elif type == "tsv":
        with pd.read_csv(file, chunksize=chunk_size, sep="\t") as reader:
            for chunk in reader:
                yield chunk

    elif type in ["json", "jsonl"]:
        with pd.read_json(file, chunksize=chunk_size, lines=True) as reader:
            for chunk in reader:
                yield chunk

    else:
        raise NotImplementedError(f"Type '{type}' not implemented.")


@app.command()
def delete_dataset(dataset_name: str = typer.Option(...)):
    config = _read_config()
    url = f"{_get_shaped_url(config)}/datasets/{dataset_name}"
    headers = {"accept": "application/json", "x-api-key": config.api_key}
    response = requests.delete(url, headers=headers)
    typer.echo(_parse_response_as_yaml(response.text))


if __name__ == "__main__":
    app(prog_name="shaped")
