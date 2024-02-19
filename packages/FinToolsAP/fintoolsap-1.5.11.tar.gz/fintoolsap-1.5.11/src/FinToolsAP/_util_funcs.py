from __future__ import annotations

import pandas as pd
import numpy as np
import datetime
import dateutil
import pathlib
import _config

def _rhasattr(obj, attr):
    try: 
        left, right = attr.split('.', 1)
    except: 
        return(hasattr(obj, attr))
    return(_rhasattr(getattr(obj, left), right))

def _rgetattr(obj, attr, default = None):
    try: 
        left, right = attr.split('.', 1)
    except: 
        return(getattr(obj, attr, default))
    return(_rgetattr(getattr(obj, left), right, default))

def _rsetattr(obj, attr, val):
    try: 
        left, right = attr.split('.', 1)
    except: 
        return(setattr(obj, attr, val))
    return(_rsetattr(getattr(obj, left), right, val))

def _check_file_path_type(path, path_arg: str) -> pathlib.Path:
    try:
        path = pathlib.Path(path)
        return(path)
    except:
        raise TypeError(_config.Messages.PATH_FORMAT.format(color = _config.bcolors.FAIL,
                                                            obj = path_arg))

def percentile_rank(df: pd.DataFrame, var: str) -> pd.DataFrame:
    ptiles = list(df[var].quantile(q = list(np.arange(start = 0, step = 0.01, stop = 1))))
    df[f'{var}_pr'] = 100
    for i in range(99, 0, -1):
        mask = df[var] < ptiles[i]
        df.loc[mask, f'{var}_pr'] = i
    return(df)

def prior_returns(df: pd.DataFrame, 
                  id_type: str, 
                  return_types: list[str], 
                  return_intervals: list[tuple[int, int]]
                  ) -> pd.DataFrame:
    """ Calculates the cummulative return between two backward looking time
    intervals
    """
    for ret_typ in return_types:
        for typ in return_intervals:
            name = f'pr{typ[0]}_{typ[1]}' if(ret_typ == 'adjret') else f'prx{typ[0]}_{typ[1]}'
            df[name] = 1
            dic = {}
            for i in range(typ[0], typ[1] + 1):
                dic[f'{ret_typ}_L{i}'] = 1 + df.groupby(by = [id_type])[ret_typ].shift(i)
                df[name] *= dic[f'{ret_typ}_L{i}']
            df = df.drop(df.filter(regex = '_L').columns, axis = 1)
            df[name] -= 1
    return(df)

def gorup_avg(df: pd.DataFrame, gr: list, vr: str, wt: str = None, name: str = None):
    name = vr if(name is None) else name
    if(wt is None):
        res = df.groupby(by = gr).mean(numeric_only = True)[vr]
    else:
        res = df.groupby(by = gr).apply(wavg, vr, wt)
    res = res.to_frame().reset_index()
    if(0 in list(res.columns)):
        res = res.rename(columns = {0: name})
    else:
        res = res.rename(columns = {vr: name})
    return(res)

def winsorize(col: pd.Series, pct_lower: float = None, pct_upper: float = None) -> pd.Series:
    if(pct_lower is None and pct_upper is None):
        raise ValueError('pct_lower and pct_upper can not bth be None.')
    val_lower, val_upper = -np.inf, np.inf
    if(pct_lower is not None):
        val_lower = np.percentile(col, pct_lower)
    if(pct_upper is not None):
        val_upper = np.percentile(col, pct_upper)
    col = np.where(col < val_lower, val_lower, col)
    col = np.where(col > val_upper, val_upper, col)
    return(col)

def groupby_nunique(df, gr, var, name = None, no_merge = False):
    if(isinstance(gr, str)):
        gr = [gr]
    grp = df.groupby(by = gr)[var].nunique()
    grp = grp.reset_index(drop = False)
    new_name = f'cnt_{var}'
    if(name is not None):
        new_name = name
    grp = grp.rename(columns = {var: new_name})
    if(no_merge):
        return(grp)
    else:
        df = df.merge(grp, how = 'left', on = gr)
        return(df)

def date_intervals(min_date: datetime.datetime, 
                   max_date: datetime.datetime, 
                   overlap: bool = False, 
                   **kwargs
                   ) -> list[tuple[datetime.datetime, datetime.datetime]]:    
    blocks = []
    start_date = min_date
    while(True):
        end_date = start_date + dateutil.relativedelta.relativedelta(**kwargs)
        if(end_date >= max_date):
            end_date = max_date
            blocks.append((start_date, end_date))
            break 
        
        end_date_adj = end_date
        if(not overlap):
            end_date_adj -= dateutil.relativedelta.relativedelta(days = 1)
        blocks.append((start_date, end_date_adj))
        start_date = end_date
    return(blocks)

def convert_to_list(val: list|str|float|int):
    if(isinstance(val, list)):
        return(val)
    else:
        return([val])

def list_diff(list1: list, list2: list) -> list:
    res = [e for e in list1 if e not in list2]
    return(res)

def list_inter(list1: list, list2: list) -> list:
    res = [e for e in list1 if e in list2]
    return(res)

def msci_quality(Z: float) -> float:
    if(Z >= 0):
        return(1 + Z)
    else:
        return(1 / (1 - Z))
        
# Weighted average
# can be used with groupby:  df.groupby('col1').apply(wavg, 'avg_name', 'weight_name')
# ML: corrected by ML to allow for missing values
def wavg(group, avg_name, weight_name=None):
    if weight_name==None:
        return group[avg_name].mean()
    else:
        x = group[[avg_name,weight_name]].dropna()
        try:
            return (x[avg_name] * x[weight_name]).sum() / x[weight_name].sum()
        except ZeroDivisionError:
            return group[avg_name].mean()
        