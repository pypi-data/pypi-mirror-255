SEP005 parquet io
-----------------------

Basic package to import data collected from FBGS data compliant with
SDyPy format for timeseries as proposed in SEP005.

Using the package
------------------

    .. code-block:: python

        from sep005_io_parquet import read_parquet

        file_path = # Path to the parquet file of interest
        signals = read_parquet(file_path)

Acknowledgements
----------------
