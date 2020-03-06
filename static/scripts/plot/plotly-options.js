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
    const templateOption = $("#template");
    templateOption.click(() => {
        const template = templateOption.data('template');
        updateTemplate(template);
        if (template === "plotly_white") {
            templateOption.data('template', 'plotly_dark').text("Dark Background");
        } else {
            templateOption.data('template', 'plotly_white').text("Bright Background");
        }
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
        if (templates[template]) {
            Plotly.relayout(divPlotly, {template: templates[template]});
            if (template === "plotly_dark") {
                $("#plotly .updatemenu-item-text").css('fill', 'black');
            }
            return;
        }
        $.ajax({
            url: '/static/plot-template/' + template + '.json',
            dataType: 'json',
            success: (data) => {
                Plotly.relayout(divPlotly, {template: data});
                templates[template] = data;
                if (template === "plotly_dark") {
                    $("#plotly .updatemenu-item-text").css('fill', 'black');
                }
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
        selection_div.append(selected_button);
        selection_div.append(trace_button);


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
                    const href = "/process/new-process.html?dataset=" + String(data.id);
                    const further_button = $("<a class='btn btn-primary'>Start Further Analysis</a>");
                    further_button.attr("href", href);
                    $("#modal-warning .modal-footer").prepend(further_button);
                }
            });
        });
    };

    const type = divPlotly.data[0].type;
    if (type === "scattergl" || type === "scatter") {
        addOptionsScatter(divPlotly);
        templateOption.data("template", "plotly_dark");
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



