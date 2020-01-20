from typing import List, Optional, Union, Sequence, Literal
from anndata import AnnData
import plotly.graph_objects as go

def tsne(adata: AnnData,
         basis: str,
         ids: Union[str, Sequence[str], None] = None,
         gene_symbols: Optional[str] = None,
         use_raw: Optional[bool] = None,
         layer: Optional[str] = None,
         sort_order: bool = True,
         groups: Optional[str] = None,
         components: Union[str, Sequence[str], None] = None,
         projection: Literal['2d', '3d'] = '2d'):
    if groups and isinstance(groups, str):
        groups = list(groups)

    if use_raw:
        use_raw = layer is None and adata.raw is not None
    if use_raw and layer is not None:
        raise ValueError("Cannot use both a layer and the raw representation. Was passed:"
            f"use_raw={use_raw}, layer={layer}.")
    if adata.raw is None and use_raw:
        raise ValueError(
            "`use_raw` is set to True but AnnData object does not have raw. "
            "Please check."
        )