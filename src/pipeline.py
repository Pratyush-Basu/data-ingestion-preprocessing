import pandas as pd
from pathlib import Path
import yaml

from ingestion import load_csv, save_csv
from preprocessing import Preprocessor
from validation import build_schema_from_spec, validate_df


def load_config(path="params.yaml"):
    """Load YAML configuration file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def cast_columns(df: pd.DataFrame, schema_cfg: dict) -> pd.DataFrame:
    """Cast dataframe columns according to schema dtypes."""
    for col_name, col_spec in schema_cfg.items():
        if col_name in df.columns:
            dtype = col_spec["dtype"]
            try:
                if dtype == "int":
                    df[col_name] = df[col_name].astype(pd.Int64Dtype())
                elif dtype == "float":
                    df[col_name] = df[col_name].astype(float)
                elif dtype == "string" or dtype == "object":
                    df[col_name] = df[col_name].astype(str)
            except Exception as e:
                print(f"Warning: Could not cast column {col_name} to {dtype}: {e}")
    return df


def run_pipeline():
    cfg = load_config()

    # === Paths ===
    dataset_cfg = cfg["dataset"]["titanic"]  # Can generalize for other datasets
    raw_path = Path(dataset_cfg["raw_path"])
    interim_path = Path(dataset_cfg["interim_path"])
    processed_path = Path(dataset_cfg["processed_path"])
    validated_path = Path(dataset_cfg["validated_path"])

    # === 1. Ingestion ===
    df_raw = load_csv(raw_path)
    save_csv(df_raw, interim_path)

    # === 2. Preprocessing ===
    prep_cfg = cfg["preprocessing"]
    preprocessor = Preprocessor(
        numeric_columns=prep_cfg.get("numeric_columns", []),
        categorical_columns=prep_cfg.get("categorical_columns", []),
        num_impute_strategy=prep_cfg.get("num_impute_strategy", "median"),
        cat_impute_strategy=prep_cfg.get("cat_impute_strategy", "most_frequent"),
        scaler=prep_cfg.get("scaler", "standard"),
        encoding=prep_cfg.get("encoding", "onehot"),
        drop_first=prep_cfg.get("drop_first", True),
    )
    df_processed = preprocessor.fit_transform(df_raw)

    # === 2a. Cast columns according to schema ===
    schema_cfg = cfg["schema"]
    df_processed = cast_columns(df_processed, schema_cfg)

    save_csv(df_processed, processed_path)

    # === 3. Validation ===
    schema = build_schema_from_spec(schema_cfg)
    report_path = Path("data/validated/titanic_validation_report.txt")
    valid, msg = validate_df(df_processed, schema, report_path=report_path)

    if not valid:
        print("❌ Validation failed!")
        print(msg)
        return
    else:
        print("✅ Validation passed!")
        save_csv(df_processed, validated_path)


if __name__ == "__main__":
    run_pipeline()
