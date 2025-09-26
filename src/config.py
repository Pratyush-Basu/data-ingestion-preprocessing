import yaml
from pathlib import Path


DEFAULT_PARAMS_PATH = Path("params.yaml")




def load_params(path: str | Path = DEFAULT_PARAMS_PATH):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_dataset_config(dataset_name: str, params_path: str | Path = DEFAULT_PARAMS_PATH):
    params = load_params(params_path)
    cfg = params.get("dataset", {}).get(dataset_name)
    if cfg is None:
        raise KeyError(f"Dataset '{dataset_name}' not found in {params_path}")
    return cfg