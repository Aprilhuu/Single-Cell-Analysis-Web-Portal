'use strict';
const shape = ($("#dataset-shape").text()).split(", ").map(e => Number(e));
const n_vars = shape[0];
const n_obs = shape[1];
const attrs = JSON.parse($("#dataset-attrs").text());
const id = Number($(".id").text());

const resetStudio = () => {
    $("#plotly").prop("hidden", true);
    $("#div-select").prop("hidden", false);
};

if (attrs.obsm.includes("X_pca")) {
    $(".basis").append($("<option value='scanpy.pca'>PCA</option>"))
}
if (attrs.obsm.includes("X_tsne")) {
    $(".basis").append($("<option value='scanpy.tsne'>tSNE</option>"))
}
if (attrs.obsm.includes("X_umap")) {
    $(".basis").append($("<option value='scanpy.umap'>UMAP</option>"))
}

attrs.obs.forEach(col => {
    $("#scatter-names").append($("<option>" + col + "</option>"))
});

if (attrs.var.includes("n_cells")) {
    $.get('/plot/plot-sync', {
        id: id,
        call: "portal.get_rank_genes"
    }, data => {
        console.log(data);
        data.index.forEach(i => {
            const markernames = $("#marker-names");
            markernames.append($("<option>" + i + "</option>"));
            markernames.selectpicker('refresh');
        })
    })
}


$(".scatter-button").click(() => {
    const type = $(event.target).data("type");
    const call = $("#" + type + "-basis").val();
    const names = $("#" + type + "-names").selectpicker("val");
    if (!call || !names) {
        return;
    }
    $.get("/plot/plot-sync", {
        id: id,
        call: call,
        params: JSON.stringify({names: names})
    }, data => {
        $("#plotly").prop("hidden", false);
        Plotly.newPlot('plotly', JSON.parse(data), {});
        $("#div-select").prop("hidden", true);
        window.scrollTo(0, document.body.scrollHeight);
    });
});