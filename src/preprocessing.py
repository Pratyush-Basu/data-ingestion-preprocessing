import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, MinMaxScaler
from sklearn.compose import ColumnTransformer
import joblib


class Preprocessor:
    def __init__(self, numeric_columns=None, categorical_columns=None,
                num_impute_strategy='median', cat_impute_strategy='most_frequent',
                scaler='standard', encoding='onehot', drop_first=True):
        self.numeric_columns = numeric_columns or []
        self.categorical_columns = categorical_columns or []
        self.num_impute_strategy = num_impute_strategy
        self.cat_impute_strategy = cat_impute_strategy
        self.scaler = scaler
        self.encoding = encoding
        self.drop_first = drop_first
        self._ct = None   # ColumnTransformer

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Numeric pipeline
        num_steps = [('imputer', SimpleImputer(strategy=self.num_impute_strategy))]
        if self.scaler == 'standard':
            num_steps.append(('scaler', StandardScaler()))
        elif self.scaler == 'minmax':
            num_steps.append(('scaler', MinMaxScaler()))
        num_pipeline = Pipeline(num_steps)

        # Categorical pipeline
        cat_steps = [('imputer', SimpleImputer(strategy=self.cat_impute_strategy, fill_value=None))]
        if self.encoding == 'onehot':
            ohe = OneHotEncoder(
                sparse_output=False,
                handle_unknown='ignore',
                drop='first' if self.drop_first else None
            )
            cat_steps.append(('onehot', ohe))
        cat_pipeline = Pipeline(cat_steps)

        # ColumnTransformer
        transformers = []
        if self.numeric_columns:
            transformers.append(('num', num_pipeline, self.numeric_columns))
        if self.categorical_columns:
            transformers.append(('cat', cat_pipeline, self.categorical_columns))

        self._ct = ColumnTransformer(transformers, remainder='passthrough')
        X = self._ct.fit_transform(df)

        # Get feature names
        new_cols = []
        if self.numeric_columns:
            new_cols.extend(self.numeric_columns)

        if self.categorical_columns:
            ohe = self._ct.named_transformers_['cat'].named_steps.get('onehot')
            if ohe is not None:
                ohe_cols = list(ohe.get_feature_names_out(self.categorical_columns))
                new_cols.extend(ohe_cols)

        # Add passthrough columns (columns not in num/cat lists)
        passthrough_cols = [
            col for col in df.columns
            if col not in self.numeric_columns + self.categorical_columns
        ]
        new_cols.extend(passthrough_cols)

        return pd.DataFrame(X, columns=new_cols)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Use fitted transformer on new data"""
        if self._ct is None:
            raise ValueError("You must fit or load the transformer before calling transform.")
        X = self._ct.transform(df)

        # Keep same feature names as before
        new_cols = self.get_feature_names()
        return pd.DataFrame(X, columns=new_cols)

    def get_feature_names(self):
        """Return feature names after preprocessing"""
        new_cols = []
        if self.numeric_columns:
            new_cols.extend(self.numeric_columns)

        if self.categorical_columns:
            ohe = self._ct.named_transformers_['cat'].named_steps.get('onehot')
            if ohe is not None:
                ohe_cols = list(ohe.get_feature_names_out(self.categorical_columns))
                new_cols.extend(ohe_cols)

        passthrough_cols = [
            col for col in self._ct.feature_names_in_
            if col not in self.numeric_columns + self.categorical_columns
        ]
        new_cols.extend(passthrough_cols)
        return new_cols

    def save(self, path: str):
        joblib.dump(self._ct, path)

    def load(self, path: str):
        self._ct = joblib.load(path)
        return self._ct
