import argparse
import datetime
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import random
import seaborn as sns

from alive_progress import alive_bar
from alive_progress.animations.spinners import bouncing_spinner_factory
from matplotlib.ticker import ScalarFormatter
from pathlib import Path
from typing import Final, Generator, Literal, Optional

import seal.config as conf
from seal.common import analysis_results_name, data_dir, Sides


type Metadata = dict[str, str | list[str] | None]

SVG_METADATA: Final[Metadata] = {
    'Description': (
        'Work was funded by project Influence of sample grain'
        ' and extent on coral reef fish richness, MUNI / IGA / 1076 / 2021.'
    ),
    'Contributor': ['Martin Matouš', 'Barbora Winterová'],
    'Coverage': None,
    'Keywords': None,
    'Language': 'en',
    'Publisher': 'Department of Botany and Zoology, Faculty of Science, Masaryk University',
    # 'Relation': DOI of published paper
    'Rights': 'CC BY-SA 4.0',
    'Title': None,
}

ADD_PNG_METADATA: Final[Metadata] = {
    'Copyright': 'CC BY-SA 4.0',
    'Creation Time': None,
    'Software': 'seal (https://pypi.org/project/seal-tool/)',
}


def main(args: argparse.Namespace) -> int:
    sns.set_theme(palette='colorblind')
    cfg = conf.Config.from_file(args.taskfile)
    locality = cfg.get_subconf('locality')

    if args.joined:
        atype = args.joined[0]
        joined_input = Path(args.joined[1])
        analysis = config_analysis(atype, cfg)
        df = pd.read_csv(joined_input)
        fig, meta = plot_analysis(df, locality, analysis)
        out_path = joined_input.with_stem(joined_input.stem + f'-{atype}').with_suffix('.svg')
        fig.savefig(out_path, metadata=meta)
        print(f'Graph plotted at {out_path}')
        return 0

    analyses = cfg.get_list('analyses')
    csv_results_dir = data_dir(cfg)

    emoji = ['🐧', '🐡', '🐟', '🦑', '🦦', '🐠', '🦐', '🐙']
    random.shuffle(emoji)
    emoji = ''.join(emoji)
    spinner = bouncing_spinner_factory(('🌊', emoji), 6, block=(1, 1), hide=True)

    with alive_bar(len(analyses), title='Plotting', spinner=spinner) as bar:
        for pos, analysis in enumerate(analyses):
            if not (isinstance(analysis, str) or isinstance(analysis, conf.Config)):
                raise conf.InvalidTaskError(f'invalid analysis {analysis} on position {pos}')
            analysis = config_analysis(analysis, cfg)
            a_type = analysis.get_string('type')
            analysis_file = analysis_results_name(csv_results_dir, args, a_type)
            df = pd.read_csv(analysis_file)
            figs, meta = plot_analysis(df, locality, analysis)
            if args.png:
                suffix = '.png'
                meta = conv_png_metadata(meta)
            else:
                suffix = '.svg'
            out_path = analysis_file.with_suffix(suffix)
            for i, fig in enumerate(figs):
                out_path = out_path.with_stem(f'{analysis_file.stem}-{i}')
                fig.savefig(out_path, metadata=meta)
                print(f'Graph plotted at {out_path}')
            bar.text(f'{a_type}')
            bar()

    return 0


def plot_analysis(df, locality, analysis):
    match analysis.get_string('type'):
        case 'a1' | 'overview':
            return a1(df, locality, analysis)
        case 'a2' | 'sar':
            return a2(df, locality, analysis)
        case 'a3' | 'spdiff':
            return a3(df, locality, analysis)
        case 'a4' | 'rrich':
            return a4(df, locality, analysis)
        case 'a5' | 'oerich':
            return a5(df, locality, analysis)
        case 'a6' | 'sratios':
            return a6(df, locality, analysis)
        case 'a7' | 'jaccard':
            return a7(df, locality, analysis)
        case _:
            raise conf.InvalidTaskError(analysis.get_string('type'))


def config_analysis(analysis: conf.Config | str, taskfile: conf.Config) -> conf.Config:
    analysis = conf.Config.from_string(f'type = {analysis}') if isinstance(analysis, str) else analysis
    analysis.put('plot', taskfile.get_subconf('plot'))
    analysis.put('seed', taskfile.get_int_unchecked('seed', None))
    analysis.put('level-strategy', taskfile.get_string('level-strategy'))
    return analysis


def level_aspect(sides: Sides, level: int, lvl_strat: str) -> float:
    if (
        lvl_strat == 'transect-merging'
        or lvl_strat == 'repeated-transect-merging'
        or lvl_strat == 'striped-transect-merging'
    ):
        return sides.y / (sides.x * level)
    elif lvl_strat == 'zone-merging':
        return sides.y * level / sides.x
    elif (
        lvl_strat == 'overlaid-subgrids'
        or lvl_strat == 'transect-additive'
        or lvl_strat == 'zone-additive'
        or lvl_strat == 'nested-quadrats'
    ):
        return sides.y / sides.x
    raise conf.InvalidTaskError(lvl_strat)


def a1(df: pd.DataFrame, locality: conf.Config, analysis: conf.Config) -> tuple[list[matplotlib.figure.Figure], Metadata]:
    locname = locality.get_string('name')
    meta = fill_metadata(locname, 'a1')
    s = locality.get_subconf('sides')
    sides = Sides(s.get_float('x'), s.get_float('y'))
    lvl_strat = analysis.get_string('level-strategy')

    figs = []
    for ldf, level in df_levels(df):
        ldf = ldf.astype(int)

        fig, ax = plt.subplots(figsize=(12, 12))
        fig.suptitle(f'{locname} species')

        val_matrix = ldf.pivot(index='coord_y', columns='coord_x', values='n_species')
        val_matrix.sort_index(ascending=False, inplace=True)

        aspect = level_aspect(sides, level, lvl_strat)
        sns.heatmap(val_matrix, annot=True, fmt='g', cmap='magma_r', linewidths=0.3, ax=ax)
        ax.grid(False)
        ax.set(xlabel='Transect', ylabel='Zone', aspect=aspect, title=f'Level {level}')
        fig.text(x=0.7, y=0.05, s=f'Level strategy: {lvl_strat}')
        figs.append(fig)

        fig, ax = plt.subplots(figsize=(12, 12))
        fig.suptitle(f'{locname} individuals')

        val_matrix = ldf.pivot(index='coord_y', columns='coord_x', values='n_individuals')
        val_matrix.sort_index(ascending=False, inplace=True)

        aspect = level_aspect(sides, level, lvl_strat)
        sns.heatmap(val_matrix, annot=True, fmt='g', cmap='magma_r', linewidths=0.3, ax=ax)
        ax.grid(False)
        ax.set(xlabel='Transect', ylabel='Zone', aspect=aspect, title=f'Level {level}')
        fig.text(x=0.7, y=0.05, s=f'Level strategy: {lvl_strat}')
        figs.append(fig)

    return figs, meta


def a2(df: pd.DataFrame, locality: conf.Config, analysis: conf.Config) -> tuple[list[matplotlib.figure.Figure], Metadata]:
    locname = locality.get_string('name')
    meta = fill_metadata(locname, 'a2')
    ycol = 'species'
    seed = analysis.get_int_unchecked('seed')
    plotconf = analysis.get('plot')
    err_style = plotconf.get_string('error-style', 'band')  # type: ignore[union-attr]   # todo: switch to loading params once in main

    init_df = df.copy()
    df = df.drop(['min_acc', 'max_acc'], axis='columns', errors='raise')
    df['id'] = range(len(df))
    df = pd.wide_to_long(df, stubnames='', i=['id'], j='area').rename({'': ycol}, axis='columns', errors='raise')

    fig1, ax1 = plt.subplots()

    sns.lineplot(
        x='area',
        y=ycol,
        hue='level',
        seed=seed,
        estimator='mean',
        err_style=err_style,
        ax=ax1,
        data=df,
        palette='colorblind',
    )
    ax1.set(xlabel='Surface area ($m^2$)', ylabel='# of species', title='Species-area relationship')

    fig2, ax2 = plt.subplots()
    sns.lineplot(
        x='area',
        y='min_acc',
        hue='level',
        seed=seed,
        estimator='mean',
        err_style=None,
        data=init_df,
        ax=ax2,
        legend=False,
        palette='colorblind',
    )
    sns.lineplot(
        x='area',
        y='max_acc',
        hue='level',
        seed=seed,
        estimator='mean',
        err_style=None,
        data=init_df,
        ax=ax2,
        palette='colorblind',
    )
    ax2.set(xlabel='Surface area ($m^2$)', ylabel='# of species', title='Species-area relationship extremes')

    if plotconf.get_bool('logscale-x'):   # type: ignore[union-attr]   # todo: switch to loading params once in main
        for ax in [ax1, ax2]:
            ax.set_xscale('log')
            ax.xaxis.set_major_formatter(ScalarFormatter())

    return [fig1, fig2], meta


def a3(df: pd.DataFrame, locality: conf.Config, analysis: conf.Config) -> tuple[list[matplotlib.figure.Figure], Metadata]:
    locname = locality.get_string('name')
    meta = fill_metadata(locname, 'a3')
    seed = analysis.get_int_unchecked('seed')

    interval = analysis.get_float_unchecked('interval', None)
    if interval:
        bins = pd.interval_range(0, df.distance.max() + interval, freq=interval, closed='left')  # type: ignore[call-overload]
        df['distance_bin'] = pd.cut(df.distance, bins)

    plotconf = analysis.get('plot')
    err_style = plotconf.get_string('error-style', 'band')  # type: ignore[union-attr]   # todo: switch to loading params once in main
    figs = []
    axs = []

    fig1, ax1 = plt.subplots()
    fig1.suptitle('Pair-wise species difference')
    sns.lineplot(
        x='distance',
        y='abs_diff',
        hue='level',
        seed=seed,
        estimator='mean',
        err_style=err_style,
        ax=ax1,
        data=df,
        palette='colorblind',
    )
    figs.append(fig1)
    axs.append(ax1)

    if 'distance_bin' in df.columns:
        fig2, ax2 = plt.subplots(figsize=(20, 20))
        fig2.suptitle('Pair-wise species difference')
        sns.boxplot(x='distance_bin', y='abs_diff', hue='level', ax=ax2, data=df, palette='colorblind')
        plt.setp(ax2.collections, alpha=0.3)
        sns.rugplot(y='abs_diff', hue='level', ax=ax2, data=df, palette='colorblind')
        ax2.tick_params(axis='x', labelrotation=45)
        figs.append(fig2)
        axs.append(ax2)

    for ax in axs:
        ax.set(xlabel='Distance ($m$)', ylabel='Difference', title=locname)

    return figs, meta


def a4(df: pd.DataFrame, locality: conf.Config, analysis: conf.Config) -> tuple[list[matplotlib.figure.Figure], Metadata]:
    locname = locality.get_string('name')
    meta = fill_metadata(locname, 'a4')
    seed = analysis.get_int_unchecked('seed')

    # intervals are simply strings to seaborn, can't be sorted automatically
    df['distance'] = df['distance'].apply(to_interval)
    df = df.sort_values('distance')
    df['distance'] = df.distance.apply(str)

    fig1, ax1 = plt.subplots(figsize=(20, 20))
    fig1.suptitle('Richness of quadrats within distance')
    sns.boxplot(x='distance', y='radius_richness', hue='level', ax=ax1, data=df, palette='colorblind')

    fig2, ax2 = plt.subplots(figsize=(20, 20))
    fig2.suptitle('Richness of quadrats within distance')
    plotconf = analysis.get('plot')
    err_style = plotconf.get_string('error-style', 'band')  # type: ignore[union-attr]   # todo: switch to loading params once in main
    sns.lineplot(
        x='distance',
        y='radius_richness',
        seed=seed,
        estimator='median',
        err_style=err_style,
        hue='level',
        ax=ax2,
        data=df,
        palette='colorblind',
    )

    for ax in [ax1, ax2]:
        ax.set(title=locname, xlabel=r'Radius ($m$)', ylabel='# of species')
        ax.tick_params(axis='x', labelrotation=45)

    return [fig1, fig2], meta


def a5(
    df: pd.DataFrame, locality: conf.Config, analysis: conf.Config
) -> tuple[list[matplotlib.figure.Figure], Metadata]:
    ratios = []
    for ldf, lvl in df_levels(df):
        ratios.append(pd.DataFrame({'oe_ratio': ldf['oe_ratio_mean'], 'level': lvl}))
    df = pd.concat(ratios, ignore_index=True)

    locname = locality.get_string('name')
    meta = fill_metadata(locname, 'a5')

    fig1, ax1 = plt.subplots()
    fig1.suptitle('Observed/expected ratio per level')
    sns.violinplot(x='level', y='oe_ratio', ax=ax1, data=df)
    plt.setp(ax1.collections, alpha=0.3)
    sns.rugplot(y='oe_ratio', ax=ax1, data=df)
    ax1.set(title=locname, xlabel='Level', ylabel='Observed/Expected')

    fig2, ax2 = plt.subplots()
    fig1.suptitle('Observed/expected ratio per level')
    sns.boxplot(x='level', y='oe_ratio', ax=ax2, data=df)
    sns.stripplot(x='level', y='oe_ratio', ax=ax2, data=df)
    ax2.set(title=locname, xlabel='Level', ylabel='Observed/Expected')

    return [fig1, fig2], meta


def a6(
    df: pd.DataFrame, locality: conf.Config, analysis: conf.Config
) -> tuple[list[matplotlib.figure.Figure], Metadata]:
    locname = locality.get_string('name')
    meta = fill_metadata(locname, 'a6')
    seed = analysis.get_int_unchecked('seed')

    cfgs = [
        {'ycol': 'common_total', 'title': f'{locname}, common / total species ratio', 'ylabel': 'common / total'},
        {
            'ycol': 'common_diff',
            'title': f'{locname}, common / differing species ratio',
            'ylabel': 'common / differing',
        },
        {'ycol': 'common_union', 'title': f'{locname}, common / present species ratio', 'ylabel': 'common / present'},
    ]

    plotconf = analysis.get('plot')
    err_style = plotconf.get_string('error-style', 'band')  # type: ignore[union-attr]   # todo: switch to loading params once in main
    figs = []
    for cfg in cfgs:
        fig, ax = plt.subplots()
        sns.lineplot(
            x='distance',
            y=cfg['ycol'],
            seed=seed,
            estimator='mean',
            err_style=err_style,
            hue='level',
            data=df,
            palette='colorblind',
            ax=ax,
        )
        ax.set(title=cfg['title'], xlabel=r'Quadrat distance ($m$)', ylabel=cfg['ylabel'])
        figs.append(fig)

    return figs, meta


def a7(
    df: pd.DataFrame, locality: conf.Config, analysis: conf.Config
) -> tuple[list[matplotlib.figure.Figure], Metadata]:
    locname = locality.get_string('name')
    meta = fill_metadata(locname, 'a7')
    seed = analysis.get_int_unchecked('seed')

    plotconf = analysis.get('plot')
    err_style = plotconf.get_string('error-style', 'band')  # type: ignore[union-attr]   # todo: switch to loading params once in main
    fig, ax = plt.subplots()
    sns.lineplot(
        x='distance',
        y='jaccard_dissimilarity',
        seed=seed,
        estimator='mean',
        err_style=err_style,
        hue='level',
        data=df,
        palette='colorblind',
        ax=ax,
    )
    fig.suptitle('Jaccard dissimilarity / distance')
    ax.set(title=locname, xlabel=r'Quadrat distance ($m$)', ylabel='Jaccard dissimilarity')

    return [fig], meta


def df_levels(df: pd.DataFrame) -> Generator[tuple[pd.DataFrame, int], None, None]:
    levels = df['level'].unique()
    for level in sorted(levels):
        ldf = df[df.level == level]
        yield (ldf, level)


def to_interval(intr: str):
    closed = (intr[0] == '[', intr[-1] == ']')
    cl_type: Literal['left', 'right', 'both', 'neither']
    match closed:
        case (True, False):
            cl_type = 'left'
        case (False, True):
            cl_type = 'right'
        case (True, True):
            cl_type = 'both'
        case (False, False):
            cl_type = 'neither'
    left, right = map(float, intr[1:-1].split(','))
    return pd.Interval(left, right, cl_type)


def fill_metadata(title: str, analysis: str, locname: Optional[str] = None) -> Metadata:
    if locname is None:
        locname = title
    metadata = SVG_METADATA.copy()
    metadata['Coverage'] = locname
    per_analysis_kw = {
        'a1': ['overview', 'species', 'quadrat', 'transect', 'species richness'],
        'a2': ['species area relationship', 'species', 'area'],
        'a3': ['pairwise difference', 'distance', 'distance decay'],
        'a4': ['species', 'sum', 'radius'],
        'a5': ['expected species richness', 'observed/expected'],
        'a6': ['species', 'shared species', 'different specied', 'distance decay', 'common/total', 'common/differing'],
        'a7': ['jaccard dissimilarity', 'jaccard', 'distance decay'],
    }
    kws = ['marine', 'ecology', locname] + per_analysis_kw[analysis]
    metadata['Keywords'] = list(sorted(kws))
    metadata['Title'] = title
    return metadata


def conv_png_metadata(metadata: Metadata) -> Metadata:
    for key, val in ADD_PNG_METADATA.items():
        metadata[key] = val
    # vals must be latin1-encodable, convert lists to strs
    metadata['Keywords'] = ', '.join(metadata['Keywords'])  # type: ignore[arg-type]
    metadata['Contributor'] = ', '.join(metadata['Contributor'])    # type: ignore[arg-type]
    metadata['Creation Time'] = datetime.datetime.now().astimezone().isoformat()
    del metadata['Rights']  # PNG has "Copyright"
    return metadata
