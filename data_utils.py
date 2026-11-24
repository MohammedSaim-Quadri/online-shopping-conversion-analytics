"""Validation, filtering and data summaries. Nothing in the charts is hard-coded to UCI rows."""
from __future__ import annotations
import base64
import io
import numpy as np
import pandas as pd

REQUIRED = ['Administrative', 'Administrative_Duration', 'Informational', 'Informational_Duration',
            'ProductRelated', 'ProductRelated_Duration', 'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay',
            'Month', 'OperatingSystems', 'Browser', 'Region', 'TrafficType', 'VisitorType', 'Weekend', 'Revenue']
NUMERIC = ['Administrative', 'Administrative_Duration', 'Informational', 'Informational_Duration',
           'ProductRelated', 'ProductRelated_Duration', 'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay']
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
LABELS = {'Returning_Visitor': 'Returning',
          'New_Visitor': 'New', 'Other': 'Other'}
MAX_UPLOAD = 12 * 1024 * 1024


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip().str.removeprefix('\ufeff')
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError('Missing required UCI columns: ' + ', '.join(missing))
    if len(df) < 1:
        raise ValueError('CSV contains no data rows.')
    for col in NUMERIC + ['OperatingSystems', 'Browser', 'Region', 'TrafficType']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    for col in ['Weekend', 'Revenue']:
        s = df[col].astype('string').str.strip().str.lower()
        if not s.isin(['true', 'false', '1', '0']).all():
            raise ValueError(f'{col} must contain true/false or 1/0 values.')
        df[col] = s.isin(['true', '1']).astype(int)
    df['Month'] = df['Month'].astype(
        'string').str.strip().replace({'Jun': 'June'})
    df['VisitorType'] = df['VisitorType'].astype('string').str.strip()
    if not df['Month'].isin(MONTHS).all():
        raise ValueError('Month has unrecognized values.')
    if (df['VisitorType'].isna() | (df['VisitorType'] == '')).any():
        raise ValueError('VisitorType contains blanks.')
    if df[NUMERIC + ['OperatingSystems', 'Browser', 'Region', 'TrafficType']].isna().any().any():
        raise ValueError(
            'Numeric fields contain missing or invalid values; clean the file before upload.')
    if (df['ProductRelated_Duration'] < 0).any() or not df['ExitRates'].between(0, 1).all():
        raise ValueError(
            'Product-related duration must be nonnegative; exit rate must be 0–1.')
    if not df['TrafficType'].ge(0).all():
        raise ValueError('TrafficType must be nonnegative.')
    df['TrafficType'] = df['TrafficType'].astype(int).astype(str)
    return df[REQUIRED].copy()


def parse_upload(content: str) -> pd.DataFrame:
    if not content or ',' not in content:
        raise ValueError('No uploaded CSV data.')
    encoded = content.split(',', 1)[1]
    data = base64.b64decode(encoded, validate=True)
    if len(data) > MAX_UPLOAD:
        raise ValueError('CSV exceeds 12 MB upload limit.')
    return normalize(pd.read_csv(io.BytesIO(data)))


def filter_data(df, visitors=None, months=None, weekends='all', traffic=None):
    out = df
    if visitors:
        out = out[out['VisitorType'].isin(visitors)]
    if months:
        out = out[out['Month'].isin(months)]
    if weekends in ('weekend', 'weekday'):
        out = out[out['Weekend'] == int(weekends == 'weekend')]
    if traffic is not None:
        out = out[out['TrafficType'] == str(traffic)]
    return out


def summary(df):
    return {'sessions': int(len(df)), 'purchases': int(df['Revenue'].sum()),
            'conversion': float(df['Revenue'].mean()) if len(df) else 0}


def fork_data(df, scale_max=None):
    if df.empty:
        return []
    stats = df.groupby(['TrafficType', 'VisitorType'], observed=True)[
        'Revenue'].agg(['count', 'sum']).reset_index()
    stats = stats.rename(columns={'count': 'sessions', 'sum': 'purchases'})
    stats['rate'] = stats['purchases']/stats['sessions']
    stats['TrafficType'] = stats['TrafficType'].astype(int)
    stats = stats.sort_values(['TrafficType', 'VisitorType'])

    return [
        {
            'traffic': str(r.TrafficType),
            'visitor': str(r.VisitorType),
            'sessions': int(r.sessions),
            'purchases': int(r.purchases),
            'nonPurchases': int(r.sessions - r.purchases),
            'rate': float(r.rate),
            'scaleMax': int(scale_max) if scale_max is not None else int(stats['sessions'].max())
        }
        for r in stats.itertuples()
    ]
