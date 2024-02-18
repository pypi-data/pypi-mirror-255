import argparse
import math
import numpy as np
import pandas as pd
import random
import sys

from alive_progress import alive_bar
from alive_progress.animations.spinners import bouncing_spinner_factory
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import cast, Callable, Literal, TypeGuard

import seal.config as conf
from seal.common import analysis_results_name, enc_dtypes, Encounters, data_dir, Sides, QList

type Coord = tuple[int, int]  # type: ignore[valid-type]
type CoordCol = Literal['coord_x', 'coord_y']
type DistFunction = Callable[[pd.DataFrame, pd.DataFrame], pd.Series]
type Edge = Literal['left', 'right', 'top', 'bottom']
type LvlType = Literal[
    'nested-quadrats',
    'overlaid-subgrids',
    'repeated-transect-merging',
    'striped-transect-merging',
    'transect-additive',
    'transect-merging',
    'zone-additive',
    'zone-merging',
]
type SppMatrix = pd.DataFrame


@dataclass
class Position:
    """Represents coordinates of quadrat on a grid"""

    x_g: int
    y_g: int


@dataclass
class Point:
    """Represents point on a grid with coordinates in meters"""

    x_m: float
    y_m: float


def main(args: argparse.Namespace) -> int:
    """Load taskfile configuration, datasets, perform and save
    requested analyses. Create output directory if necessary.
    """

    cfg = conf.Config.from_file(args.taskfile)
    enc_path = Path(cfg.get_string('encounters'))
    enc = load_encounters(enc_path)


    dist_fn_type = cfg.get_string('distance-type', 'diagonal')
    quadrat_types = cfg.get_list('quadrat-types', ['normal'])
    quadrat_types = [str(val) for val in quadrat_types]
    locality = cfg.get_subconf('locality')
    qlist_path = Path(locality.get_string('quadrat-list'))
    quadrats = load_quadrats(qlist_path, quadrat_types)

    enc = filter_encounters(enc, cfg)
    qids_enc = set(enc.quadrat_id)
    qids_qlist = set(quadrats.quadrat_id)
    qids_diff = qids_enc - qids_qlist
    if len(qids_diff) > 0:
        print(
            f"""Filtered dataset contains encounters in quadrats not found in quadrat list.
            Possible causes may be using quadrat list for unintended locality, incorrectly set-up filters, e.g. *from* and *to* dates in taskfile\'s locality section or simply mistakes/typos in provided quadrat list or dataset.
            Extraneous IDs:
            {qids_diff}
            """
        )
        sys.exit(1)

    discard_transect = cfg.get_bool('discard-transect-info', False)
    discard_zone = cfg.get_bool('discard-zone-info', False)
    sides_orig = Sides(**locality.get('sides'))  # type: ignore[arg-type] # is a mapping (or should be)
    quadrats = add_quadrat_centroids(quadrats, sides_orig)
    enc, quadrats, sides_adj = adjust_grid(enc, quadrats, sides_orig, discard_transect, discard_zone)
    locality.put( # technically, they are adjusted, but for the purposes of other computations they replace original values completely
        'sides', {'x': sides_adj.x, 'y': sides_adj.y}
    )
    caps = compute_caps(quadrats, sides_orig)

    completed: dict[str, pd.DataFrame] = {}
    additional: dict[str, list[str | pd.DataFrame]] = defaultdict(list)

    levels = cfg.get_list('levels')
    analyses = cfg.get_list('analyses')
    n_tasks = len(levels) * len(analyses)
    if not is_int_list(levels):
        raise conf.InvalidTaskError('level values should be integers')
    seed = cfg.get_int_unchecked('seed', None)

    emoji = ['🐧', '🐡', '🐟', '🦑', '🦦', '🐠', '🦐', '🐙']
    random.shuffle(emoji)
    emoji = ''.join(emoji)
    spinner = bouncing_spinner_factory(('🌊', emoji), 6, block=(1, 1), hide=True)

    with alive_bar(n_tasks, title='Analysis', spinner=spinner) as bar:
        for level in levels:
            lvl_strat = cfg.get_string('level-strategy', 'striped-transect-merging')
            enc_subgrids, q_subgrids, sides_adj = adjust_for_lvl(
                enc,
                quadrats,
                locality,
                level,
                max(levels),
                lvl_strat,  # type: ignore[arg-type] # method rejects invalid strats, no need for TypeGuard
                sides_orig,
            )
            capped_dist_fn = get_distance_function(dist_fn_type, sides_adj, caps)
            dmats = [distance_matrix(qs, capped_dist_fn) for qs in q_subgrids]
            for analysis in analyses:
                analysis = conf.Config.from_string(f'type = {analysis}') if isinstance(analysis, str) else analysis
                analysis = cast(conf.Config, analysis)
                a_type = analysis.get_string('type')
                bar.text(f'{a_type}, level {level}')
                res, additional_data = do_analysis(enc_subgrids, q_subgrids, dmats, analysis, sides_adj, seed, caps)
                res['level'] = level

                if additional_data is not None:
                    additional[a_type].append(additional_data)
                prev = completed.get(a_type, pd.DataFrame())
                completed[a_type] = pd.concat([prev, res])  # todo: build list, concat just once
                bar()
    out_dir = data_dir(cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    save_results(args, out_dir, completed, additional)
    return 0


def do_analysis(
    enc_subgrid: list[Encounters],
    q_subgrid: list[QList],
    dmats: list[pd.DataFrame],
    analysis: conf.Config,
    sides_adj: Sides,
    seed: int | None,
    caps: dict[str, float],
) -> tuple[pd.DataFrame, str | pd.DataFrame | None]:
    """Pick appropriate analysis to perform on passed subgrids
    with given config settings and return its results.
    """

    if seed:
        random.seed(seed)
        np.random.seed(seed)


    spp_matrices = []
    for enc, qlist in zip(enc_subgrid, q_subgrid, strict=True):
        spp_matrices.append(get_spp_matrix(enc, qlist))
    match analysis.get_string('type'):
        case 'a1' | 'overview':
            return a1_overview(enc_subgrid, q_subgrid)
        case 'a2' | 'sar':
            return a2_sar(enc_subgrid, q_subgrid, spp_matrices, analysis, sides_adj, caps)
        case 'a3' | 'spdiff':
            return a3_species_delta(enc_subgrid, q_subgrid, spp_matrices, dmats, analysis)
        case 'a4' | 'rrich':
            return a4_avg_radius_richness(enc_subgrid, q_subgrid, spp_matrices, dmats, analysis)
        case 'a5' | 'oerich':
            return a5_observed_expected(enc_subgrid, q_subgrid, spp_matrices)
        case 'a6' | 'sratios':
            return a6_shared_ratios(enc_subgrid, q_subgrid, spp_matrices, dmats)
        case 'a7' | 'jaccard':
            return a7_jaccard_diss(enc_subgrid, q_subgrid, spp_matrices, dmats)
        case _:
            raise conf.InvalidTaskError(analysis.get_string('type'))


class TilingError(Exception):
    """Exception raised when request quadrat level doesn't fit the study grid.

    Attributes:
        level -- level being analyzed
        sides -- dimensions of the entire locality
    """

    def __init__(self, level: int, sides: Sides):
        super().__init__(f'Requested level {level} incompatible with locality dimensions: {sides.x} x {sides.y}')


def describe_full(df: pd.DataFrame) -> pd.DataFrame:
    stats = df.describe(percentiles=[0.025, 0.25, 0.5, 0.75, 0.975], include='all')
    stats.loc['median'] = df.median(numeric_only=True)
    stats.loc['sem'] = df.sem(numeric_only=True)
    stats.loc['skewness'] = df.skew(numeric_only=True)
    stats.loc['kurtosis'] = df.kurtosis(numeric_only=True)
    return stats


def a1_overview(enc_subgrid: list[Encounters], q_subgrid: list[QList]) -> tuple[pd.DataFrame, str]:
    """Return DataFrame containing number of unique species
    as well as number of individuals encountered in respective quadrats.
    Additional data contains per-level (and per-subgrid if applicable)
    descriptive statistics about encounters being processed.
    """

    res = []
    uniques = []
    res += ['====LEVEL OVERVIEW START====']
    for i, (enc, quadrats) in enumerate(zip(enc_subgrid, q_subgrid, strict=True)):
        if len(enc_subgrid) > 1:
            res += [f'===SUBGRID #{i} START===']
        desc = describe_full(enc)
        res += [desc.to_string()]

        by_qid = enc.groupby(['coord_x', 'coord_y'])
        unique = by_qid.species.nunique()
        # fill 0 for quadrats where nothing was encountered
        unique = unique.reindex(quadrats.index, fill_value=0).to_frame('n_species')
        unique['n_individuals'] = by_qid.individuals.sum()
        assert (unique['n_individuals'] >= unique['n_species']).all()
        unique = unique.fillna(0)
        res += ['\n==Unique per quadrat==']
        res += [unique.to_string()]

        avg = unique / len(quadrats)
        res += [f'\n==Avg per quadrat==\n{avg.to_string()}']

        indist_mask = enc.species.str.endswith(' sp.', na=True)
        indist_enc = indist_mask.sum()
        res += ['\n==Indistinguishable encounters #==']
        res += [f'{indist_enc}']
        res += ['\n==Indistinguishable encounters %==']
        res += [f'{100 * indist_enc / (indist_enc + len(enc.index))}']
        indist_individuals = enc[indist_mask].individuals.sum()
        res += ['\n==Indistinguishable individuals #==']
        res += [f'{indist_individuals}']
        res += ['\n==Indistinguishable individuals %==']
        res += [f'{100 * indist_individuals / enc.individuals.sum()}']

        res += ['\n==Direction richness difference==']
        dirdiff = direction_difference(enc).dropna()
        dirdiff['diff_abs#'] = dirdiff['diff_#'].abs()
        dirdiff = dirdiff.sort_values(by='diff_abs#', ascending=False)
        res += [describe_full(dirdiff).to_string(), '\n']
        res += [dirdiff.to_string()]

        if len(enc_subgrid) > 1:
            res += [f'===SUBGRID #{i} END===\n']

        unique = unique.reset_index(drop=False)
        uniques.append(unique)
    res += ['====LEVEL OVERVIEW END====\n\n']
    unique_avg = pd.concat(uniques, ignore_index=True).groupby(['coord_x', 'coord_y']).mean().convert_dtypes()
    unique_avg = unique_avg.assign(
        coord_x=quadrats.index.get_level_values('coord_x'), coord_y=quadrats.index.get_level_values('coord_y')
    )
    return (unique_avg, '\n'.join(res))


def a2_sar(
    enc_subgrids: list[Encounters],
    q_subgrids: list[QList],
    spp_matrices: list[pd.DataFrame],
    analysis: conf.Config,
    sides_adj: Sides,
    caps: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return DataFrame containing quadrat richness accumulation
    in random order with separate columns for slowest and fastest
    growing series and total accumulated area.
    """

    accumulated = []
    permutations = analysis.get_int('permutations')
    for spp_matrix in spp_matrices:
        for _ in range(permutations):
            shuff = acc_richness_shuffled(spp_matrix)
            accumulated.append(shuff)
    sar = pd.DataFrame(accumulated).transpose()
    sar_add = agg_results(sar, 'n_species', 'area')

    min_acc = sar[0].to_list()
    max_acc = sar[0].to_list()
    for colname in sar:
        col = sar[colname].to_list()
        if col < min_acc:
            min_acc = col
        if col > max_acc:
            max_acc = col
    sar['min_acc'] = min_acc
    sar['max_acc'] = max_acc

    surface_area = sides_adj.x * sides_adj.y
    sar['area'] = np.minimum((sar.index + 1) * surface_area, caps['total_area'])
    sar_add['area'] = sar['area']
    return sar, sar_add


def a3_species_delta(
    enc_subgrids: list[Encounters],
    q_subgrids: list[QList],
    spp_matrices: list[SppMatrix],
    dmats: list[pd.DataFrame],
    analysis: conf.Config,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return DataFrame containing distance-dependent species difference.
    Absolute and relative differences between species lists are calculated
    for each pair of quadrats of given distance. This is done with all possible
    pairs of quadrats of given level.
    """

    deltas_list = []
    for enc, quadrats, richness, dmat in zip(enc_subgrids, q_subgrids, spp_matrices, dmats, strict=True):
        sub_deltas = species_delta(richness, dmat)
        deltas_list.append(sub_deltas)
    deltas = pd.concat(deltas_list)
    deltas = deltas[deltas.distance > 0]

    deltas_stats = deltas.reset_index(drop=True)
    interval = analysis.get_float_unchecked('interval', None)
    if interval and not deltas_stats.empty:
        bins = pd.interval_range(0, deltas_stats.distance.max() + interval, freq=interval, closed='left') # type: ignore[call-overload] # should accept numeric, but rejects float; pandas 2.2.0 bug?
        deltas_stats['distance'] = pd.cut(deltas_stats.distance, bins)
    deltas_stats = deltas_stats.groupby('distance', observed=False).agg(AGG_STATS)
    deltas_stats = flatten_multicolumns(deltas_stats)
    return (deltas, deltas_stats)


def a4_avg_radius_richness(
    enc_subgrids: list[Encounters],
    q_subgrids: list[QList],
    spp_matrices: list[pd.DataFrame],
    dmats: list[pd.DataFrame],
    cfg: conf.Config,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return DataFrame containing the sum of richness
    of quadrats orbiting a select as a point of origin.
    This is done for every quadrat in a grid for every distance bin.
    Additional data is returned as an aggregation of various statistics
    for said DataFrame.
    """

    step = cfg.get_float('radius-step')
    radius_richness_lst = []
    for enc, quadrats, spp_matrix, dmat in zip(enc_subgrids, q_subgrids, spp_matrices, dmats, strict=True):
        radius_bins = pd.interval_range(0, dmat.distance.max() + step, freq=step, closed='left')  # type: ignore[call-overload]  # freq should accept float, pd or mypy err?
        dmat = dmat.assign(distance=pd.cut(dmat.distance, radius_bins)).dropna()
        dmat_groups = dmat.groupby(['coord_x', 'coord_y', 'distance'], observed=False)

        def rpd(df: pd.DataFrame) -> int:
            return total_radius_richness(df, spp_matrix)

        radius_richness = dmat_groups.agg(rpd)
        radius_richness_lst.append(radius_richness)
    radius_richness = (
        pd.concat(radius_richness_lst).reset_index().rename({0: 'radius_richness'}, errors='raise', axis='columns')
    )
    stats = (
        radius_richness.drop(['coord_x', 'coord_y'], axis='columns', errors='raise')
        .groupby(by='distance', observed=False)
        .agg(AGG_STATS)
    )
    stats = stats
    stats = flatten_multicolumns(stats)
    return (radius_richness, stats)


def a5_observed_expected(
    enc_subgrids: list[pd.DataFrame], q_subgrids: list[pd.DataFrame], spp_matrices: list[SppMatrix]
) -> tuple[pd.DataFrame, None]:
    """Return DataFrame containing observed and expected
    species occurences in a given list of subgrids.
    """

    oe_ratios = []
    for enc, quadrats, spp_matrix in zip(enc_subgrids, q_subgrids, spp_matrices, strict=True):
        species_in_n_quadrats = enc.groupby('species').quadrat_id.nunique()
        observed_ratio = species_in_n_quadrats / len(quadrats)
        expected_var = (observed_ratio * (1 - observed_ratio)).sum()
        q_richnesses = spp_matrix.sum(axis='columns')
        oe_ratio = q_richnesses / expected_var
        oe_ratios.append(pd.DataFrame({'oe_ratio': oe_ratio}))
    oe_ratios = pd.concat(oe_ratios, axis='columns')
    oe_ratios = pd.DataFrame(
        {'oe_ratio_mean': oe_ratios.mean(axis='columns'), 'oe_ratio_med': oe_ratios.median(axis='columns')}
    )
    return oe_ratios, None


def a6_shared_ratios(
    enc_subgrids: list[Encounters], q_subgrids: list[QList], spp_matrices: list[SppMatrix], dmats: list[pd.DataFrame]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return DataFrame containing ratios of species intersection vs
    species total and union of species for respective distances
    between quadrats in a given list of subgrids.
    Additional data is returned as an aggregation of various statistics
    for said DataFrame.
    """

    res: dict[str, list[pd.Series]] = {
        'common_diff': [],
        'common_total': [],
        'common_union': [],
        'distance': [],
    }
    for enc, quadrats, spp_matrix, dmat in zip(enc_subgrids, q_subgrids, spp_matrices, dmats, strict=True):
        spp_grid_total = len(spp_matrix.columns)
        for idx, row in spp_matrix.iterrows():
            n_intersect = (spp_matrix & row).sum(axis='columns')
            n_xor = (spp_matrix ^ row).sum(axis='columns')
            n_union = (spp_matrix | row).sum(axis='columns')

            res['common_diff'].append(n_intersect / n_xor)
            res['common_total'].append(n_intersect / spp_grid_total)
            res['common_union'].append(n_intersect / n_union)
            res['distance'].append(dmat.loc[idx, 'distance'])  # type: ignore[arg-type, index]   # is truly pd.Series, can be indexed by MultiIndex tuple just fine
    res = {k: pd.concat(v) for k, v in res.items()}
    ratios = pd.DataFrame(res)
    ratios = ratios[ratios.distance > 0]
    with np.errstate(invalid='ignore'):  # inf-inf may occur since values above may be inf
        ratios_stats = ratios.groupby('distance').agg(AGG_STATS)
    ratios_stats = flatten_multicolumns(ratios_stats)
    return ratios, ratios_stats


def a7_jaccard_diss(
    enc_subgrids: list[Encounters], q_subgrids: list[QList], spp_matrices: list[pd.DataFrame], dmats: list[pd.DataFrame]
) -> tuple[pd.DataFrame, None]:
    """Return DataFrame containing Jaccard dissimilarity for
    for respective distances between quadrats in a given list of subgrids.
    """

    jaccards_list = []
    for enc, quadrats, spp_matrix, dmat in zip(enc_subgrids, q_subgrids, spp_matrices, dmats, strict=True):
        jaccards_list.append(jaccard_dissimilatity(spp_matrix, dmat))
    list_of_jaccard_lists = pd.concat(jaccards_list)
    return list_of_jaccard_lists, None


def jaccard_dissimilatity(spp_matrix: pd.DataFrame, dmat: pd.DataFrame) -> pd.DataFrame:
    """Return Jaccard dissimilarity for respective distances in a DataFrame.

    >>> spp_idx = pd.MultiIndex.from_arrays([[0, 0, 1], [0, 1, 0]], names=('coord_x', 'coord_y'))
    >>> spp_matrix = pd.DataFrame(
    ...     index=spp_idx,
    ...     data={
    ...         'A': [True, True, False],
    ...         'B': [True, False, False],
    ...         'C': [True, False, False],
    ...         'D': [False, True, False],
    ...     },
    ... )
    >>> idx = pd.MultiIndex.from_tuples(
    ...     [
    ...         (0, 0, 0, 0),
    ...         (0, 0, 0, 1),
    ...         (0, 0, 1, 0),
    ...         (0, 1, 0, 0),
    ...         (0, 1, 0, 1),
    ...         (0, 1, 1, 0),
    ...         (1, 0, 0, 0),
    ...         (1, 0, 0, 1),
    ...         (1, 0, 1, 0),
    ...     ],
    ...     names=['coord_x', 'coord_y', 'coord_x_other', 'coord_y_other'],
    ... )
    >>> dmat = pd.DataFrame(index=idx, data={'distance': [0, 1, 1, 1, 0, 2, 1, 2, 0]})
    >>> jaccard_dissimilatity(spp_matrix, dmat)
       jaccard_dissimilarity  log_jaccard_dissimilarity  distance
    1                   0.75                  -0.124939         1
    2                   1.00                   0.000000         1
    3                   0.75                  -0.124939         1
    5                   1.00                   0.000000         2
    6                   1.00                   0.000000         1
    7                   1.00                   0.000000         2
    """

    jacc_diss = []
    dists = []
    for idx, row in spp_matrix.iterrows():
        n_intersect = (spp_matrix & row).sum(axis='columns')
        n_unique_a = (spp_matrix & ~row).sum(axis='columns')
        n_unique_b = (~spp_matrix & row).sum(axis='columns')

        divisor = n_intersect + n_unique_a + n_unique_b
        jd = 1 - (n_intersect / divisor)

        jacc_diss.append(jd)
        dists.append(dmat.loc[idx, 'distance'])  # type: ignore[index]   # can be indexed by MultiIndex tuple just fine
    jd_series = pd.concat(jacc_diss, ignore_index=True)  #
    with np.errstate(divide='ignore'):  # J.d. may be 0 for 2 quadrats with same species, results in NaN
        log_jd = np.log10(jd_series)
    res = pd.DataFrame(
        {
            'jaccard_dissimilarity': jd_series,
            'log_jaccard_dissimilarity': log_jd,
            'distance': pd.concat(dists, ignore_index=True),
        }
    )
    res = res[res.distance > 0]
    return res


def adjust_for_lvl(
    enc: Encounters, quadrats: QList, locality: conf.Config, lvl: int, max_lvl: int, lvl_strat: LvlType, sides: Sides
) -> tuple[list[pd.DataFrame], list[pd.DataFrame], Sides]:
    """Transform study grid according to current level and level strategy.
    Returns list because 'overlaid-subgrids' level strategy averages multiple subgrids.
    """

    # todo: split into individual functions, docs + unit tests
    new_x = sides.x
    new_y = sides.y
    # todo: use either .loc or standalone pd.Series
    quadrats['coord_x'] = quadrats.index.get_level_values('coord_x')
    quadrats['coord_y'] = quadrats.index.get_level_values('coord_y')
    if lvl_strat == 'transect-additive':
        enc = enc[enc.coord_x < lvl]
        quadrats = quadrats[quadrats.coord_x < lvl]
    elif lvl_strat == 'zone-additive':
        enc = enc[enc.coord_y < lvl]
        quadrats = quadrats[quadrats.coord_y < lvl]
    elif lvl_strat == 'overlaid-subgrids':
        cutoffs = cutting_bounds(quadrats, lvl)
        q_subgrids = create_subgrids(quadrats, cutoffs)
        shift_tuples = get_shift_tuples(q_subgrids)
        q_subgrids = shift_coords(q_subgrids, shift_tuples, lvl)

        enc_subgrids = create_subgrids(enc, cutoffs)
        enc_subgrids = shift_coords(enc_subgrids, shift_tuples, lvl)

        quadrats['centroid_x'] = quadrats['centroid_x'] + ((sides.x / 2) * lvl)
        quadrats['centroid_y'] = quadrats['centroid_y'] + ((sides.y / 2) * lvl)

        new_x *= lvl
        new_y *= lvl
    elif lvl_strat == 'transect-merging':
        enc = enc[enc.coord_x < lvl]
        enc = replace_coords(enc, {'coord_x': 0})

        quadrats = quadrats[quadrats.coord_x < lvl]
        quadrats = replace_coords(quadrats, {'coord_x': 0})
        quadrats = quadrats.drop_duplicates(subset=['coord_x', 'coord_y'])
        quadrats['centroid_x'] = quadrats['centroid_x'] + ((sides.x / 2) * lvl)

        new_x *= lvl
    elif lvl_strat == 'zone-merging':
        enc = enc[enc.coord_y < lvl]
        enc = replace_coords(enc, {'coord_y': 0})

        quadrats = quadrats[quadrats.coord_y < lvl]
        quadrats = replace_coords(quadrats, {'coord_y': 0})
        quadrats = quadrats.drop_duplicates(subset=['coord_x', 'coord_y'])
        quadrats['centroid_y'] = quadrats['centroid_y'] + ((sides.y / 2) * lvl)

        new_y *= lvl
    elif lvl_strat == 'repeated-transect-merging':
        new_xs = enc.coord_x.floordiv(lvl)
        enc = replace_coords(enc, {'coord_x': new_xs})

        new_xs = quadrats.coord_x.floordiv(lvl)
        quadrats = replace_coords(quadrats, {'coord_x': new_xs})
        quadrats = quadrats.drop_duplicates(subset=['coord_x', 'coord_y'])
        quadrats['centroid_x'] = quadrats['centroid_x'] + ((sides.x / 2) * lvl)
        quadrats = quadrats.set_index(['coord_x', 'coord_y'], drop=False, verify_integrity=True)

        new_x *= lvl
    elif lvl_strat == 'striped-transect-merging':
        enc = enc[(enc.coord_x % max_lvl) < lvl]
        new_xs = enc.coord_x.floordiv(max_lvl)
        enc = replace_coords(enc, {'coord_x': new_xs})

        quadrats = quadrats[(quadrats.coord_x % max_lvl) < lvl]
        new_xs = quadrats.coord_x.floordiv(max_lvl)
        quadrats = replace_coords(quadrats, {'coord_x': new_xs})
        quadrats = quadrats.drop_duplicates(subset=['coord_x', 'coord_y'])
        quadrats = quadrats.set_index(['coord_x', 'coord_y'], drop=False, verify_integrity=True)
        quadrats['centroid_x'] = quadrats['centroid_x'] + ((sides.x / 2) * lvl)

        new_x *= lvl
    elif lvl_strat == 'nested-quadrats':
        merges = [1, 2]
        discards = [2, 1]
        merge_n_quadrats = 2 ** (lvl - 1)
        print('CURR LVL: ', lvl)
        print(f'MERGING {merge_n_quadrats}x{merge_n_quadrats} orig quadrats\n')
        assert merge_n_quadrats == merges[lvl - 1]
        retain_every_nth = 2 ** (max_lvl - lvl)
        print(f'WILL RETAIN EVERY {retain_every_nth}nd quadrat\n')
        assert retain_every_nth == discards[lvl - 1]

        new_xs = enc.coord_x.floordiv(merge_n_quadrats)
        new_ys = enc.coord_y.floordiv(merge_n_quadrats)
        enc = replace_coords(enc, {'coord_x': new_xs, 'coord_y': new_ys})
        keep_x = (enc.coord_x % retain_every_nth) == 0
        keep_y = (enc.coord_y % retain_every_nth) == 0
        enc = enc[keep_x & keep_y]
        # todo: do quadrats first, then simply drop those not in quadrats?

        new_xs = quadrats.coord_x.floordiv(merge_n_quadrats)
        new_ys = quadrats.coord_y.floordiv(merge_n_quadrats)
        quadrats = replace_coords(quadrats, {'coord_x': new_xs, 'coord_y': new_ys})
        quadrats = quadrats.drop_duplicates(subset=['coord_x', 'coord_y'])

        keep_x = (quadrats.coord_x % retain_every_nth) == 0
        keep_y = (quadrats.coord_y % retain_every_nth) == 0
        quadrats = quadrats[keep_x & keep_y]

        quadrats = quadrats.set_index(['coord_x', 'coord_y'], drop=False, verify_integrity=True)

        quadrats['centroid_x'] = quadrats['centroid_x'] + ((sides.x / 2) * merge_n_quadrats)
        quadrats['centroid_y'] = quadrats['centroid_y'] + ((sides.y / 2) * merge_n_quadrats)

        new_x = sides.x * merge_n_quadrats
        new_y = sides.y * merge_n_quadrats

        qids_enc = set(enc.quadrat_id)
        qids_qlist = set(quadrats.quadrat_id)
        qids_diff = qids_enc - qids_qlist
        if len(qids_diff) > 0:
            print(
                f'''Filtered dataset contains encounters in quadrats not found in quadrat list.
                Possible causes may be using quadrat list for unintended locality, incorrectly set-up filters, e.g. *from* and *to* dates in taskfile\'s locality section or simply mistakes/typos in provided quadrat list or dataset.
                Extraneous IDs:
                {list(sorted(qids_diff))}
                '''
            )
            sys.exit(1)
    else:
        raise conf.InvalidTaskError(lvl_strat)

    assert list(quadrats['coord_x']) == list(quadrats.index.get_level_values('coord_x'))
    assert list(quadrats['coord_y']) == list(quadrats.index.get_level_values('coord_y'))

    if lvl_strat != 'overlaid-subgrids':
        enc_subgrids = [enc]
        q_subgrids = [quadrats]
    sides_adj = Sides(new_x, new_y)

    assert len(enc_subgrids) == len(q_subgrids)
    for e, q in zip(enc_subgrids, q_subgrids, strict=True):
        assert set(zip(e.coord_x, e.coord_y)).issubset(
            set(zip(q.coord_x, q.coord_y))
        )  # every encounter must be in a known quadrat

    return (enc_subgrids, q_subgrids, sides_adj)


def is_int_list(lst: Sequence[object]) -> TypeGuard[Sequence[int]]:
    """Verify that all objects in *lst* are integers."""
    # todo: test

    return all(isinstance(elem, int) for elem in lst)


def add_quadrat_centroids(quadrats: pd.DataFrame, sides: Sides) -> pd.DataFrame:
    """Add centroid_x and centroid_y columns to *quadrats* with coordinates of quadrats' centroids.

    >>> qlist = pd.DataFrame(
    ...     index=pd.MultiIndex.from_arrays([[0, 0, 1, 1, 2], [0, 1, 0, 1, 0]], names=('coord_x', 'coord_y'))
    ... )
    >>> add_quadrat_centroids(qlist, Sides(1, 2))  # doctest: +NORMALIZE_WHITESPACE
                     centroid_x  centroid_y
    coord_x coord_y
    0       0               0.5         1.0
            1               0.5         3.0
    1       0               1.5         1.0
            1               1.5         3.0
    2       0               2.5         1.0
    """
    quadrats['centroid_x'] = (quadrats.index.get_level_values('coord_x') * sides.x) + (sides.x / 2)
    quadrats['centroid_y'] = (quadrats.index.get_level_values('coord_y') * sides.y) + (sides.y / 2)
    return quadrats


def compute_caps(quadrats: QList, sides: Sides) -> dict[str, float]:
    """Compute and return maximum possible area distance in a study grid.
    This is necessary because some grid transformations, e.g. involving
    quadrat merging, could result in the grid seeming larger for a
    given level.
    Does not take grid irregularities, like nonsampled shallows, into account.

    >>> qlist = pd.DataFrame(
    ...     index=pd.MultiIndex.from_arrays([[0, 0, 1, 1, 2], [0, 1, 0, 1, 0]], names=('coord_x', 'coord_y'))
    ... )
    >>> compute_caps(qlist, Sides(1, 2))
    {'total_area': 12, 'max1dx': 3, 'max1dy': 4, 'diagonal': 5.0, 'centroid': 2.8284271247461903}
    """

    x_max = quadrats.index.get_level_values('coord_x').max()
    y_max = quadrats.index.get_level_values('coord_y').max()
    max1dx = (1 + x_max) * sides.x
    max1dy = (1 + y_max) * sides.y
    total_area = max1dx * max1dy
    diagonal = math.sqrt(max1dx**2 + max1dy**2)
    centroid_diff = {'x': max1dx - sides.x, 'y': max1dy - sides.y}
    centroid = math.sqrt(centroid_diff['x'] ** 2 + centroid_diff['y'] ** 2)
    return {'total_area': total_area, 'max1dx': max1dx, 'max1dy': max1dy, 'diagonal': diagonal, 'centroid': centroid}


def save_results(
    args: argparse.Namespace,
    out_dir: Path,
    completed: dict[str, pd.DataFrame],
    additional: dict[str, list[str | pd.DataFrame]],
) -> None:
    """Save analysis results in *completed* and additional data in
    *additional* to *out_dir*. *out_dir* must be created
    beforehand.
    """

    for analysis, df in completed.items():
        out_file = analysis_results_name(out_dir, args, analysis)
        df.to_csv(out_file, index=False)
        print(f'Result written to {out_file}')

    for analysis, data_lst in additional.items():
        out_file = out_dir / f'{args.taskfile.stem}-{analysis}-add'
        if isinstance(data_lst[0], pd.DataFrame):
            out_file = out_file.with_suffix('.csv')
            for lvl, adf in enumerate(data_lst):
                adf['level'] = lvl  # type: ignore[index]
            pd.concat(data_lst).to_csv(out_file)  # type: ignore[arg-type]
        else:
            out_file = out_file.with_suffix('.txt')
            with open(out_file, 'w') as out:
                out.write('\n'.join(data_lst))  # type: ignore[arg-type]
        print(f'Additional data written to {out_file}')


def replace_coords(df: pd.DataFrame, coords: dict[CoordCol, int | pd.Series]) -> pd.DataFrame:
    """Assigns coordinates to appropriate columns and changes quadrat_id to reflect said changes.
    Erases dd/mm/yyyy part because it causes certain quadrats to be split over dates

    >>> df = pd.DataFrame(
    ...     {
    ...         'coord_x': [0, 0, 1, 1, 2],
    ...         'coord_y': [0, 1, 0, 1, 0],
    ...         'quadrat_id': [
    ...             'T_1_2/3/2022_1',
    ...             'T_1_2/3/2022_2',
    ...             'T_2_2/3/2022_1',
    ...             'T_2_3/3/2022_2',
    ...             'T_3_3/3/2022_1',
    ...         ],
    ...     }
    ... )
    >>> new_coords = {'coord_x': [3, 4, 5, 6, 7], 'coord_y': [8, 7, 6, 5, 4]}
    >>> replace_coords(df, new_coords)
       coord_x  coord_y quadrat_id
    0        3        8      T_4_9
    1        4        7      T_5_8
    2        5        6      T_6_7
    3        6        5      T_7_6
    4        7        4      T_8_5
    """

    df = df.assign(**coords)  # type: ignore[misc]

    id_split = df['quadrat_id'].str.split('_')
    q_id_iter = zip(id_split, df['coord_x'], df['coord_y'], strict=True)
    new_ids = [strs[0] + f'_{x+1}_{y+1}' for strs, x, y in q_id_iter]
    id_split = pd.Series(data=new_ids, index=id_split.index)
    df['quadrat_id'] = id_split
    return df


def total_radius_richness(dist_group: pd.DataFrame, spp_matrix: pd.DataFrame) -> int:
    """Return total richness in a given distance group.
    Assumes that distance group (radius) from a certain quadrat
    has already been created by previous grouping.

    >>> idx = pd.MultiIndex.from_arrays(
    ...     [[0, 0, 0, 0], [0, 0, 0, 0], [10, 10, 10, 10], [0, 0, 0, 0], [0, 1, 2, 3]],
    ...     names=('coord_x', 'coord_y', 'distance', 'coord_x_other', 'coord_y_other'),
    ... )
    >>> dist_group = pd.DataFrame(index=idx, data={})
    >>> spp_idx = pd.MultiIndex.from_arrays([[0, 0, 0, 0], [0, 1, 2, 3]], names=('coord_x', 'coord_y'))
    >>> spp_matrix = pd.DataFrame(
    ...     index=spp_idx,
    ...     data={
    ...         'A': [True, True, False, False],
    ...         'B': [True, False, False, False],
    ...         'C': [True, True, False, False],
    ...         'D': [False, False, False, False],
    ...         'E': [False, False, True, False],
    ...     },
    ... )
    >>> total_radius_richness(dist_group, spp_matrix)
    4
    """

    peri_idx = pd.MultiIndex.from_arrays(
        [dist_group.index.get_level_values('coord_x_other'), dist_group.index.get_level_values('coord_y_other')]
    )
    perimeter = spp_matrix.loc[peri_idx]
    perimeter_richness = perimeter.cumsum().astype(bool).iloc[-1].sum()
    return perimeter_richness


def flatten_multicolumns(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience function to flatten and rename multicolumns in a DataFrame

    >>> cols = pd.MultiIndex.from_tuples([('top', 'btm1'), ('top', 'btm2')])
    >>> multi = pd.DataFrame(data=[[0, 1], [2, 3]], columns=cols)
    >>> flatten_multicolumns(multi)
       top_btm1  top_btm2
    0         0         1
    1         2         3
    """
    df.columns = df.columns.to_flat_index()
    name_map = {col: f'{col[0]}_{col[1]}' for col in df.columns}
    df = df.rename(name_map, axis='columns', errors='raise')
    return df


def get_distance_function(dist_type: str, sides_adj: Sides, caps: dict[str, float]) -> DistFunction:
    """Return function to use for computing values in distance matrix.

    >>> loc = conf.Config.from_string('sides_adj = { x = 1, y = 1}')
    >>> get_distance_function('diagonal', loc, None)  # doctest: +ELLIPSIS
    <function get_distance_function.<locals>.<lambda> at ...>
    >>> get_distance_function(':)', loc, None)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    RuntimeError: Invalid distance ":)" specified in taskfile
    """

    if dist_type == 'centroid':
        return lambda ps, qs: q_distance_centroid(ps, qs, sides_adj, caps)
    elif dist_type == 'max1d':
        return lambda ps, qs: q_distance_collapsed(ps, qs, sides_adj, caps)
    elif dist_type == 'diagonal':
        return lambda ps, qs: q_distance_diagonal(ps, qs, sides_adj, caps)
    else:
        raise RuntimeError(f'Invalid distance "{dist_type}" specified in taskfile')


def filter_encounters(enc: pd.DataFrame, cfg: conf.Config) -> pd.DataFrame:
    """Return encounters filtered according to criteria specified in *cfg*
    Supported criteria are documented in example-task.conf.
    """

    locality = cfg.get_subconf('locality')
    l_from = date.fromisoformat(locality.get_string('from', f'{date.min}'))
    l_to = date.fromisoformat(locality.get_string('to', f'{date.max}'))
    l_name = locality.get_string('name')
    enc = enc[(enc.locality == l_name) & (enc.date.dt.date >= l_from) & (enc.date.dt.date <= l_to)]

    direction = cfg.get_string('direction', '-')
    if direction[0] == 'r':
        dirdiff = direction_difference(enc)
        enc = enc.join(dirdiff, on=['coord_x', 'coord_y'], validate='m:1')
        # drop if (forward_has_more_species) and (direction_is_b)
        enc = enc[~((enc['diff_#'] >= 0) & (enc.direction == 'b'))]
        enc = enc[~((enc['diff_#'] < 0) & (enc.direction == 'f'))]
        enc = enc.drop(['f_species', 'b_species', 'diff_%', 'diff_#'], axis='columns', errors='raise')
    elif direction[0] == 'b' or direction[0] == 'f':
        enc = enc[enc.direction == direction[0]]

    include_families = cfg.get_list('include-families', [])
    if include_families:
        enc = enc[enc.family.isin(include_families)]
    else:
        exclude_families = cfg.get_list('exclude-families', [])
        enc = enc[~enc.family.isin(exclude_families)]
    phases = cfg.get_list('exclude-phases', [])
    enc = enc[~enc.phase.isin(phases)]
    include_tiny = cfg.get_bool('include-tiny', False)
    if not include_tiny:
        enc = enc[enc.significant_size]
    use_morph = cfg.get_bool('use-morph', False)
    # backup for analyses where orig values are needed for indistinguishables
    # currently only a1
    enc['species_orig'] = enc['species']
    if use_morph:
        enc['species'] = enc['morph']

    indist_mask = enc.species.str.endswith(' sp.', na=True)
    discard_ind = cfg.get_bool('discard-indistinguishable', False)
    if discard_ind:
        enc = enc[~indist_mask]
    assert pd.api.types.is_integer_dtype(enc.coord_x)
    assert pd.api.types.is_integer_dtype(enc.coord_y)
    enc = enc.reset_index(drop=True)
    return enc


def adjust_grid(
    enc: Encounters, qlist: QList, sides: Sides, discard_transect: bool, discard_zone: bool
) -> tuple[Encounters, QList, Sides]:
    """Transform coordinates and quadrat_ids in DataFrames to reflect discarding transect
    and/or zone information if requested.

    >>> enc = pd.DataFrame(
    ...     {
    ...         'coord_x': [0, 1, 1, 1, 1],
    ...         'coord_y': [0, 0, 1, 0, 1],
    ...         'species': ['B', 'A', 'A', 'C', 'B'],
    ...         'quadrat_id': ['T_1_1', 'T_2_1', 'T_2_2', 'T_2_1', 'T_2_2'],
    ...     }
    ... )
    >>> idx = pd.MultiIndex.from_arrays([[0, 0, 1, 1, 2], [0, 1, 0, 1, 0]], names=('coord_x', 'coord_y'))
    >>> quadrats = pd.DataFrame(
    ...     index=idx,
    ...     data={
    ...         'centroid_x': [0.5, 0.5, 1.5, 1.5, 2.5],
    ...         'centroid_y': [0.5, 1.5, 0.5, 1.5, 0.5],
    ...         'quadrat_id': ['T_1_1', 'T_1_2', 'T_2_1', 'T_2_2', 'T_3_1'],
    ...     },
    ... )
    >>> sides = Sides(1, 1)
    >>> res = adjust_grid(enc.copy(), quadrats.copy(), sides, discard_transect=True, discard_zone=False)
    >>> res[0]
       coord_x  coord_y species quadrat_id
    0        0        0       B      T_1_1
    1        0        0       A      T_1_1
    2        0        1       A      T_1_2
    3        0        0       C      T_1_1
    4        0        1       B      T_1_2
    >>> res[1]  # doctest: +NORMALIZE_WHITESPACE
                     centroid_x  centroid_y quadrat_id
    coord_x coord_y
    0       0               0.5         0.5      T_1_1
            1               0.5         1.5      T_1_2
    >>> res[2]
    Sides(x=3, y=1)

    >>> res = adjust_grid(enc.copy(), quadrats.copy(), sides, discard_transect=False, discard_zone=True)
    >>> res[0]
       coord_x  coord_y species quadrat_id
    0        0        0       B      T_1_1
    1        1        0       A      T_2_1
    2        1        0       A      T_2_1
    3        1        0       C      T_2_1
    4        1        0       B      T_2_1
    >>> res[1]  # doctest: +NORMALIZE_WHITESPACE
                     centroid_x  centroid_y quadrat_id
    coord_x coord_y
    0       0               0.5         0.5      T_1_1
    1       0               1.5         0.5      T_2_1
    2       0               2.5         0.5      T_3_1
    >>> res[2]
    Sides(x=1, y=2)


    >>> res = adjust_grid(enc.copy(), quadrats.copy(), sides, discard_transect=True, discard_zone=True)
    >>> res[0]
       coord_x  coord_y species quadrat_id
    0        0        0       B      T_1_1
    1        0        0       A      T_1_1
    2        0        0       A      T_1_1
    3        0        0       C      T_1_1
    4        0        0       B      T_1_1
    >>> res[1]  # doctest: +NORMALIZE_WHITESPACE
                     centroid_x  centroid_y quadrat_id
    coord_x coord_y
    0       0               0.5         0.5      T_1_1
    >>> res[2]
    Sides(x=3, y=2)


    >>> res = adjust_grid(enc.copy(), quadrats.copy(), sides, discard_transect=False, discard_zone=False)
    >>> res[0]
       coord_x  coord_y species quadrat_id
    0        0        0       B      T_1_1
    1        1        0       A      T_2_1
    2        1        1       A      T_2_2
    3        1        0       C      T_2_1
    4        1        1       B      T_2_2
    >>> res[1]  # doctest: +NORMALIZE_WHITESPACE
                     centroid_x  centroid_y quadrat_id
    coord_x coord_y
    0       0               0.5         0.5      T_1_1
            1               0.5         1.5      T_1_2
    1       0               1.5         0.5      T_2_1
            1               1.5         1.5      T_2_2
    2       0               2.5         0.5      T_3_1
    >>> res[2]
    Sides(x=1, y=1)
    """

    new_x = sides.x
    new_y = sides.y
    if discard_transect:
        enc['coord_x'] = 0
        # replace group of digits after first underscore
        enc['quadrat_id'] = enc['quadrat_id'].str.replace(r'(^[^_])_(\d+)', r'\1_1', regex=True)
        qlist['quadrat_id'] = qlist['quadrat_id'].str.replace(r'(^[^_])_(\d+)', r'\1_1', regex=True)
        x_coords = qlist.index.get_level_values('coord_x')
        new_x = sides.x * (x_coords.max() + 1)
        qlist['centroid_x'] = sides.x / 2
    if discard_zone:
        enc['coord_y'] = 0
        # replace group of digits at the end
        enc['quadrat_id'] = enc['quadrat_id'].str.replace(r'_\d+$', '_1', regex=True)
        qlist['quadrat_id'] = qlist['quadrat_id'].str.replace(r'_\d+$', '_1', regex=True)
        y_coords = qlist.index.get_level_values('coord_y')
        new_y = sides.y * (y_coords.max() + 1)
        qlist['centroid_y'] = sides.y / 2
    qlist = qlist.drop_duplicates()  # automatically adjusts index
    return enc, qlist, Sides(new_x, new_y)


def direction_difference(enc: Encounters) -> pd.DataFrame:
    """Return dataframe with (coord_x, coord_y) as index and columns 'f_species' and 'b_species'
    describing how many species were sampled in a given direction, including absolute and
    relative differences between the two.

    >>> df = pd.DataFrame(
    ...     {
    ...         'coord_x': ['0', '0', '0', '1', '1'],
    ...         'coord_y': ['0', '0', '0', '1', '1'],
    ...         'direction': ['f', 'f', 'b', 'f', 'b'],
    ...         'species': ['A', 'B', 'A', 'B', 'B'],
    ...     }
    ... )
    >>> direction_difference(df)  # doctest: +NORMALIZE_WHITESPACE
                     f_species  b_species  diff_%  diff_#
    coord_x coord_y
    0       0                2          1     0.5       1
    1       1                1          1     0.0       0
    """
    forward = enc[enc.direction == 'f'][['coord_x', 'coord_y', 'species']]
    backward = enc[enc.direction == 'b'][['coord_x', 'coord_y', 'species']]
    f_lens = (
        forward.groupby(['coord_x', 'coord_y'])
        .nunique()
        .rename({'species': 'f_species'}, axis='columns', errors='raise')
    )
    b_lens = (
        backward.groupby(['coord_x', 'coord_y'])
        .nunique()
        .rename({'species': 'b_species'}, axis='columns', errors='raise')
    )
    stats = f_lens.join(b_lens, how='outer')
    stats['diff_%'] = (stats['f_species'] - stats['b_species']) / stats['f_species']
    stats['diff_#'] = stats['f_species'] - stats['b_species']
    return stats


def load_quadrats(qlist: Path, quadrat_types: Sequence[str]) -> QList:
    """Load CSV dataset listing all quadrats in a grid from *qlist* filtered by *quadrat_types*"""

    q_type = pd.CategoricalDtype(['normal', 'shallows', 'riptide'])
    qs = pd.read_csv(qlist, dtype={'quadrat_type': q_type}, index_col=['coord_x', 'coord_y']).convert_dtypes()
    assert pd.api.types.is_integer_dtype(qs.index.get_level_values(0))
    assert pd.api.types.is_integer_dtype(qs.index.get_level_values(1))
    qs.set_flags(allows_duplicate_labels=False)
    qs = qs[qs.quadrat_type.isin(quadrat_types)].drop(columns='quadrat_type', errors='raise')
    qs = qs.sort_index()
    return qs


def load_encounters(dataset: Path) -> Encounters:
    """Load CSV dataset with encounters from *dataset*"""

    dtype_dict = enc_dtypes()
    enc = pd.read_csv(dataset, dtype=dtype_dict, parse_dates=['date']).convert_dtypes()
    enc.set_flags(allows_duplicate_labels=False)
    return enc


def get_spp_matrix(enc: Encounters, quadrats: QList) -> SppMatrix:
    """Return DataFrame with coordinate MultiIndex labels and species as columns
    with bool denoting whether species COL was encountered in quadrat LABEL.

    >>> enc = pd.DataFrame(
    ...     {'coord_x': [0, 1, 1, 1, 1], 'coord_y': [0, 0, 1, 0, 1], 'species': ['B', 'A', 'A', 'C', 'B']}
    ... )
    >>> idx = pd.MultiIndex.from_arrays([[0, 0, 1, 1, 2], [0, 1, 0, 1, 0]], names=('coord_x', 'coord_y'))
    >>> quadrats = pd.DataFrame(index=idx)
    >>> get_spp_matrix(enc, quadrats)  # doctest: +NORMALIZE_WHITESPACE
    species              A      B      C
    coord_x coord_y
    0       0        False   True  False
            1        False  False  False
    1       0         True  False   True
            1         True   True  False
    2       0        False  False  False
    """

    enccoords = [enc.coord_x, enc.coord_y]
    spp_matrix = pd.crosstab(enccoords, columns=enc.species, dropna=False)
    spp_matrix = spp_matrix.reindex(quadrats.index).fillna(0).astype(bool)
    spp_matrix = spp_matrix.sort_index()
    return spp_matrix


def p025(x: pd.Series) -> float:
    """Return 0.25 quantile (25th percentile) of pandas Series"""
    return x.quantile(0.025)


def p975(x: pd.Series) -> float:
    """Return 0.975 quantile (97.5th percentile) of pandas Series"""
    return x.quantile(0.975)


AGG_STATS: list[str | Callable] = ['mean', 'median', 'sem', 'std', 'count', 'min', 'max', 'skew', p025, p975]
"""List with aggregation to be called at once for convenience"""


def acc_richness_shuffled(spp_matrix: pd.DataFrame) -> pd.Series:
    """Return Series containing accumulated richness.
    Quadrats are accumulated in random order.

    >>> np.random.seed(0)
    >>> spp_matrix = pd.DataFrame(
    ...     {
    ...         'A': [True, False, True, False],
    ...         'B': [True, False, False, False],
    ...         'C': [True, True, False, False],
    ...         'D': [False, False, False, False],
    ...         'E': [False, False, True, False],
    ...     }
    ... )
    >>> acc_richness_shuffled(spp_matrix)
    0    2
    1    2
    2    3
    3    4
    dtype: int64
    """

    return (
        spp_matrix.sample(frac=1, ignore_index=True)  # reshuffle dataset
        .cumsum()
        .astype(bool)
        .sum(axis='columns')  # sum total species
    )


def agg_results(df: pd.DataFrame, col_prefix: str, index_name: str) -> pd.DataFrame:
    """Aggregate data from DataFrame in a wide format

    >>> pd.set_option('display.width', None)
    >>> df = pd.DataFrame({'col1': [1, 0], 'col2': [2, 1], 'col3': [2, 2], 'col4': [1, 3]})
    >>> agg_results(df, 'col', 'idx')  # doctest: +NORMALIZE_WHITESPACE
         col_mean  col_med   col_sem   col_std  col_count  col_p025  col_p975  col_min  col_max  col_skew  col_kurtosis
    idx
    0         1.5      1.5  0.288675  0.577350          4     1.000     2.000        1        2       0.0          -6.0
    1         1.5      1.5  0.645497  1.290994          4     0.075     2.925        0        3       0.0          -1.2
    """

    res = pd.DataFrame(index=df.index)
    res.index.name = index_name
    res[f'{col_prefix}_mean'] = df.mean(axis='columns')
    res[f'{col_prefix}_med'] = df.median(axis='columns')
    res[f'{col_prefix}_sem'] = df.sem(axis='columns')
    res[f'{col_prefix}_std'] = df.std(axis='columns')
    res[f'{col_prefix}_count'] = df.count(axis='columns')
    res[f'{col_prefix}_p025'] = df.quantile(0.025, axis='columns')
    res[f'{col_prefix}_p975'] = df.quantile(0.975, axis='columns')
    res[f'{col_prefix}_min'] = df.min(axis='columns')
    res[f'{col_prefix}_max'] = df.max(axis='columns')
    res[f'{col_prefix}_skew'] = df.skew(axis='columns')
    res[f'{col_prefix}_kurtosis'] = df.kurtosis(axis='columns')
    return res


def species_delta(species: pd.DataFrame, dmat: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame containing absolute in quadrats richness.

    >>> cols = ['A', 'B', 'C', 'D', 'E']
    >>> vals = [
    ...     [True, True, True, False, False],
    ...     [True, False, True, False, False],
    ...     [False, False, False, False, True],
    ... ]
    >>> idx_spp = pd.MultiIndex.from_tuples([(0, 0), (0, 1), (1, 0)])
    >>> spp_matrix = pd.DataFrame(index=idx_spp, data=vals, columns=cols)
    >>> idx = pd.MultiIndex.from_tuples(
    ...     [
    ...         (0, 0, 0, 0),
    ...         (0, 0, 0, 1),
    ...         (0, 0, 1, 0),
    ...         (0, 1, 0, 0),
    ...         (0, 1, 0, 1),
    ...         (0, 1, 1, 0),
    ...         (1, 0, 0, 0),
    ...         (1, 0, 0, 1),
    ...         (1, 0, 1, 0),
    ...     ],
    ...     names=['coord_x', 'coord_y', 'coord_x_other', 'coord_y_other'],
    ... )
    >>> dmat = pd.DataFrame(index=idx, data={'distance': [0, 1, 1, 1, 0, 2, 1, 2, 0]})
    >>> species_delta(spp_matrix, dmat)
         distance  abs_diff
    0 0         0         0
      1         1         0
    1 0         1         1
    0 0         1         1
      1         0         0
    1 0         2         1
    0 0         1         3
      1         2         2
    1 0         0         0

    >>> vals = [
    ...     [False, False, False, False, False],
    ...     [True, False, True, False, False],
    ...     [False, False, False, False, False],
    ... ]
    >>> spp_matrix = pd.DataFrame(index=idx_spp, data=vals, columns=cols)
    >>> species_delta(spp_matrix, dmat)
         distance  abs_diff
    0 0         0         0
      1         1         2
    1 0         1         0
    0 0         1         0
      1         0         0
    1 0         2         0
    0 0         1         0
      1         2         2
    1 0         0         0
    """

    spp_diff: dict[str, list[pd.Series]] = {'distance': [], 'abs_diff': []}
    for idx, row in species.iterrows():
        abs_diffs = (species & ~row).sum(axis='columns')
        spp_diff['abs_diff'].append(abs_diffs)
        dists = dmat.loc[idx, 'distance']  # type: ignore[index]   # can be indexed by MultiIndex tuple just fine
        spp_diff['distance'].append(dists)  # type: ignore[arg-type]   # is Series, not DF, verified by assert
    res = pd.DataFrame(
        {
            'distance': pd.concat(spp_diff['distance']),
            'abs_diff': pd.concat(spp_diff['abs_diff']),
        }
    )
    return res


def distance_matrix(quadrats: pd.DataFrame, distance: DistFunction) -> pd.DataFrame:
    """Convert quadrat's grid coordinates to quadrat's centroid coordinates on a meters-based plane.

    >>> df = pd.DataFrame(
    ...     {
    ...         'quadrat_id': ['1_1', '1_2', '2_1', '2_2'],
    ...         'coord_x': [0, 0, 1, 1],
    ...         'coord_y': [0, 1, 0, 1],
    ...         'centroid_x': [0.5, 0.5, 1.5, 1.5],
    ...         'centroid_y': [0.5, 1.5, 0.5, 1.5],
    ...     }
    ... )
    >>> distance_matrix(
    ...     df, lambda a, b: q_distance_diagonal(a, b, Sides(1, 1), {'diagonal': 10})
    ... )  # doctest: +NORMALIZE_WHITESPACE
                                                 distance
    coord_x coord_y coord_x_other coord_y_other
    0       0       0             0              0.000000
                                  1              2.236068
                    1             0              2.236068
                                  1              2.828427
            1       0             0              2.236068
                                  1              0.000000
                    1             0              2.828427
                                  1              2.236068
    1       0       0             0              2.236068
                                  1              2.828427
                    1             0              0.000000
                                  1              2.236068
            1       0             0              2.828427
                                  1              2.236068
                    1             0              2.236068
                                  1              0.000000
    """

    quadrats = quadrats.reset_index(drop=True)
    dmat = quadrats.join(quadrats, how='cross', rsuffix='_other')  # type: ignore[arg-type]     # pandas bug as of 2.0.3
    dmat = dmat.set_index(['quadrat_id', 'quadrat_id_other'], verify_integrity=True)
    ps = dmat[['centroid_x', 'centroid_y']]
    qs = dmat[['centroid_x_other', 'centroid_y_other']]
    qs = qs.rename(
        columns={'centroid_x_other': 'centroid_x', 'centroid_y_other': 'centroid_y'}, errors='raise'
    )  # 'coord_x_other': 'x_g', 'coord_y_other': 'y_g',
    dmat = dmat[['coord_x', 'coord_y', 'coord_x_other', 'coord_y_other']]
    dmat['distance'] = distance(ps, qs)
    dmat = dmat.set_index(['coord_x', 'coord_y', 'coord_x_other', 'coord_y_other'])
    dmat = dmat.sort_index()
    return dmat


def q_distance_centroid(
    c_coords1: pd.DataFrame, c_coords2: pd.DataFrame, sides: Sides, caps: dict[str, float]
) -> pd.Series:
    """Return series of euclidean distance between centroids of quadrats at *c_coords1* and *c_coords2*.
    Distance is capped by *centroid* value from *caps*.

    Grid coords should be paired-up, e.g. using cross-join, beforehand.

    >>> c_coords1 = pd.DataFrame(
    ...     {
    ...         'centroid_x': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5],
    ...         'centroid_y': [0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5],
    ...     }
    ... )
    >>> c_coords2 = pd.DataFrame(
    ...     {
    ...         'centroid_x': [0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 1.5, 1.5],
    ...         'centroid_y': [0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5],
    ...     }
    ... )
    >>> q_distance_centroid(c_coords1, c_coords2, Sides(1, 1), {'centroid': 10})
    0     0.000000
    1     1.000000
    2     1.000000
    3     1.414214
    4     1.000000
    5     0.000000
    6     1.414214
    7     1.000000
    8     1.000000
    9     1.414214
    10    0.000000
    11    1.000000
    12    1.414214
    13    1.000000
    14    1.000000
    15    0.000000
    dtype: float64
    """

    dists = pd.Series(
        np.sqrt((c_coords1.centroid_x - c_coords2.centroid_x) ** 2 + (c_coords1.centroid_y - c_coords2.centroid_y) ** 2)
    )
    return dists.where(dists <= caps['centroid'], caps['centroid'])


def q_distance_collapsed(
    c_coords1: pd.DataFrame, c_coords2: pd.DataFrame, sides: Sides, caps: dict[str, float]
) -> pd.Series:
    """Return series of farthest single direction side-to-side distances between dataframes
    of points at *c_coords1* and *c_coords2*.
    Extent as per P&W paper, longest distance on 1 axis, taking larger of x or y differences.
    Distance is capped by *max1dx* value from *caps* in case x distance is taken and *max1dy* in case of y.

    Correction is applied to result to make distance of quadrat to itself 0.

    Grid coords should be paired-up, e.g. using cross-join, beforehand.

    >>> c_coords1 = pd.DataFrame(
    ...     {
    ...         'centroid_x': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5],
    ...         'centroid_y': [0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5],
    ...     }
    ... )
    >>> c_coords2 = pd.DataFrame(
    ...     {
    ...         'centroid_x': [0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 1.5, 1.5],
    ...         'centroid_y': [0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5],
    ...     }
    ... )
    >>> q_distance_collapsed(c_coords1, c_coords2, Sides(1, 1), {'max1dx': 10, 'max1dy': 10})
    0     0.0
    1     2.0
    2     2.0
    3     2.0
    4     2.0
    5     0.0
    6     2.0
    7     2.0
    8     2.0
    9     2.0
    10    0.0
    11    2.0
    12    2.0
    13    2.0
    14    2.0
    15    0.0
    Name: centroid_x, dtype: float64
    """
    x_diff = (c_coords1.centroid_x - c_coords2.centroid_x).abs()
    y_diff = (c_coords1.centroid_y - c_coords2.centroid_y).abs()
    x_diff[x_diff > 0] += sides.x
    y_diff[y_diff > 0] += sides.y
    x_diff = x_diff.where(x_diff <= caps['max1dx'], caps['max1dx'])
    y_diff = y_diff.where(y_diff <= caps['max1dy'], caps['max1dy'])
    dist = x_diff.where(x_diff > y_diff, y_diff)
    return dist


def q_distance_diagonal(
    c_coords1: pd.DataFrame, c_coords2: pd.DataFrame, sides: Sides, caps: dict[str, float]
) -> pd.Series:
    """Return series of diagonal, farthest corner-to-corner, distances between dataframes of
    points at *c_coords1* and *c_coords2*. Distance is capped by *diagonal* value
    from *caps* to prevent overspilling from grid in case of merged quadrats.

    Centroid coordinates should be paired-up beforehand, e.g. using cross join.

    >>> c_coords1 = pd.DataFrame(
    ...     {
    ...         'centroid_x': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5],
    ...         'centroid_y': [0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5],
    ...     }
    ... )
    >>> c_coords2 = pd.DataFrame(
    ...     {
    ...         'centroid_x': [0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 1.5, 1.5],
    ...         'centroid_y': [0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5],
    ...     }
    ... )
    >>> q_distance_diagonal(c_coords1, c_coords2, Sides(1, 1), {'diagonal': 10})
    0     0.000000
    1     2.236068
    2     2.236068
    3     2.828427
    4     2.236068
    5     0.000000
    6     2.828427
    7     2.236068
    8     2.236068
    9     2.828427
    10    0.000000
    11    2.236068
    12    2.828427
    13    2.236068
    14    2.236068
    15    0.000000
    dtype: float64
    >>> q_distance_diagonal(c_coords1, c_coords2, Sides(1, 1), {'diagonal': 2.5})
    0     0.000000
    1     2.236068
    2     2.236068
    3     2.500000
    4     2.236068
    5     0.000000
    6     2.500000
    7     2.236068
    8     2.236068
    9     2.500000
    10    0.000000
    11    2.236068
    12    2.500000
    13    2.236068
    14    2.236068
    15    0.000000
    dtype: float64
    """

    # "push" centroids into oposite corners
    x_dist = (c_coords1.centroid_x - c_coords2.centroid_x).abs() + sides.x
    y_dist = (c_coords1.centroid_y - c_coords2.centroid_y).abs() + sides.y
    dists_pre_sqrt = pd.Series(x_dist**2 + y_dist**2)
    quadrat_diagonal_2 = sides.x**2 + sides.y**2
    dists_pre_sqrt[dists_pre_sqrt == quadrat_diagonal_2] = 0
    dists = np.sqrt(dists_pre_sqrt)
    return dists.where(dists <= caps['diagonal'], caps['diagonal'])


def cutting_bounds(quadrats: pd.DataFrame, level: int) -> dict[Edge, int]:
    """Returns minimum and maximum coordinates to be retained when tiling subgrid with level x level tiles.
    In other words
    >>> idx = pd.MultiIndex.from_tuples(
    ...     [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (3, 0), (3, 1), (3, 2)],
    ...     names=['coord_x', 'coord_y'],
    ... )
    >>> qs = pd.DataFrame(index=idx)
    >>> cutting_bounds(qs, 1)
    {'left': 0, 'bottom': 0, 'right': 3, 'top': 2}
    >>> cutting_bounds(qs, 2)
    {'left': 0, 'bottom': 1, 'right': 3, 'top': 1}
    >>> cutting_bounds(qs, 3)
    {'left': 1, 'bottom': 0, 'right': 2, 'top': 2}
    >>> cutting_bounds(qs, 4)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TilingError: Requested level 4 incompatible with locality dimensions: 3 x 2
    """

    xmax = quadrats.index.get_level_values('coord_x').max()
    ymax = quadrats.index.get_level_values('coord_y').max()
    if (level > xmax + 1) or (level > ymax + 1):
        raise TilingError(level, Sides(xmax, ymax))
    xmin_cutoff = (xmax + 1) % level
    ymin_cutoff = (ymax + 1) % level
    xmax_cutoff = xmax - xmin_cutoff
    ymax_cutoff = ymax - ymin_cutoff
    return {'left': xmin_cutoff, 'bottom': ymin_cutoff, 'right': xmax_cutoff, 'top': ymax_cutoff}


def get_shift_tuples(qlist_subgrid: list[QList]) -> list[tuple[int, int]]:
    """Get a list containing tuples indicating by how many coordinates will
    grids need to be shifted to start at (0, 0). In other words, tuples with
    minimal coordinates on each axis.

    >>> df0 = pd.DataFrame(index=pd.MultiIndex.from_arrays([[0, 0, 1, 1], [0, 1, 0, 1]], names=('coord_x', 'coord_y')))
    >>> df1 = pd.DataFrame(index=pd.MultiIndex.from_arrays([[1, 1, 2, 2], [2, 3, 2, 3]], names=('coord_x', 'coord_y')))
    >>> get_shift_tuples([df0, df1])
    [(0, 0), (1, 2)]
    """
    shifts = []
    for subgrid in qlist_subgrid:
        shift_x = subgrid.index.get_level_values('coord_x').min()
        shift_y = subgrid.index.get_level_values('coord_y').min()
        shifts.append((shift_x, shift_y))
    return shifts


def shift_coords(df_subgrids: list[pd.DataFrame], shifts: list[tuple[int, int]], level: int) -> list[pd.DataFrame]:
    """Shift (x, y) coordinates in cropped grids from *df_subgrids* to create proper subgrids of corresponding *level*.
    The subgrids will start at (0, 0). Adjacent quadrats will be merged to create larger *level*x*level* quadrats.

    If quadrat list is passed (has coords as indices), duplicates will be dropped.

    >>> df0 = pd.DataFrame(
    ...     {
    ...         'quadrat_id': ['P_1_date_1', 'P_1_date_2', 'P_2_date_1', 'P_2_date_2'],
    ...         'coord_x': [0, 0, 1, 1],
    ...         'coord_y': [0, 1, 0, 1],
    ...     }
    ... )
    >>> res = shift_coords([df0], [(0, 0)], 1)
    >>> len(res)
    1
    >>> res[0]
      quadrat_id  coord_x  coord_y
    0      P_1_1        0        0
    1      P_1_2        0        1
    2      P_2_1        1        0
    3      P_2_2        1        1
    >>> df1 = pd.DataFrame(
    ...     data={
    ...         'quadrat_id': ['P_1_date_2', 'P_1_date_3', 'P_2_date_2', 'P_2_date_3'],
    ...         'coord_x': [0, 0, 1, 1],
    ...         'coord_y': [1, 2, 1, 2],
    ...     }
    ... )
    >>> res = shift_coords([df0, df1], [(0, 0), (0, 1)], 2)
    >>> len(res)
    2
    >>> res[0]
      quadrat_id  coord_x  coord_y
    0      P_1_1        0        0
    1      P_1_1        0        0
    2      P_1_1        0        0
    3      P_1_1        0        0
    >>> res[1]
      quadrat_id  coord_x  coord_y
    0      P_1_1        0        0
    1      P_1_1        0        0
    2      P_1_1        0        0
    3      P_1_1        0        0
    >>> coords_idx = pd.MultiIndex.from_arrays([[0, 0, 1, 1], [1, 2, 1, 2]], names=('coord_x', 'coord_y'))
    >>> df2 = df1.copy().set_index(coords_idx, verify_integrity=True)
    >>> res = shift_coords([df2], [(0, 1)], 2)
    >>> res[0]  # doctest: +NORMALIZE_WHITESPACE
                    quadrat_id  coord_x  coord_y
    coord_x coord_y
    0       0            P_1_1        0        0
    """

    res = []
    for subgrid, shift in zip(df_subgrids, shifts, strict=True):
        new_xs = subgrid.coord_x.sub(shift[0]).floordiv(level)
        new_ys = subgrid.coord_y.sub(shift[1]).floordiv(level)
        subgrid = replace_coords(subgrid, {'coord_x': new_xs, 'coord_y': new_ys})
        if 'coord_x' in subgrid.index.names:  # is qlist
            subgrid = subgrid.drop_duplicates(subset=['coord_x', 'coord_y'])
            # fix up out-of-sync coords after drop
            subgrid = subgrid.set_index(['coord_x', 'coord_y'], drop=False, verify_integrity=True)
        res.append(subgrid)
    return res


def create_subgrids(df: pd.DataFrame, cutoffs: Mapping[Edge, int]) -> list[pd.DataFrame]:
    """Create up to 4 subgrids by cutting off transects/zones beyond cutoff from either side.

    >>> idx = pd.MultiIndex.from_tuples(
    ...     [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (3, 0), (3, 1), (3, 2)],
    ...     names=['coord_x', 'coord_y'],
    ... )
    >>> df = pd.DataFrame(
    ...     index=idx,
    ...     data={
    ...         'quadrat_id': [
    ...             'P_1_25/2/2022_1',
    ...             'P_1_25/2/2022_2',
    ...             'P_1_25/2/2022_3',
    ...             'P_2_25/2/2022_1',
    ...             'P_2_25/2/2022_2',
    ...             'P_2_26/2/2022_3',
    ...             'P_3_26/2/2022_1',
    ...             'P_3_26/2/2022_2',
    ...             'P_3_26/2/2022_3',
    ...             'P_4_26/2/2022_1',
    ...             'P_4_26/2/2022_2',
    ...             'P_4_26/2/2022_3',
    ...         ]
    ...     },
    ... )
    >>> res = create_subgrids(df, {'left': 0, 'bottom': 0, 'right': 3, 'top': 2})
    >>> len(res)
    1
    >>> res[0]  # doctest: +NORMALIZE_WHITESPACE
                          quadrat_id
    coord_x coord_y
    0       0        P_1_25/2/2022_1
            1        P_1_25/2/2022_2
            2        P_1_25/2/2022_3
    1       0        P_2_25/2/2022_1
            1        P_2_25/2/2022_2
            2        P_2_26/2/2022_3
    2       0        P_3_26/2/2022_1
            1        P_3_26/2/2022_2
            2        P_3_26/2/2022_3
    3       0        P_4_26/2/2022_1
            1        P_4_26/2/2022_2
            2        P_4_26/2/2022_3
    """

    if not set(['coord_x', 'coord_y']).issubset(df.columns):
        coord_x = df.index.get_level_values('coord_x')
        coord_y = df.index.get_level_values('coord_y')
    else:
        coord_x = df['coord_x'] # type: ignore[assignment]  # behaves the same for our purposes
        coord_y = df['coord_y'] # type: ignore[assignment]  # behaves the same for our purposes
    left_part = (coord_x <= cutoffs['right'])
    bottom_part = (coord_y <= cutoffs['top'])
    right_part = (coord_x >= cutoffs['left'])
    top_part = (coord_y >= cutoffs['bottom'])

    df0 = df[bottom_part & left_part]
    df1 = df[bottom_part & right_part]
    df2 = df[top_part & left_part]
    df3 = df[top_part & right_part]

    res: list[pd.DataFrame] = []
    for d in [df0, df1, df2, df3]:
        df_is_in = is_in(res, d)
        if not df_is_in:
            res.append(d)
    return res


def is_in(dfs: list[pd.DataFrame], maybe_duplicate: pd.DataFrame) -> bool:
    """Checks whether *maybe_duplicate* DataFrame is already in *dfs* list

    >>> dfs = [pd.DataFrame({'vals': [0, 1, 2, 3]}), pd.DataFrame({'vals': [1, 2, 3]})]
    >>> is_in(dfs, pd.DataFrame({'vals': [1, 2, 3, 4]}))
    False
    >>> is_in(dfs, pd.DataFrame({'vals': [1, 2, 3]}))
    True
    >>> is_in(dfs, pd.DataFrame({'values': [0, 1, 2, 3]}))
    False
    """

    for df in dfs:
        if maybe_duplicate.equals(df):
            return True
    return False
