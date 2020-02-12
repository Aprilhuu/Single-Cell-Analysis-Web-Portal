const activateOptions = (divPlotly) => {
    /***
     * Change the orientation of the plot
     */
    $("#orientation").click(() => {
        const target = $(event.target);
        if (target.data('orientation') === 'v') {
            Plotly.restyle(divPlotly, {orientation: 'h'});
            target.data('orientation', 'h').text("Vertical Layout")
        } else {
            Plotly.restyle(divPlotly, {orientation: 'v'});
            target.data('orientation', 'v').text("Horizontal Layout")
        }
    });

    /***
     * Hide the legend
     */
    $("#legend").click(() => {
        const legend = $("#legend");
        if (legend.text() === "Hide Legend") {
            legend.html('Show Legend');
            Plotly.relayout(divPlotly, {showlegend: false});
        } else {
            legend.html('Hide Legend');
            Plotly.relayout(divPlotly, {showlegend: true});
        }
    });

    /***
     * Choose the overall template
     */
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

    /***
     * Choose the output ratio
     */
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
            config.height = Math.round(size * ratio[1] / ratio[0]);
        } else {
            config.height = size;
            config.width = Math.round(size * ratio[0] / ratio[1]);
        }
        Plotly.downloadImage(divPlotly, config);
    });
};


$("#data-wizard").click(() => {
    const type = divPlotly.data[0].type;

    const wizard = $('#data-wizard-card');
    if (wizard.prop("hidden")) {
        wizard.prop('hidden', false);
        if (wizard.data("shown") === true) {
            return;
        }
        wizard.data("shown", true);
    } else {
        wizard.prop('hidden', true);
        return;
    }

    if (type === "scattergl" || type === "scatter") {
        addOptionsScatter(divPlotly);
    }
});

const addOptionsScatter = (divPlotly) => {
    const card_body_ = $('#data-wizard-card .card-body .row');
    const col_ = $('<div class="col-md-6 col-lg-4"></div>');
    const selected_button = $('<button class="mb-2 mr-2 btn btn-primary" ' +
        'id="button-selected">Export Selected Data Points</button>');
    const trace_button = $('<button class="mb-2 mr-2 btn btn-primary" ' +
        'id="button-shown">Export Selected Clusters</button>');
    col_.append(selected_button);
    col_.append(trace_button);
    card_body_.append(col_);

    trace_button.click(() => {
        selected_points = [];
        divPlotly.data.forEach((trace) => {
            if (trace.visible === true) selected_points.push(...trace.text);
        });
        $('#selected-length').text(selected_points.length);
    });

    selected_button.click(() => {
        const selected_length = $('#selected-length');
        if (!selected) {
            console.log("not selected");
            selected_length.text(0);
            return;
        }
        selected_points = [];
        selected.points.forEach(p => selected_points.push(p.text));
        selected_length.text(selected_points.length);
    });

    $("#select-confirm").click(() => {
        if (selected_points.length === 0) {
            return;
        }
        const data = {
            pid: $("#output").data("id"),
            index: selected_points.join(",")
        };
        console.log(data);
        $.ajax({
            url: '/dataset/result-export',
            type: "POST",
            data: data,
            success: (data) => {
                console.log(data)
            }
        });
    })


};