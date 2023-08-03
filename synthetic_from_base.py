import json
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer
import pandas as pd
from sdv.single_table import CTGANSynthesizer

def json_data_to_pandas_df(filepath):
    json_file_path = filepath
    with open(json_file_path, 'r') as json_file:
        user_actions = json.load(json_file)
    df = pd.DataFrame(user_actions)

    return df

df = json_data_to_pandas_df("data.json")

metadata = SingleTableMetadata()
metadata.detect_from_dataframe(data=df)
metadata.update_column(column_name="timestamp", sdtype="datetime", datetime_format="%Y-%m-%dT%H:%M:%S")
print(metadata)
metadata.validate()

synthesizer = GaussianCopulaSynthesizer(metadata)
synthesizer.fit(df)
synthetic_data = synthesizer.sample(num_rows=100)

print(synthetic_data)