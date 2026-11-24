import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd
import pytest
from data_utils import normalize,filter_data,summary,fork_data

ROOT=pathlib.Path(__file__).resolve().parents[1]
def demo():return normalize(pd.read_csv(ROOT/'data'/'online_shoppers_intention.csv'))

def test_schema():
    d=demo(); assert len(d.columns)==18 and d['Revenue'].isin([0,1]).all()

def test_summary():
    d=demo(); s=summary(d); assert s['sessions']==len(d) and s['purchases']==int(d.Revenue.sum())

def test_fork_aggregation():
    d=demo(); xs=fork_data(d); assert sum(x['sessions'] for x in xs)==len(d)
    assert sum(x['purchases'] for x in xs)==int(d.Revenue.sum())
    assert all(abs(x['rate']-x['purchases']/x['sessions'])<1e-10 for x in xs)

def test_filter():
    d=demo(); f=filter_data(d,visitors=['New_Visitor'],weekends='weekend')
    assert (f['VisitorType']=='New_Visitor').all() and (f['Weekend']==1).all()

def test_missing_columns():
    with pytest.raises(ValueError,match='Missing required'):normalize(pd.DataFrame({'Revenue':[True]}))


def test_authentic_uci_statistics():
    d=demo()
    assert d.shape==(12330,18)
    assert d['Revenue'].sum()==1908
    assert int((d['Revenue']==0).sum())==10422
    assert len(d['Month'].unique())==10
    assert len(d['TrafficType'].unique())==20
    assert d.isna().sum().sum()==0

def test_authentic_uci_conversion_reconciliation():
    d=demo()
    expected=1908/12330
    assert abs(summary(d)['conversion']-expected)<1e-12
    assert sum(x['sessions'] for x in fork_data(d))==12330
    assert sum(x['purchases'] for x in fork_data(d))==1908

def test_low_sample_zero_rate_is_genuine():
    d=demo()
    observed=fork_data(d)
    lookup={(x['traffic'],x['visitor']):x for x in observed}
    assert lookup[('8','Other')]['sessions']==1
    assert lookup[('8','Other')]['purchases']==0
    assert lookup[('15','Returning_Visitor')]['sessions']==36
    assert lookup[('15','Returning_Visitor')]['purchases']==0
    assert lookup[('20','New_Visitor')]['sessions']==17
    assert lookup[('20','New_Visitor')]['purchases']==7

def test_monthly_reindex_keeps_gaps_after_filtering():
    d=demo()
    f=filter_data(d,months=['Sep','Nov'])
    monthly=f.groupby('Month')['Revenue'].mean().reindex(['Sep','Oct','Nov'])
    assert pd.isna(monthly['Oct'])
    assert pd.notna(monthly['Sep']) and pd.notna(monthly['Nov'])
