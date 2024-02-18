import datetime
import os
import sys

import numpy as np
import pytest
from sdypy_sep005.sep005 import assert_sep005

import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sep005_io_parquet.parquet import read_parquet, ParquetFileReader

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, 'static')
GOOD_FILES = os.listdir(os.path.join(static_dir, 'good'))


@pytest.mark.parametrize("filename", GOOD_FILES)
def test_compliance_sep005(filename):
    """
    Test the compliance with the SEP005 guidelines
    """
    file_path = os.path.join(static_dir, 'good', filename)
    signals = read_parquet(file_path)  # should already not crash here

    assert len(signals) != 0  # Not an empty response
    assert_sep005(signals)

@pytest.mark.parametrize("filename", GOOD_FILES)
def test_qa(filename):
    """
    Test the Quality assurance functions
    """
    file_path = os.path.join(static_dir, 'good', filename)

    # good pf should pass all quality assurance
    pf = ParquetFileReader(file_path, qa=True)

    # Inserting a NaN should trip nan_samples
    pf.df.iloc[10, 0] = np.nan

    pf.missing_samples # Should still be fine
    with pytest.raises(ValueError):
        pf.nan_samples

    # Removing a row should trip missing_samples
    pf.df = pf.df.drop(index=pf.df.iloc[10].name)

    pf.nan_samples  # Should still be fine
    with pytest.raises(ValueError):
        pf.missing_samples

@pytest.mark.parametrize("filename", GOOD_FILES)
def test_df_update(filename):
    """
    Test the behaviour when a DataFrame is updated, other properties also
    need to be updated accordingly

    """
    file_path = os.path.join(static_dir, 'good', filename)

    # good pf should pass all quality assurance
    pf = ParquetFileReader(file_path, qa=True)

    dur_0 = pf.duration
    dt_s = pf.start_timestamp
    pf.df = pf.df.drop(pf.df.index[:100]) # Drop the first 100 samples

    assert pf.start_timestamp == dt_s+datetime.timedelta(seconds=(1/pf.fs*100))
    assert pf.duration == dur_0 - 1/pf.fs*100
    assert len(pf.time) == len(pf.df)

@pytest.mark.parametrize("filename", GOOD_FILES)
def test_resolve_missing_samples(filename):
    file_path = os.path.join(static_dir, 'good', filename)
    # good pf should pass all quality assurance
    pf = ParquetFileReader(file_path, qa=True)
    no_samples = len(pf.df)

    dt_del = pf.df.iloc[10].name
    pf.df = pf.df.drop(index=dt_del)
    with pytest.raises(ValueError):
        pf.missing_samples

    assert len(pf.df) == no_samples-1
    assert dt_del not in pf.df.index

    #%% Fix the missing sample
    pf.resolve_missing_samples(inplace=True)
    # Both QA's should pass now
    pf.missing_samples
    pf.nan_samples

    assert len(pf.df) == no_samples
    assert dt_del in pf.df.index
    assert pf.df.index.is_monotonic_increasing
    for i in range(len(pf.channels)):
        # All channels are interpolated
        assert pf.df.iloc[10,i] == pytest.approx((pf.df.iloc[11,i]+pf.df.iloc[9,i])/2) # Linear interpolation


    #%% Check if the limit on the number of samples to resolve is respected
    pf.df = pf.df.drop(pf.df.index[90:100])  # Drop 10 samples
    pf.resolve_missing_samples(inplace=True)
    pf.missing_samples
    pf.nan_samples
    assert len(pf.df) == no_samples

    pf.df = pf.df.drop(pf.df.index[90:100])  # Drop 10 samples
    pf.resolve_missing_samples(inplace=True, limit=5)
    pf.missing_samples # No missing samples, just NaN
    with pytest.raises(ValueError):
        pf.nan_samples