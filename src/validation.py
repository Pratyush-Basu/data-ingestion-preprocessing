import pandera.pandas as pa
from pandera import Column, Check
import pandas as pd
from pathlib import Path


def _map_dtype(dtype_str: str):
    """Map string dtype from spec to Pandera dtype."""
    mapping = {
        'int': pa.Int,
        'float': pa.Float,
        'string': pa.String,
        'bool': pa.Bool
    }
    return mapping.get(dtype_str, pa.String)


def build_schema_from_spec(spec: dict) -> pa.DataFrameSchema:
    """Build a Pandera schema dynamically from a spec dict."""
    cols = {}
    for col_name, col_spec in spec.items():
        dtype = _map_dtype(col_spec.get('dtype', 'string'))
        checks = []
        c = col_spec.get('checks', {}) or {}
        if 'isin' in c:
            checks.append(Check.isin(c['isin']))
        if 'min' in c:
            checks.append(Check.ge(c['min']))
        if 'max' in c:
            checks.append(Check.le(c['max']))
        nullable = col_spec.get('nullable', False)

        cols[col_name] = Column(dtype, checks=checks if checks else None, nullable=nullable)

    schema = pa.DataFrameSchema(cols)
    return schema

"""
def validate_df(df: pd.DataFrame, schema: pa.DataFrameSchema):
    "Validate DataFrame against schema. Returns (status, message)."
    try:
        validated = schema.validate(df)
        return True, "✅ All checks passed!"
    except Exception as e:
        return False, f"❌ Validation failed: {e}"
    
    """
    
def validate_df(df: pd.DataFrame, schema: pa.DataFrameSchema, report_path: str = None):
    """Validate DataFrame against schema. Always generates a TXT report."""
    report_lines = []
    try:
        # Validate with lazy=True to collect all errors
        validated = schema.validate(df, lazy=True)
        report_lines.append("✅ All checks passed!")
        status = True
    except pa.errors.SchemaErrors as err:
        status = False
        report_lines.append("❌ Validation failed!\n")
        failure_report = err.failure_cases
        for i, row in failure_report.iterrows():
            report_lines.append(f"Column: {row['column']}")
            report_lines.append(f"Check: {row['check']}")
            report_lines.append(f"Index: {row['index']}")
            report_lines.append(f"Failure Case: {row['failure_case']}")
            report_lines.append("-----------------")

    # Always write report
    if report_path:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:  # <- fix here
            f.write("Validation Report\n")
            f.write("=================\n\n")
            f.write("\n".join(report_lines))
    
    return status, f"Report generated at {report_path if report_path else 'N/A'}"
