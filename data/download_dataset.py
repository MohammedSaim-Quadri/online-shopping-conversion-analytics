"""Run from project root: python data/download_dataset.py. Writes genuine UCI CSV."""
import pathlib
import urllib.request
URL = 'https://archive.ics.uci.edu/ml/machine-learning-databases/00468/online_shoppers_intention.csv'
TARGET = pathlib.Path(__file__).with_name('online_shoppers_intention.csv')
if __name__ == '__main__':
    urllib.request.urlretrieve(URL, TARGET)
    import pandas as pd
    df = pd.read_csv(TARGET)
    assert df.shape == (12330, 18), f'Unexpected source file: {df.shape}'
    print(
        f'Official UCI CSV saved to {TARGET}, {len(df):,} sessions, {len(df.columns)} attributes')
