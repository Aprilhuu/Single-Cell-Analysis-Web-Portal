from typing import Optional, Sequence

import numpy as np
import plotly.graph_objects as go
from anndata import AnnData

from .._utils._color import get_weighted_color_blend


def tsne(adata: AnnData,
         genes: Optional[Sequence[str]] = None,
         use_raw: Optional[bool] = None,
         layer: Optional[str] = None,
         palette: str = 'Accent',
         save: Optional[str] = None
         ):
    return _scatter(adata, "tsne", genes, use_raw, layer, save, palette)


def _scatter(adata: AnnData,
             basis: str,
             genes: Optional[Sequence[str]] = None,
             use_raw: Optional[bool] = None,
             layer: Optional[str] = None,
             save: Optional[str] = None,
             palette: str = 'Accent') -> None:
    """
    Plot a 2D scatter plot on the given basis,
    :param adata: given annData that contains the obsm of the given basis
    :param basis: the name of the basis, currently accepting tsne and umap
    :param genes: a list of gene names that will decide the coloring. If is None, chose the top 5 most.
    :param layer: Name of the AnnData object layer that wants to be plotted.
    :param use_raw: Use .raw attribute of adata for coloring with gene expression.
    """

    if f'X_{basis}' not in adata.obsm_keys():
        raise ValueError(f"Cannot find the basis. Was passed {basis}")

    if genes is not None:
        genes = genes[:5]
    elif "n_cells" in adata.var.columns:
        genes = adata.var.sort_values("n_cells", ascending=False).index[:5]
    else:
        genes = adata.var.sort_values(adata.var.columns[1], ascending=False).index[:1]
    if use_raw:
        use_raw = layer is None and adata.raw is not None
        if layer is not None:
            raise ValueError("Cannot use both a layer and the raw representation. Was passed:"
                             f"use_raw={use_raw}, layer={layer}.")
        if adata.raw is None:
            raise ValueError(
                "`use_raw` is set to True but AnnData object does not have raw. "
                "Please check."
            )
        matrix = np.array(adata.raw[:, genes].X.toarray())
    elif layer is not None:
        if adata.layers is None:
            raise ValueError("AnnData does not have any layers")
        if adata.layers.get(layer) is None:
            raise ValueError(f"Cannot find the layer. Was passed: {layer}")
        matrix = np.array(adata.layers[layer].X.toarray())
    else:
        matrix = np.array(adata[:, genes].X.toarray())

    c = get_weighted_color_blend(matrix, palette)

    fig = go.Figure()

    fig.add_trace(
        go.Scattergl(
            x=adata.obsm['X_tsne'][:, 0],
            y=adata.obsm['X_tsne'][:, 1],
            mode='markers',
            marker={
                'color': [f'rgb({row[0]}, {row[1]}, {row[2]})' for row in list(c)],
                'opacity': .8
            }
        )
    )

    if save:
        fig.write_image(save)
    return fig.to_json()
