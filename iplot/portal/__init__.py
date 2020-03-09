def get_rank_genes(adata, subset=None, n_names=50):
    if subset is not None:
        adata = adata[subset, :]
    if "n_cells" not in adata.var.columns:
        return None
    return {'index': list(adata.var.sort_values("n_cells", ascending=False).index[:n_names])}
