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
        updateTemplate(template);
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

    const updateTemplate = (template) => {
        target = $(".template-choice[data-template=" + template + "]");
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
    };


    const addOptionsScatter = (divPlotly) => {
        const selection_div = $("#selection-div");
        const selected_button = $('<button class="my-2 mr-2 btn btn-primary" ' +
            'id="button-selected">Export Selected Data Points</button>');
        const trace_button = $('<button class="my-2 mr-2 btn btn-primary" ' +
            'id="button-shown">Export Selected Clusters</button>');
        const further_button = $('<button class="mt-2 mr-2 btn btn-primary" ' +
            'id="button-select">Plot on the selected Data</button>');
        selection_div.append(selected_button);
        selection_div.append(trace_button);
        $("#data-wizard-card .card-footer").append(further_button);


        const select_confirm = $("#select-confirm");

        trace_button.click(() => {
            selected_points = [];
            divPlotly.data.forEach((trace) => {
                if (trace.visible === true) selected_points.push(...trace.text);
            });
            $('#selected-length').text(selected_points.length);
            if (selected_points.length > 0) {
                select_confirm.prop("disabled", false);
            } else {
                select_confirm.prop("disabled", true);
            }
        });

        selected_button.click(() => {
            const selected_length = $('#selected-length');
            if (!selected) {
                selected_length.text(0);
                select_confirm.prop("disabled", true);
                return;
            }
            selected_points = [];
            selected.points.forEach(p => selected_points.push(p.text));
            selected_length.text(selected_points.length);
            if (selected_points.length > 0) {
                select_confirm.prop("disabled", false);
            } else {
                select_confirm.prop("disabled", true);
            }
        });

        select_confirm.click(() => {
            if (selected_points.length === 0) {
                return;
            }
            const data = {
                pid: $("#output").data("id"),
                index: selected_points.join(",")
            };
            const name = $("#name-input").val();
            if (name !== "") data.name = name;
            const description = $("#description-input").val();
            if (description !== "") data.description = description;

            $("#modal-warning .modal-title").text("Exporting");
            $("#modal-warning .modal-body p").text("The data is exporting, please keep this page open");
            $("#modal-warning").modal();

            $.ajax({
                url: '/dataset/result-export',
                type: "POST",
                data: data,
                success: (data) => {
                    $("#modal-warning .modal-title").text("Export");
                    $("#modal-warning .modal-body p").text(data.info);
                }
            });
        });

        further_button.click(() => {
//TODO: ASK FOR FUTTHER ANALYSIS CODE
        })

    };

    const type = divPlotly.data[0].type;
    if (type === "scattergl" || type === "scatter") {
        addOptionsScatter(divPlotly);
        updateTemplate("plotly_white");
    }

    $("#data-wizard").click(() => {

        const wizard = $('#data-wizard-card');
        if (wizard.prop("hidden")) {
            wizard.prop('hidden', false);
            if (wizard.data("shown") === true) {
                return;
            }
            wizard.data("shown", true);
        } else {
            wizard.prop('hidden', true);
        }
    });

};



