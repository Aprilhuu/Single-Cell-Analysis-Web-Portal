$("#submit-process").click(e => {
    const worker_name = $("#worker-name");
    if (worker_name.val() === "") {
        return;
    }
    const full_data = {
        name: worker_name.val()
    };
    const process_order = $("#active-process-table").find(".btn-alternate.option-btn")
        .parent()
        .map((index, e) => {
            return $(e).data("pid")
        })
        .get();

    const reader_data = {
        name: $(".non-sort .options").data("name"),
        package: $(".non-sort .options").data("package"),
        params: {filename: $("#chosen-dataset").data("id")}
    };

    if (!reader_data.params.filename) {
        const card_ = $($("#active-process-table .card-process")[0]);
        card_.addClass("card-shadow-danger border-danger");
        card_.removeClass("card-shadow-secondary border-secondary");
        return;
    }

    const curr_reader = installedReaders.find(el => el.name === reader_data.name && el.package === reader_data.package);
    reader_data.type = curr_reader.type;
    curr_reader.params.forEach(p => {
        reader_data.params[p.name] = p.default
    });


    const data = [reader_data];

    let integrity = true;
    process_order.forEach((order) => {
        const process = active_processing.find(e => e.pid === order);
        const target = {
            name: process.name,
            type: process.type,
            package: process.package,
            params: {},
            view: process.view
        };
        process.params.forEach(p => {
            if (p.required && p.default === "") {
                integrity = false;
                const card_ = $("#active-process-table .card-pp span")
                    .filter((index, e) => $(e).data("pid") === order).parent();
                card_.addClass("card-shadow-danger border-danger");
                card_.removeClass("card-shadow-secondary border-secondary");
            }
            target.params[p.name] = p.default;
            if (p.type === "number") {
                target.params[p.name] = Number(target.params[p.name])
            }
        });
        data.push(target);
    });

    if (!integrity) {
        $("#modal-warning .modal-title").text("Integrity Check");
        $("#modal-warning .modal-body p").text("Exist required parameters that is not filled");
        $("#modal-warning").modal();
        return;
    }

    full_data.process = JSON.stringify(data);

    console.log(full_data);

    $.ajax({
        url: '/process/new-process',
        data: full_data,
        type: 'POST',
        success: data => {
            $("#modal-warning .modal-title").text("Work Deplyed");
            $("#modal-warning .modal-body p").text("Work has been successfully deployed, " +
                "the deployment ID is " + data.info);
            $("#modal-warning").modal();
        }
    });
});
