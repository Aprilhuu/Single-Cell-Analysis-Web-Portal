const divPlotly = document.querySelector('#plotly');
const templates = {
    none: {}
};
$.ajax({
    url: $('#output').data('link'),
    dataType: 'json',
    success: function (data) {
        Plotly.newPlot('plotly', JSON.parse(data), {}, {modeBarButtonsToRemove: ['toImage']});
    },
    statusCode: {
        404: () => alert('Plot not found')
    }
});

$("#orientation").click(() => {
    const icon = $("#orientation i");
    if (icon.hasClass("fa-arrow-circle-up")) {
        Plotly.restyle(divPlotly, {orientation: 'h'});
    } else {
        Plotly.restyle(divPlotly, {orientation: 'v'});
    }
    icon.toggleClass("fa-arrow-circle-up fa-arrow-circle-right");
});

$("#legend").click(() => {
    const legend = $("#legend");
    if (legend.text() === "Hide Legend") {
        legend.html('<i class=\"metismenu-icon fas fa-bars\"></i>Show Legend');
        Plotly.relayout(divPlotly, {showlegend: false});
    } else {
        legend.html('<i class="metismenu-icon fas fa-bars"></i>Hide Legend');
        Plotly.relayout(divPlotly, {showlegend: true});
    }
});

$(".template-choice").click(() => {
    const target = $(event.target);
    const template = target.data('template');
    $(".template-choice").removeClass('active-sidebar');
    target.addClass('active-sidebar');
    if (templates[template]) {
        Plotly.relayout(divPlotly, {template: templates[template]});
        return;
    }
    $.ajax({
        url: '/static/plot-template/' + template + '.json',
        dataType: 'json',
        success: (data) => {
            Plotly.relayout(divPlotly, {template: data});
            templates[template] = data;
        },
        statusCode: {
            404: () => alert('Plot not found')
        }
    });
});

$(".ratio-choice").click(() => {
    const target = $(event.target);
    $(".ratio-choice").removeClass('active-sidebar');
    target.addClass('active-sidebar');
});
$(".size-choice").click(() => {
    const target = $(event.target);
    $(".size-choice").removeClass('active-sidebar');
    target.addClass('active-sidebar');
});

$("#download-image").click(() => {
    const config = {
        format: 'png',
        filename: $('#output').text().trim()
    };
    const ratio = $(".ratio-choice.active-sidebar").data("ratio").split(",");
    const size = Number($(".size-choice.active-sidebar").data("size"));
    if (ratio[0] >= ratio[1]) {
        config.width = size;
        config.height = size * ratio[1] / ratio[0];
    } else {
        config.height = size;
        config.width = size * ratio[0] / ratio[1];
    }
    Plotly.downloadImage(divPlotly, config);
});