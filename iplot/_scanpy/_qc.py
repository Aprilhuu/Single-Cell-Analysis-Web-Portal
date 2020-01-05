from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scanpy as sc
from anndata import AnnData


def highest_expr_genes(adata: AnnData,
                       n_top: int = 30,
                       gene_symbols: Optional[str] = None,
                       log: bool = False,
                       save: Optional[str] = None,
                       **kwds
                       ):
    from scipy.sparse import issparse
    norm_dict = sc.pp.normalize_total(adata, target_sum=100, inplace=False)
    # identify the genes with the highest mean
    if issparse(norm_dict['X']):
        mean_percent = norm_dict['X'].mean(axis=0).A1
        top_idx = np.argsort(mean_percent)[::-1][:n_top]
        counts_top_genes = norm_dict['X'][:, top_idx].A
    else:
        mean_percent = norm_dict['X'].mean(axis=0)
        top_idx = np.argsort(mean_percent)[::-1][:n_top]
        counts_top_genes = norm_dict['X'][:, top_idx]
    columns = (
        adata.var_names[top_idx]
        if gene_symbols is None
        else adata.var[gene_symbols][top_idx]
    )
    counts_top_genes = pd.DataFrame(
        counts_top_genes, index=adata.obs_names, columns=columns
    )
    data = []
    for col in counts_top_genes.columns:
        data.append(go.Box(y=counts_top_genes[col], name=col))
    layout = go.Layout(xaxis={'type': 'log' if log else 'linear'})
    fig = go.Figure(data, layout)
    if save:
        fig.write_image(save)
    return fig.to_json(save + ".json")
