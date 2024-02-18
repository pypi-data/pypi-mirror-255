import pandas as pd
from pyarrow import parquet
from typing import Union, List, Tuple, Any
from fastapi.logger import logger

from app.core.config import settings


def file_iterator(
        filepath: str, 
        columns: List[str] = None, 
        filters: Union[List[Tuple], List[List[Tuple]]] = None,
) -> Any:
    """
    Iterator over the requested columns of a Parquet file
    Returns (in CSV format) a given number or rows at a time to limit memory consumption. 
    """
    for row in pd.read_parquet(
        path=filepath,
        engine="pyarrow",
        columns=columns,
        filters=filters,
    ).iterrows():
        # Returns a Tuple[index, Series]
        datarow = ",".join(str(i) for i in row[1].to_list())
        if row[0] == 0:
            # Write column headers only once
            header = ",".join(str(i) for i in row[1].keys().values.tolist())
            yield header + "\n" + datarow + "\n" 
        else:
            yield datarow + "\n" 


def file_iterator_aggregation(
        filepath: str, 
        columns: List[str] = None, 
        filters: Union[List[Tuple], List[List[Tuple]]] = None,
        identifier_columns: List[str] = None, 
        measure_columns: List[str] = None, 
) -> Any:
    """
    Iterator over the requested columns of a Parquet file, grouped by the identifier columns
    with the measure columns aggregated (summed). 
    Returns (in CSV format) one row at a time to limit memory consumption. 
    """
    agg_dict = {col: "sum" for col in measure_columns}

    data_headers = ",".join(ic for ic in identifier_columns) + "," + ",".join(ic for ic in measure_columns)
    date_headers = ",".join(dh[0] for dh in filters)
    out_headers = data_headers + "," + date_headers

    date_values = ",".join(str(dh[2]) for dh in filters)

    row_num = 0
    for row in pd.read_parquet(
        path=filepath,
        engine="pyarrow",
        columns=columns,
        filters=filters,
    ).groupby(by=identifier_columns, sort=False).agg(agg_dict).iterrows():
        row_num += 1
        # Returns a Tuple[index, Series]
        datarow = row[0] + "," + ",".join(str(i) for i in row[1].to_list())+ "," + date_values
        if row_num == 1:
            # Write column headers only once
            yield out_headers + "\n" + datarow + "\n" 
        else:
            yield datarow + "\n" 


def variable_data_iterator(
        variable_name: str,
        filters: Union[List[Tuple], List[List[Tuple]]] = None,
) -> Any:
    """
    Iterator over the data corresponding to a given Kudaf Variable,
    Returns (in CSV format) a given number or rows at a time to limit the server's memory consumption. 
    """
    columns = []
    if variable_name not in settings.VARIABLE_MAPPINGS:
        logger.error(f'No data found for variable: {variable_name}')
        return []

    var_map = settings.VARIABLE_MAPPINGS.get(variable_name)

    if "CALCULATED" not in var_map.get('measure_columns'):
        for type_col in ["identifier_columns", "measure_columns", "attribute_columns"]:
            columns += var_map.get(type_col) if var_map.get(type_col) is not None else []

        filepath = var_map.get('data_filepath')

        if var_map.get('temporality_type') == 'ACCUMULATED' and not \
            var_map.get('measure_columns_accumulated'):
            # ACCUMULATED temporality case, with file data not yet accumulated,
            # needs more complex processing to aggregate
            return file_iterator_aggregation(
                filepath=filepath, 
                columns=columns,
                filters=filters,
                identifier_columns=var_map.get('identifier_columns'),
                measure_columns=var_map.get('measure_columns'),
            )
        else:
            # EVENT or STATUS temporality, only time filtering needed
            return file_iterator(
                filepath=filepath, 
                columns=columns,
                filters=filters,
            )
    else:
        """
        PLACEHOLDER: INSERT HERE  the logic (or function call) necessary to
        perform whatever calculation is required 
        and return an iterator over the dataset
        """
        return []
    

def parquet_file_iterator(
        parquet_file: parquet.ParquetFile, 
        columns: List[str] = None, 
        batch_size: int = 65536
) -> Any:
    """
    Iterator over the requested columns of a Parquet file
    Returns (in CSV format) a given number or rows at a time to limit memory consumption. 
    """
    batch_num = 0
    for record_batch in parquet_file.iter_batches(
        columns=columns,
        batch_size=batch_size
    ):
        batch_num += 1
        if batch_num == 1:
            # Write column headers only once
            yield record_batch.to_pandas().to_csv(index=False, header=True)
        else:    
            yield record_batch.to_pandas().to_csv(index=False, header=False)    


def parquet_variable_data_iterator(
        variable_name: str,
        limit_rows: int = 65535,
) -> Any:
    """
    Iterator over the data corresponding to a given Kudaf Variable,
    Returns (in CSV format) a given number or rows at a time to limit the server's memory consumption. 
    """
    columns = []
    if variable_name not in settings.VARIABLE_MAPPINGS:
        logger.error(f'No data found for variable: {variable_name}')
        return []

    var_map = settings.VARIABLE_MAPPINGS.get(variable_name)

    if "CALCULATED" not in var_map.get('measure_columns'):
        for type_col in ["identifier_columns", "measure_columns", "attribute_columns"]:
            columns += var_map.get(type_col) if var_map.get(type_col) is not None else []

        filepath = var_map.get('data_filepath')
        
        return parquet_file_iterator(
            parquet_file=parquet.ParquetFile(source=filepath, memory_map=True), 
            columns=columns,
            batch_size=limit_rows,
        )
    else:
        """
        Insert here  the logic (or function call) necessary to
        perform whatever calculation is required 
        and return an iterator over the dataset
        """
        return ()
    