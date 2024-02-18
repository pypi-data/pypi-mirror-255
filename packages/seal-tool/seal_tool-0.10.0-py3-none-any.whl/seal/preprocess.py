#!/usr/bin/env python3

import argparse
import pandas as pd

from seal.common import enc_dtypes


def main(args: argparse.Namespace) -> int:
    enc = pd.read_csv(args.dataset, dtype=enc_dtypes(), parse_dates=['date']).rename(columns=str.lower).convert_dtypes()
    pd.set_option('display.max_seq_items', None)

    if 'refs' in args.checks:
        diff = check_ref(enc)
        if not diff.empty:
            print(f'WARN: The following values of "ref" column are out of place:\n{diff}.\n')

    if 'nas' in args.checks:
        na_indices, checked_cols = check_nas(enc)
        if not na_indices.empty:
            nas = enc.loc[na_indices, checked_cols]
            print('WARN: The folowing rows are missing important values:')
            for idx, row in nas.iterrows():
                nas_columns = ', '.join(row[row.isna()].index.to_list())
                print(f'Row {idx} NA columns: {nas_columns}')
            if args.drop_nas:
                enc = enc[~enc.index.isin(na_indices)]
            elif args.drop_nas is None:
                drop = input('[D]rop/[I]gnore?\n').lower()
                if 'drop'.startswith(drop):
                    enc = enc[~enc.index.isin(na_indices)]
            print('\n')

    if 'strs' in args.checks:
        cleaned = check_clean_strs(enc)
        bad_only = cleaned.dropna(how='all')
        if not bad_only.empty:
            print('WARN: The following strings were cleaned:')
            for idx, row in bad_only.iterrows():
                fixed_columns = ', '.join(row[~row.isna()].index.to_list())
                print(f'Fixed string(s) in row {idx}, columns: {fixed_columns}')
            print('\n')

            for name in enc.columns:
                if name not in cleaned.columns:
                    cleaned[name] = pd.Series([pd.NA] * enc.shape[0])
            cleaned = cleaned[enc.columns]
            enc = enc.where(cleaned.isna() | (enc.equals(cleaned)), cleaned)

    if 'coords' in args.checks:
        x_diff, y_diff = check_coords(enc)
        if not x_diff.empty:
            print(f'WARN: Following x coordinates do not match corresponding quadrat ID:\n{x_diff}\n')
        if not y_diff.empty:
            print(f'WARN: Following y coordinates do not match corresponding quadrat ID:\n{y_diff}\n')

    if 'species-name' in args.checks:
        diff = check_species_name(enc)
        if not diff.empty:
            print(f'WARN: The following species or name occurs in more than one pairing:\n{diff}\n')

    if 'species-phase-morph' in args.checks:
        diff = check_species_phase_morph(enc)
        if not diff.empty:
            bad = enc.loc[diff, ['species', 'phase', 'name', 'morph']]
            bad_groups = bad.groupby(['species', 'phase'], observed=True)
            print(f'WARN: The following ((species, phase), morph) pairs occur in multiple combinations:\n{diff}')
            for k, v in bad_groups:
                print(f'\n{k} paired-up simultaneously with\n{v.T}')
            print('\n')

    if 'morph-species' in args.checks:
        diff = check_morph_species(enc)
        if not diff.empty:
            print(f'WARN: The following morphs do not match expected species:\n{diff}\n')

    if 'family' in args.checks:
        diff = check_family(enc)
        if not diff.empty:
            print('WARN: The following families have unexpected phases:')
            enc.loc[diff, 'phase'] = 'term'
            print(f'Converted "ad" these phases to "term"\n{diff}\n')

    if 'dups' in args.checks:
        sans_ref = enc.drop(columns='ref', errors='raise') if 'ref' in enc.columns else enc
        dups = enc[sans_ref.duplicated(keep=False)]
        if not dups.empty:
            print(f'WARN: The folowing rows may be duplicates:\n{dups.index.tolist()}\n')

    if enc.empty:
        print('Result is empty. No data will be written.')
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    enc.to_csv(args.output, index=False)
    print(f'Done. {enc.shape[0]} rows written to {args.output}.')
    return 0


def check_nas(enc: pd.DataFrame) -> tuple[pd.Index, list[str]]:
    """Return indices in *enc* where important values are NA.

    Note that "important value" does not mean it is necessarily used in analysis
    just that they should not be missing by consensus.

    >>> enc = pd.DataFrame(
    ...     {
    ...         'locality': [0, pd.NA, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    ...         'transect': [0, 1, pd.NA, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    ...         'coord_x': [0, 1, pd.NA, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    ...         'coord_y': [0, 1, 2, pd.NA, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    ...         't': [0, 1, 2, 3, pd.NA, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    ...         'species': [0, 1, 2, 3, 4, pd.NA, 6, 7, 8, 9, 10, 11, 12, 13],
    ...         'name': [0, 1, 2, 3, 4, 5, pd.NA, 7, 8, 9, 10, 11, 12, 13],
    ...         'morph': [0, 1, 2, 3, 4, 5, 6, pd.NA, 8, 9, 10, 11, 12, 13],
    ...         'individuals': [0, 1, 2, 3, 4, 5, 6, 7, pd.NA, 9, 10, 11, 12, 13],
    ...         'significant_size': [0, 1, 2, 3, 4, 5, 6, 7, 8, pd.NA, 10, 11, 12, 13],
    ...         'family': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, pd.NA, 11, 12, 13],
    ...         'phase': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, pd.NA, 12, 13],
    ...         'quadrat': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, pd.NA, 13],
    ...         'quadrat_id': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, pd.NA],
    ...     }
    ... ).convert_dtypes()
    >>> res = check_nas(enc)
    >>> res[0]
    Index([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], dtype='int64')
    >>> res[1]
    ['significant_size', 'coord_x', 'coord_y', 'family', 'individuals', 'locality', 'morph', 'name', 'phase', 'quadrat', 'quadrat_id', 'species', 'transect', 't']
    """

    checked_cols = [
        'significant_size',
        'coord_x',
        'coord_y',
        'family',
        'individuals',
        'locality',
        'morph',
        'name',
        'phase',
        'quadrat',
        'quadrat_id',
        'species',
        'transect',
        't',
    ]
    found_cols = [col for col in checked_cols if col in enc.columns]

    col_has_nas = enc[found_cols].isna().any(axis='columns')
    return enc[col_has_nas].index, found_cols


def check_ref(enc: pd.DataFrame) -> pd.Index:
    """Return indices of *enc* where they differ from the expected 1-inf
    well behaved series

    >>> enc = pd.DataFrame({'ref': [1, 2, 3, 4, 5, 6]}).convert_dtypes()
    >>> check_ref(enc)
    Index([], dtype='int64')

    >>> enc = pd.DataFrame({'ref': [1, pd.NA, 3, 5, 4, 6]}).convert_dtypes()
    >>> check_ref(enc)
    Index([1, 3, 4], dtype='int64')

    >>> enc = pd.DataFrame({'ref': [1, 2, 4, 5, 6]}).convert_dtypes()
    >>> check_ref(enc)
    Index([2, 3, 4], dtype='int64')
    """

    good_ref = pd.Series(range(1, enc.shape[0] + 1), dtype=enc.ref.dtype)
    diffs = enc[(enc.ref != good_ref) | enc.ref.isna()].index
    return diffs


def check_clean_strs(enc: pd.DataFrame) -> pd.DataFrame:
    """Return new DataFrame containing values where any whitespace was not a simple
    whitespace in the original DataFrame with the rest of values being <NA>

    >>> enc = pd.DataFrame(
    ...     {
    ...         'locality': ['good1', 'go od 2', 'ba  d', 'ba\u00A0d', 'good3'],
    ...         'species': ['b\tad', 'good4', 'good5', 'bad  ', 'good7'],
    ...     }
    ... ).convert_dtypes()
    >>> check_clean_strs(enc)
      locality species
    0     <NA>    b ad
    1     <NA>    <NA>
    2     ba d    <NA>
    3     ba d     bad
    4     <NA>    <NA>
    """
    strs = enc.select_dtypes(['string'])
    cleaned_strs = strs.apply(lambda col: col.str.strip().replace(r'\s+', ' ', regex=True))
    diff = cleaned_strs[strs != cleaned_strs]
    return diff


def check_coords(enc: pd.DataFrame) -> tuple[pd.Index, pd.Index]:
    """Return tuple (idx_x, idx_y) of indices in *enc* where coord columns differ from the expected
    value implied by the quadrat_id column.

    >>> enc = pd.DataFrame(
    ...     {
    ...         'quadrat_id': ['q_1_good_1', 'q_1_badx_2', 'q_2_bady_1', 'q_2_good_2'],
    ...         'coord_x': [0, 1, 1, 1],
    ...         'coord_y': [0, 1, -2, 1],
    ...     }
    ... ).convert_dtypes()
    >>> check_coords(enc)
    (Index([1], dtype='int64'), Index([2], dtype='int64'))
    """
    splt = enc['quadrat_id'].str.split('_', expand=True)
    x_from_qid = pd.to_numeric(splt[1], downcast='unsigned') - 1
    y_from_qid = pd.to_numeric(splt[3], downcast='unsigned') - 1
    x_diff = enc[(x_from_qid - enc.coord_x) != 0]
    y_diff = enc[(y_from_qid - enc.coord_y) != 0]
    return x_diff.index, y_diff.index


def check_species_name(enc: pd.DataFrame) -> pd.Index:
    """Return indices in *enc* where single species
    has multiple values in name or vice versa.

    This should not happen has name is simply a translation of species.

    >>> enc = pd.DataFrame(
    ...     data={'species': ['spp1', 'spp2', 'spp2', 'spp3', 'spp4'], 'name': ['a', 'c', 'b', 'c', 'b']}
    ... ).convert_dtypes()
    >>> check_species_name(enc)
    Index([1, 2, 3, 4], dtype='int64')
    """

    spp_name = enc[['species', 'name']].drop_duplicates()
    spp_dups = spp_name.duplicated(subset='species', keep=False)
    name_dups = spp_name.duplicated(subset='name', keep=False)
    return spp_name[spp_dups | name_dups].index


def check_species_phase_morph(enc: pd.DataFrame) -> pd.Index:
    """Return indices in *enc* where a species in given phase occurs with more than one morph.

    This should not happen as species in given life phase are assigned only to one morphotaxon.

    >>> enc = pd.DataFrame(
    ...     data={
    ...         'species': ['spp1', 'spp2', 'spp2', 'spp1', 'spp1'],
    ...         'phase': ['1', '1', '2', '1', '1'],
    ...         'morph': ['a', 'a', 'b', 'a', 'b'],
    ...     }
    ... ).convert_dtypes()
    >>> check_species_phase_morph(enc)
    Index([0, 4], dtype='int64')
    """
    trio = enc[['species', 'phase', 'morph']].drop_duplicates()
    dups_bools = trio.duplicated(subset=['species', 'phase'], keep=False)
    return trio[dups_bools].index


def check_morph_species(enc: pd.DataFrame) -> pd.Index:
    """Return indices in *enc* where the morph is either not identical with the species
    or does not start with 'M ', which indicates a morphotaxon.

    This should not happen as either the species itself should be known or the morphotaxon should be specified.

    >>> enc = pd.DataFrame(
    ...     data={
    ...         'morph': ['M morph0', 'M morph1', 'm morph0', 'Morph2', 'morph3'],
    ...         'species': ['spp0', 'spp1', 'm morph0', 'spp2', 'spp3'],
    ...     }
    ... ).convert_dtypes()
    >>> check_morph_species(enc)
    Index([3, 4], dtype='int64')
    """
    non_m = enc[~enc.morph.str.startswith('M ')]
    return non_m[non_m.morph != non_m.species].index


def check_family(enc: pd.DataFrame) -> pd.Index:
    """Return indices in *enc* where species is "Labridae" or "Scaridae" yet phase is "ad".
    This should not occur as while other families have only juvenile and adult phase in our datasets,
    Labridae and Scaridae have juvenile, initial and terminal phase.

    >>> enc = pd.DataFrame(
    ...     data={
    ...         'phase': ['ad', 'juv', 'init', 'term', 'ad'],
    ...         'family': ['Labridae', 'Labridae', 'Scaridae', 'Scaridae', 'Scaridae'],
    ...     }
    ... ).convert_dtypes()
    >>> check_family(enc)
    Index([0, 4], dtype='int64')
    """
    lab_scar = enc[(enc.family == 'Labridae') | (enc.family == 'Scaridae')]
    return lab_scar[lab_scar.phase == 'ad'].index
