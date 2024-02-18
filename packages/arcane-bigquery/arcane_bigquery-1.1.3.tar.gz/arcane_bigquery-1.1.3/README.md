# Arcane bigquery

This package is based on [google-cloud-bigquery](https://pypi.org/project/google-cloud-bigquery/).

## Get Started

```sh
pip install arcane-bigquery
```

## Example Usage

```python
from arcane import bigquery
client = bigquery.Client()

dataset_ref = client.dataset('name')
dataset = bigquery.Dataset(dataset_ref)
dataset.location = 'US'
dataset = client.create_dataset(dataset)
```

Create clients with credentials:

```python
from arcane import bigquery

# Import your configs
from configure import Config

client = bigquery.Client.from_service_account_json(Config.KEY, project=Config.GCP_PROJECT)

```
