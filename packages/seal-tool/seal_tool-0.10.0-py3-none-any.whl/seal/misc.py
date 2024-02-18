#!/usr/bin/env python3

import argparse
import numpy as np
import pandas as pd


def add_date_col(args: argparse.Namespace) -> str | None:
    """Add ISO 8601-formatted date column to input based on its
    quadrat_id column.
    Intended for datasets with encounters.

    >>> from io import StringIO
    >>> df = pd.DataFrame({'quadrat_id': ['A_0_1/1/1970', 'A_0_2/1/1970']}).to_csv(index=False)
    >>> args = argparse.Namespace()
    >>> args.dataset, args.output = StringIO(df), None
    >>> pd.read_csv(StringIO(add_date_col(args)))
         quadrat_id        date
    0  A_0_1/1/1970  1970-01-01
    1  A_0_2/1/1970  1970-01-02
    """

    inp = args.dataset
    df = pd.read_csv(inp)
    dates = df['quadrat_id'].str.split('_').str[2]
    dates = pd.to_datetime(dates, format='%d/%m/%Y')
    df['date'] = dates
    return df.to_csv(args.output, index=False)


def check_quadrat_list(args: argparse.Namespace) -> None:
    """Check quadrat lists for possibly erroneous values"""

    qlist = args.quadrat_list
    cols = pd.read_csv(qlist, index_col=False, nrows=0).columns.tolist()
    if not ('quadrat_id' in cols and 'quadrat_type' in cols):
        print(f'Missing header in {qlist}')
        return
    df = pd.read_csv(qlist, index_col='quadrat_id')
    min_x, min_y = df['coord_x'].min(), df['coord_y'].min()
    if min_x != 0:
        print(f'Unusual minimal x coordinate: {min_x}')
    if min_y != 0:
        print(f'Unusual minimal y coordinate: {min_y}')
    max_x, max_y = df['coord_x'].max(), df['coord_y'].max()
    quadrats_total = (max_x + 1) * (max_y + 1)
    if len(df) != quadrats_total:
        print(f'Unusual number of quadrats, {len(df)} != {quadrats_total}, ({max_x + 1} * {max_y + 1})')
    df.set_flags(allows_duplicate_labels=False)
    if df.columns[0] == 'Unnamed: 0':
        print('Possibly redundant column')
        df = df.drop(columns='Unnamed: 0')
    if df.isnull().values.any():
        print('Missing value(s)')
    dates = df.index.str.split('_').str[2]
    startdate = pd.to_datetime(dates, format='%d/%m/%Y').min()
    startdate = startdate.isoformat().replace('-', '')[0:8]
    if not args.output:
        qlist = qlist.parent / f'{qlist.stem}-{startdate}.csv'
        qlist = str(qlist).lower().replace(' ', '-').replace("'", '')  # type: ignore[assignment]
    else:
        qlist = args.output
    qlist.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(qlist)


def add_coord_cols(args: argparse.Namespace) -> None | str:
    """Add coord_x and coord_y to quadrat list based on its quadrat_ids

    >>> from io import StringIO
    >>> df = pd.DataFrame({'quadrat_id': ['A_1_date_2', 'A_10_date_11']}).to_csv(index=False)
    >>> args = argparse.Namespace()
    >>> args.input, args.output = StringIO(df), None
    >>> pd.read_csv(StringIO(add_coord_cols(args)))
         quadrat_id  coord_x  coord_y
    0    A_1_date_2        0        1
    1  A_10_date_11        9       10
    """

    qlist = pd.read_csv(args.input, index_col='quadrat_id')
    qlist.set_flags(allows_duplicate_labels=False)
    xs = pd.to_numeric(qlist.index.str.split('_').str[1]) - 1  # type: ignore[call-overload]
    ys = pd.to_numeric(qlist.index.str.split('_').str[-1]) - 1  # type: ignore[call-overload]
    qlist['coord_x'] = xs
    qlist['coord_y'] = ys
    return qlist.to_csv(args.output)


def join_analyses(args: argparse.Namespace) -> None | str:
    """Concatenate analysis results for joint plotting

    >>> from io import StringIO
    >>> df0 = pd.DataFrame({'result1': ['0', '1'], 'result2': ['2', '3']}).to_csv(index=False)
    >>> df1 = pd.DataFrame({'result1': ['4', '5'], 'result2': ['6', '7']}).to_csv(index=False)
    >>> inputs = [StringIO(df0), StringIO(df1)]
    >>> args = argparse.Namespace()
    >>> args.inputs, args.output, args.discriminants = inputs, None, None
    >>> pd.read_csv(StringIO(join_analyses(args)))
       result1  result2  discriminant
    0        0        2             0
    1        1        3             0
    2        4        6             1
    3        5        7             1
    """

    df_list = []
    args.discriminants = args.discriminants if args.discriminants else range(len(args.inputs))
    for df_path, discr in zip(args.inputs, args.discriminants):
        df = pd.read_csv(df_path)
        df['discriminant'] = discr
        df_list.append(df)
    joined = pd.concat(df_list)
    return joined.to_csv(args.output, index=False)


def convert_biolib(args: argparse.Namespace) -> None:
    """Convert dataset from https://www.biolib.cz/cz/speciesmapping/id1/ for
    preprocess and analysis.

    Expected columns: CREATED, DAY, LATIN, MONTH, SUBSQ, SQUARE, QUANTITY, YEAR
    """

    biolib_dtypes = {'SQUARE': str, 'SUBSQ': pd.CategoricalDtype(categories=['a', 'b', 'c', 'd'])}
    biolib = (
        pd.read_csv(args.input, dtype=biolib_dtypes, parse_dates=['CREATED'], date_format='%d/%m/%Y')
        .rename(columns=str.lower)
        .convert_dtypes()
    )
    assert not biolib.subsq.isna().any()
    biolib = biolib.rename(columns={'latin': 'species', 'quantity': 'individuals'}, errors='raise')

    biolib['individuals'] = pd.to_numeric(biolib['individuals'], errors='coerce').fillna(1)

    # workaround because some sighting dates are invalid (day 0 or month 0)
    biolib['month'] = np.where(biolib.month == 0, biolib.created.dt.month, biolib.month)
    biolib['day'] = np.where(biolib.day == 0, biolib.created.dt.day, biolib.day)
    dateframe = biolib[['year', 'month', 'day']]
    biolib['date'] = pd.to_datetime(dateframe)

    coord_x = biolib['square'].str[2:]
    biolib['coord_x'] = coord_x.astype('int64')
    min_x = biolib['coord_x'].min()
    biolib['coord_x'] = biolib['coord_x'] - min_x

    coord_y = biolib['square'].str[:2]
    biolib['coord_y'] = coord_y.astype('int64')
    min_y = biolib['coord_y'].min()
    biolib['coord_y'] = biolib['coord_y'] - min_y

    # adjust for subsquares to enable nested quadrats strategy
    biolib['coord_x'] *= 2
    is_right_x = (biolib.subsq == 'b') | (biolib.subsq == 'd')
    biolib['coord_x'] = biolib['coord_x'].where(is_right_x, biolib.coord_x + 1)

    biolib['coord_y'] *= 2
    is_top_y = (biolib.subsq == 'a') | (biolib.subsq == 'b')
    biolib['coord_y'] = biolib['coord_y'].where(is_top_y, biolib.coord_y + 1)

    biolib = biolib.sort_values(by=['coord_x', 'coord_y'])
    biolib['quadrat_id'] = 'A_' + biolib.coord_x.astype(str) + '_A_' + biolib.coord_y.astype(str)
    biolib['family'] = 'DUMMY'
    biolib['phase'] = 'term'
    biolib['direction'] = 'f'
    biolib['significant_size'] = True
    biolib['locality'] = 'CZ'

    qlist = biolib[['quadrat_id', 'coord_x', 'coord_y']].drop_duplicates()
    qlist = qlist.sort_values(by=['coord_x', 'coord_y'])
    qlist['quadrat_type'] = 'normal'

    qlist.to_csv(args.output.with_stem(f'{args.output.stem}-qlist'), index=False)
    biolib.to_csv(args.output, index=False)


def convert_aopk(args: argparse.Namespace) -> None:
    """Convert dataset from https://portal.nature.cz/nd/ for
    preprocess and analysis.

    Expected columns: DRUH, CESKE_JMENO, DATI_INSERT, SITMAP, POCET

    Input is expected to use CP1250 encoding. This is the default
    after downloading from the source.
    """

    aopk_dtypes = {'SITMAP': str}
    try:
        aopk = pd.read_csv(
            args.input,
            dtype=aopk_dtypes,
            parse_dates=['DATI_INSERT'],
            date_format='%Y%m%d',
            encoding='cp1250',
            delimiter=';',
        )
    except UnicodeDecodeError:
        print('WARN: Unusual encoding for AOPK data, CP1250 expected. Trying UTF-8.')
        aopk = pd.read_csv(
            args.input, dtype=aopk_dtypes, parse_dates=['DATI_INSERT'], date_format='%Y%m%d', delimiter=';'
        )
    aopk = aopk.rename(columns=str.lower).convert_dtypes()
    aopk = aopk.rename(
        columns={
            'dati_insert': 'date',
            'druh': 'species',
            'pocet': 'individuals',
        },
        errors='raise',
    )

    aopk['individuals'] = pd.to_numeric(aopk['individuals'], errors='coerce').fillna(1)

    coord_x = aopk['sitmap'].str[2:]
    aopk['coord_x'] = coord_x.astype('int64')
    min_x = aopk['coord_x'].min()
    aopk['coord_x'] = aopk['coord_x'] - min_x

    coord_y = aopk['sitmap'].str[:2]
    aopk['coord_y'] = coord_y.astype('int64')
    min_y = aopk['coord_y'].min()
    aopk['coord_y'] = aopk['coord_y'] - min_y

    aopk['quadrat_id'] = 'A_' + aopk.coord_x.astype(str) + '_A_' + aopk.coord_y.astype(str)
    aopk['family'] = 'DUMMY'
    aopk['phase'] = 'term'
    aopk['direction'] = 'f'
    aopk['significant_size'] = True
    aopk['locality'] = 'CZ'

    qlist = aopk[['quadrat_id', 'coord_x', 'coord_y']].drop_duplicates()
    qlist['quadrat_type'] = 'normal'

    qlist.to_csv(args.output.with_stem(f'{args.output.stem}-qlist'), index=False, encoding='utf8')
    aopk.to_csv(args.output, index=False, encoding='utf8')
