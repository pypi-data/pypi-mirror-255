# Dependencies
######################
import pyspark.sql.functions as F
from pyspark.sql.dataframe import DataFrame

from typing import List

def _clean_columnname(_columnname: str, _casetype: str = 'lower') -> str:
    """
    The function cleans a column name by removing special characters, followed by converting it to the specificed case type.
    All characters are removed so that the column name is compliant with the parquet file column naming conventions.
    Note: Splitting camel and pascale case wordse (lower -> upper) is currently not supported.

    Parameters
    ----------
    _columnname : str
        The column name that will be cleaned.
    _casetype : str, default 'lower'
        The case type to which the column name will be changed after removing the characters.
        Supported case types are camel (myColumnName), pascal (MyColumnName), snake (my_column_name), lower (mycolumnname), kebab (my-column-name) and upper (MY_COLUMN_NAME). 
        More information about the case types can be found here:
        https://www.curiouslychase.com/posts/most-common-programming-case-types
    
    Returns
    -------
    str
        The cleaned column name as a string.

    Raises
    ------
    NotImplementedError
        If an invalid value for _casetype value is passed in the function.

    Examples
    --------
        >>> import datacorecommon as dc
        >>> dc.dataframe._clean_columnname('my favorite-column', 'pascal')
        'MyFavoriteColumn'
        >>> dc.dataframe._clean_columnname('my favorite-column', 'upper')
        'My_Favorite_Column'

    """

    from string import capwords
    
    """Remove the characters ",;{}()\n\t=" from the column name"""
    _columnname = _columnname.replace(',', '')
    _columnname = _columnname.replace(';', '')
    _columnname = _columnname.replace('{', '')
    _columnname = _columnname.replace('}', '')
    _columnname = _columnname.replace('(', '')
    _columnname = _columnname.replace(')', '')
    _columnname = _columnname.replace('\n', '')
    _columnname = _columnname.replace('\t', '')
    _columnname = _columnname.replace('=', '')
    
    """Change to requested case type"""
    if _casetype == 'camel':
        _columnname = _columnname.replace('-', ' ')
        _columnname = _columnname.replace('_', ' ')
        _columnname = capwords(_columnname).replace(' ', '')
        _columnname = ''.join([_columnname[0].lower(), _columnname[1:]]) # Enforce the first character of the word to lowercase

    elif _casetype == 'pascal':
        _columnname = _columnname.replace('-', ' ')
        _columnname = _columnname.replace('_', ' ')
        _columnname = capwords(_columnname).replace(' ', '')
        
    elif _casetype == 'snake':
        _columnname = _columnname.replace(' ', '_')
        _columnname = _columnname.replace('-', '_')
        _columnname = _columnname.lower()

    elif _casetype == 'lower':
        _columnname = _columnname.replace(' ', '')
        _columnname = _columnname.replace('-', '_')
        _columnname = _columnname.lower()   
        
    elif _casetype == 'kebab':
        _columnname = _columnname.replace(' ', '-')
        _columnname = _columnname.replace('_', '-')
        _columnname = _columnname.lower()
    
    elif _casetype == 'upper':
        _columnname = _columnname.replace(' ', '_')
        _columnname = _columnname.replace('-', '_')
        _columnname = _columnname.upper()
      
    else:
      raise NotImplementedError(f'_casetype: {_casetype} not implemented')
    
    return _columnname


def clean_columnnames_dataframe(_df: DataFrame, _casetype: str = 'lower') -> DataFrame:
    """
    The function cleans all the column names of the input DataFrame by removing the special characters, followed by converting the column names to the specified case type.
    All characters are removed so that the column name is compliant with the parquet file column naming conventions.
    Note: Splitting camel and pascale case wordse (lower -> upper) is currently not supported.
    _clean_columnname function is used as a helper function.

    Parameters
    ----------
    _df : DataFrame
        PySpark Dataframe with the columns that need to be cleaned.
    _casetype : str, default 'lower'
        The case type to which all the dataframe's columns will be converted after removing the characters.
        Supported case types are camel (myColumnName), pascal (MyColumnName), snake (my_column_name), lower (mycolumnname), kebab (my-column-name) and upper (MY_COLUMN_NAME). 
        More information about the case types can be found here:
        https://www.curiouslychase.com/posts/most-common-programming-case-types
    
    Returns
    -------
    DataFrame
        The dataframe with all the columns renamed to the new clean names.

    Examples
    --------
        TBD

    """
    # Get all column names out once
    _df_cols = _df.columns
    
    _clean_cols = {old_c: _clean_columnname(old_c, _casetype) for old_c in _df_cols}

    # Use a single select statement to clean all the column names
    _df = _df.select([F.col(old_c).alias(clean_c) for old_c, clean_c in _clean_cols.items()])
    
    return _df