# typings
from typing import Union, Optional, Sequence, Tuple, Mapping, Literal

from anndata import AnnData
from scanpy import logging as logg
from scanpy.plotting._anndata import _prepare_dataframe, _reorder_categories_after_dendrogram

_Basis = Literal['pca', 'tsne', 'umap', 'diffmap', 'draw_graph_fr']
_VarNames = Union[str, Sequence[str]]


def heatmap(
        adata: AnnData,
        var_names: Union[_VarNames, Mapping[str, _VarNames]],
        groupby: Optional[str] = None,
        use_raw: Optional[bool] = None,
        log: bool = False,
        num_categories: int = 7,
        dendrogram: Union[bool, str] = False,
        gene_symbols: Optional[str] = None,
        var_group_positions: Optional[Sequence[Tuple[int, int]]] = None,
        var_group_labels: Optional[Sequence[str]] = None,
        var_group_rotation: Optional[float] = None,
        layer: Optional[str] = None,
        standard_scale: Optional[Literal['var', 'obs']] = None,
        swap_axes: bool = False,
        show_gene_labels: Optional[bool] = None,
        show: Optional[bool] = None,
        save: Union[str, bool, None] = None,
        figsize: Optional[Tuple[float, float]] = None,
        **kwds,
):
    if use_raw is None and adata.raw is not None:
        use_raw = True

    var_names, var_group_labels, var_group_positions = _check_var_names_type(
        var_names, var_group_labels, var_group_positions
    )

    categories, obs_tidy = _prepare_dataframe(
        adata,
        var_names,
        groupby,
        use_raw,
        log,
        num_categories,
        gene_symbols=gene_symbols,
        layer=layer,
    )

    if standard_scale == 'obs':
        obs_tidy = obs_tidy.sub(obs_tidy.min(1), axis=0)
        obs_tidy = obs_tidy.div(obs_tidy.max(1), axis=0).fillna(0)
    elif standard_scale == 'var':
        obs_tidy -= obs_tidy.min(0)
        obs_tidy = (obs_tidy / obs_tidy.max(0)).fillna(0)
    elif standard_scale is None:
        pass
    else:
        logg.warning('Unknown type for standard_scale, ignored')

    if groupby is None or len(categories) <= 1:
        categorical = False
        # dendrogram can only be computed  between groupby categories
        dendrogram = False
    else:
        categorical = True
        # get categories colors:
        if groupby + "_colors" in adata.uns:
            groupby_colors = adata.uns[groupby + "_colors"]
        else:
            groupby_colors = None

    if dendrogram:
        dendro_data = _reorder_categories_after_dendrogram(
            adata,
            groupby,
            dendrogram,
            var_names=var_names,
            var_group_labels=var_group_labels,
            var_group_positions=var_group_positions,
        )

        var_group_labels = dendro_data['var_group_labels']
        var_group_positions = dendro_data['var_group_positions']

        # reorder obs_tidy
        if dendro_data['var_names_idx_ordered'] is not None:
            obs_tidy = obs_tidy.iloc[:, dendro_data['var_names_idx_ordered']]
            var_names = [var_names[x] for x in dendro_data['var_names_idx_ordered']]

        obs_tidy.index = obs_tidy.index.reorder_categories(
            [categories[x] for x in dendro_data['categories_idx_ordered']],
            ordered=True,
        )

        # reorder groupby colors
        if groupby_colors is not None:
            groupby_colors = [
                groupby_colors[x] for x in dendro_data['categories_idx_ordered']
            ]

    if show_gene_labels is None:
        if len(var_names) <= 50:
            show_gene_labels = True
        else:
            show_gene_labels = False
            logg.warning(
                'Gene labels are not shown when more than 50 genes are visualized. '
                'To show gene labels set `show_gene_labels=True`'
            )
    if categorical:
        obs_tidy = obs_tidy.sort_index()

    colorbar_width = 0.2

    if not swap_axes:
        # define a layout of 2 rows x 4 columns
        # first row is for 'brackets' (if no brackets needed, the height of this row is zero)
        # second row is for main content. This second row is divided into three axes:
        #   first ax is for the categories defined by `groupby`
        #   second ax is for the heatmap
        #   third ax is for the dendrogram
        #   fourth ax is for colorbar

        dendro_width = 1 if dendrogram else 0
        groupby_width = 0.2 if categorical else 0
        if figsize is None:
            height = 6
            if show_gene_labels:
                heatmap_width = len(var_names) * 0.3
            else:
                heatmap_width = 8
            width = heatmap_width + dendro_width + groupby_width
        else:
            width, height = figsize
            heatmap_width = width - (dendro_width + groupby_width)

        if var_group_positions is not None and len(var_group_positions) > 0:
            # add some space in case 'brackets' want to be plotted on top of the image
            height_ratios = [0.15, height]
        else:
            height_ratios = [0, height]

        width_ratios = [
            groupby_width,
            heatmap_width,
            dendro_width,
            colorbar_width,
        ]
        fig = pl.figure(figsize=(width, height))

        axs = gridspec.GridSpec(
            nrows=2,
            ncols=4,
            width_ratios=width_ratios,
            wspace=0.15 / width,
            hspace=0.13 / height,
            height_ratios=height_ratios,
        )

        heatmap_ax = fig.add_subplot(axs[1, 1])
        im = heatmap_ax.imshow(obs_tidy.values, aspect='auto', **kwds)
        heatmap_ax.set_ylim(obs_tidy.shape[0] - 0.5, -0.5)
        heatmap_ax.set_xlim(-0.5, obs_tidy.shape[1] - 0.5)
        heatmap_ax.tick_params(axis='y', left=False, labelleft=False)
        heatmap_ax.set_ylabel('')
        heatmap_ax.grid(False)

        # sns.heatmap(obs_tidy, yticklabels="auto", ax=heatmap_ax, cbar_ax=heatmap_cbar_ax, **kwds)
        if show_gene_labels:
            heatmap_ax.tick_params(axis='x', labelsize='small')
            heatmap_ax.set_xticks(np.arange(len(var_names)))
            heatmap_ax.set_xticklabels(var_names, rotation=90)
        else:
            heatmap_ax.tick_params(axis='x', labelbottom=False, bottom=False)

        # plot colorbar
        _plot_colorbar(im, fig, axs[1, 3])

        if categorical:
            groupby_ax = fig.add_subplot(axs[1, 0])
            ticks, labels, groupby_cmap, norm = _plot_categories_as_colorblocks(
                groupby_ax, obs_tidy, colors=groupby_colors, orientation='left'
            )

            # add lines to main heatmap
            line_positions = (
                    np.cumsum(obs_tidy.index.value_counts(sort=False))[:-1] - 0.5
            )
            heatmap_ax.hlines(
                line_positions,
                -0.73,
                len(var_names) - 0.5,
                lw=0.6,
                zorder=10,
                clip_on=False,
            )

        if dendrogram:
            dendro_ax = fig.add_subplot(axs[1, 2], sharey=heatmap_ax)
            _plot_dendrogram(
                dendro_ax, adata, groupby, ticks=ticks, dendrogram_key=dendrogram,
            )

        # plot group legends on top of heatmap_ax (if given)
        if var_group_positions is not None and len(var_group_positions) > 0:
            gene_groups_ax = fig.add_subplot(axs[0, 1], sharex=heatmap_ax)
            _plot_gene_groups_brackets(
                gene_groups_ax,
                group_positions=var_group_positions,
                group_labels=var_group_labels,
                rotation=var_group_rotation,
                left_adjustment=-0.3,
                right_adjustment=0.3,
            )

    # swap axes case
    else:
        # define a layout of 3 rows x 3 columns
        # The first row is for the dendrogram (if not dendrogram height is zero)
        # second row is for main content. This col is divided into three axes:
        #   first ax is for the heatmap
        #   second ax is for 'brackets' if any (othwerise width is zero)
        #   third ax is for colorbar

        dendro_height = 0.8 if dendrogram else 0
        groupby_height = 0.13 if categorical else 0
        if figsize is None:
            if show_gene_labels:
                heatmap_height = len(var_names) * 0.18
            else:
                heatmap_height = 4
            width = 10
            height = heatmap_height + dendro_height + groupby_height
        else:
            width, height = figsize
            heatmap_height = height - (dendro_height + groupby_height)

        height_ratios = [dendro_height, heatmap_height, groupby_height]

        if var_group_positions is not None and len(var_group_positions) > 0:
            # add some space in case 'brackets' want to be plotted on top of the image
            width_ratios = [width, 0.14, colorbar_width]
        else:
            width_ratios = [width, 0, colorbar_width]

        fig = pl.figure(figsize=(width, height))
        axs = gridspec.GridSpec(
            nrows=3,
            ncols=3,
            wspace=0.25 / width,
            hspace=0.3 / height,
            width_ratios=width_ratios,
            height_ratios=height_ratios,
        )

        # plot heatmap
        heatmap_ax = fig.add_subplot(axs[1, 0])

        im = heatmap_ax.imshow(obs_tidy.T.values, aspect='auto', **kwds)
        heatmap_ax.set_xlim(0, obs_tidy.shape[0])
        heatmap_ax.set_ylim(obs_tidy.shape[1] - 0.5, -0.5)
        heatmap_ax.tick_params(axis='x', bottom=False, labelbottom=False)
        heatmap_ax.set_xlabel('')
        heatmap_ax.grid(False)
        if show_gene_labels:
            heatmap_ax.tick_params(axis='y', labelsize='small', length=1)
            heatmap_ax.set_yticks(np.arange(len(var_names)))
            heatmap_ax.set_yticklabels(var_names, rotation=0)
        else:
            heatmap_ax.tick_params(axis='y', labelleft=False, left=False)

        if categorical:
            groupby_ax = fig.add_subplot(axs[2, 0])
            ticks, labels, groupby_cmap, norm = _plot_categories_as_colorblocks(
                groupby_ax, obs_tidy, colors=groupby_colors, orientation='bottom',
            )
            # add lines to main heatmap
            line_positions = (
                    np.cumsum(obs_tidy.index.value_counts(sort=False))[:-1] - 0.5
            )
            heatmap_ax.vlines(
                line_positions,
                -0.5,
                len(var_names) + 0.35,
                lw=0.6,
                zorder=10,
                clip_on=False,
            )

        if dendrogram:
            dendro_ax = fig.add_subplot(axs[0, 0], sharex=heatmap_ax)
            _plot_dendrogram(
                dendro_ax,
                adata,
                groupby,
                dendrogram_key=dendrogram,
                ticks=ticks,
                orientation='top',
            )

        # plot group legends next to the heatmap_ax (if given)
        if var_group_positions is not None and len(var_group_positions) > 0:
            gene_groups_ax = fig.add_subplot(axs[1, 1])
            arr = []
            for idx, pos in enumerate(var_group_positions):
                arr += [idx] * (pos[1] + 1 - pos[0])

            gene_groups_ax.imshow(
                np.matrix(arr).T, aspect='auto', cmap=groupby_cmap, norm=norm
            )
            gene_groups_ax.axis('off')

        # plot colorbar
        _plot_colorbar(im, fig, axs[1, 2])

    _utils.savefig_or_show('heatmap', show=show, save=save)

    return axs


def _check_var_names_type(var_names, var_group_labels, var_group_positions):
    """
    checks if var_names is a dict. Is this is the cases, then set the
    correct values for var_group_labels and var_group_positions
    Returns
    -------
    var_names, var_group_labels, var_group_positions
    """
    import collections.abc as cabc
    if isinstance(var_names, cabc.Mapping):
        logg.warning(
            "`var_names` is a dictionary. This will reset the current "
            "value of `var_group_labels` and `var_group_positions`."
        )
        var_group_labels = []
        _var_names = []
        var_group_positions = []
        start = 0
        for label, vars_list in var_names.items():
            if isinstance(vars_list, str):
                vars_list = [vars_list]
            # use list() in case var_list is a numpy array or pandas series
            _var_names.extend(list(vars_list))
            var_group_labels.append(label)
            var_group_positions.append((start, start + len(vars_list) - 1))
            start += len(vars_list)
        var_names = _var_names

    elif isinstance(var_names, str):
        var_names = [var_names]

    return var_names, var_group_labels, var_group_positions
