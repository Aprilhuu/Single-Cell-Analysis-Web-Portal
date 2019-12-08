'use strict'
/**
  For Process Section
**/


/** ===== Table Options ===== **/
const new_steps_option = {
  item: `<div class="col-2">
            <div class="card-shadow-secondary border mb-3 card card-body border-secondary card-new-steps">
              <h5 class="card-title" style="text-transform: lowercase;">
                <span class="package"></span>.<span class="name">
              </h5>
              <div class="scroll-area-sm">
                <div class="scrollbar-container ps--active-y">
                  <span class="description"></span>
                </div>
              </div>
            </div>
          </div>`,
  valueNames: ['name', 'package', 'description']
}


const dataset_table_option = {
  item: `<tr>
    <td class="name id"></td>
    <td class="description"></td>
    <td class="modified">
    </td>
  </tr>`,
  valueNames: ['name', 'description', 'modified',
    {
      name: 'id',
      attr: 'data-id'
    }
  ]
}


const reader_table_option = {
  item: `<tr>
    <td><span class="package"></span>.<span class="name"></span></td>
    <td class="description"></td>
  </tr>`,
  valueNames: ['name', 'package', 'description']
}

/** ===== Variables ===== **/


const new_steps_table = new List('new-steps-table', new_steps_option, {});

const active_processing = []

let installedReaders;
let installedMethods;
$.get("/installed-methods", {
  type: 'reader',
  name: '_all'
}, data => {
  installedReaders = JSON.parse(data);
});
$.get("/installed-methods", {
  type: 'processing',
  name: '_all',
}, data => {
  installedMethods = JSON.parse(data);
  new_steps_table.clear()
  new_steps_table.add(installedMethods)
})

$("#new-steps-table .list").click(() => {
  let target = $(event.target)
  for (let i = 0; i < 5; i++) {
    if (!target.hasClass("card-new-steps")) {
      target = target.parent();
    } else {
      break;
    }
  }
  if (!target.hasClass("card-new-steps")) {
    return;
  }
  const process_info = constructProcess(target.find(".name").text(),
                                        target.find(".package").text())
  active_processing.push(process_info);
})


$("#choose-dataset").click(() => {
  $("#modal-dataset").modal("show");
  const table = new List('dataset-table', dataset_table_option, {});

  $.get("/datasets", {
    limit: 10,
    offset: 0
  }, data => {
    table.clear();
    table.add(data);
  });
})


$("#choose-reader").click(() => {
  $("#modal-reader").modal("show");
  const table = new List('reader-table', reader_table_option, {});
  table.clear();
  table.add(installedReaders);
})


$("#dataset-table .list").click(() => {
  let target = $(event.target);
  if (target.prop("tagName") === "TD") {
    target = target.parent()
  } else {
    return
  }
  $("#chosen-dataset").text($(target.children()[0]).text())
  $("#chosen-dataset").data("id", $(target.children()[0]).data("id"))
  $("#modal-dataset").modal("hide")

  const card_ = $($("#active-process-table .card-process")[0])
  card_.removeClass("card-shadow-danger border-danger");
  card_.addClass("card-shadow-secondary border-secondary");
});


$("#reader-table .list").click(() => {
  let target = $(event.target);
  if (target.prop("tagName") === "TD") {
    target = target.parent()
  } else if (target.parent().prop("tagName") === "TD") {
    target = target.parent().parent()
  } else {
    return
  }
  const name = target.find(".name").text()
  const pack = target.find(".package").text()
  $("#chosen-reader").text(pack + "." + name)
  $("#modal-reader").modal("hide")
  const options = $("#choose-reader").parent().find(".options")
  options.data("name", name)
  options.data("package", pack)
});


$("#active-process-table").click(e => {
  let target = $(event.target)
  if (display_mode === "s"
    && ! target.hasClass("fas")
    && ! target.hasClass("option-btn")) {
    if (target.parent().hasClass("card-pp")) {
      target = target.parent();
    }
    if (! target.hasClass("card-pp")) {
      return;
    }
    target.children("span").toggle();
    target.parent().toggleClass("col-lg-2 col-md-3 col-sm-6 col-lg-1 col-md-2 col-sm-4");
    return;
  }
  if (target.hasClass("fas")) {
    target = target.parent()
  }
  const pid = target.parent().data("pid")
  if (pid != 0 && !pid) {
    return
  }
  if (target.hasClass("btn-alternate")) {
    const params = active_processing.find(el => el.pid == pid).params
    $("#modal-option").data("type", "processing")
    $("#option-content").empty()
    $("#option-bool").empty()
    $("#modal-option").data("pid", target.parent().data("pid"))
    constructOptions($("#option-content"), $("#option-bool"), params);
    $("#modal-option").modal("show");
  } else if (target.hasClass("btn-danger")) {
    const index_ = active_processing.findIndex(el => el.pid == pid);
    if (index_ != -1) {
      active_processing.splice(index_, 1)
    }
    for (let i = 0; i < 5; i++) {
      if (target.hasClass("sort")) {
        target.remove()
        return;
      } else {
        target = target.parent()
      }
    }
  } else if (target.hasClass("btn-secondary")) {
    active_processing.find(el => el.pid == pid).view = true
    target.removeClass("btn-secondary")
    target.addClass("btn-success")
  } else if (target.hasClass("btn-success")) {
    active_processing.find(el => el.pid == pid).view = false
    target.removeClass("btn-success")
    target.addClass("btn-secondary")
  }
})


$(".options").click(() => {
  let target = $(event.target)
  if (target.prop("tagName") === "I") {
    target = target.parent()
  }
  const reader = installedReaders.find(el => {
    return el.name === target.data("name") && el.package === target.data("package")
  })
  if (!reader) return;
  $("#modal-option").data("type", "reader")
  $("#modal-option").data("name", target.data("name"))
  $("#modal-option").data("package", target.data("package"))
  $("#option-content").empty()
  $("#option-bool").empty()
  constructOptions($("#option-content"), $("#option-bool"), reader.params)
  $("#modal-option").modal("show");
})



$("#modal-option").on("hide.bs.modal", () => {
  const target = $("#modal-option")
  let obj;
  if (target.data("type") === "reader") {
    obj = installedReaders.find(el => {
      return el.name === target.data("name") && el.package === target.data("package")
    })
  } else if (target.data("type") === "processing") {
    obj = active_processing.find(el => el.pid == target.data("pid"))
  }
  if (!obj) {
    return
  }
  let required_params = false;
  for (let i = 0; i < obj.params.length; i++) {
    obj.params[i].default = retriveValue(obj.params[i])
    if (obj.params[i].required && obj.params[i].default === "") {
      required_params = true;
    }
  }
  const card_ = $("#active-process-table .card-pp span")
  .filter((index, e) => $(e).data("pid") === obj.pid).parent();

  if (required_params) {
    card_.addClass("card-shadow-danger border-danger");
    card_.removeClass("card-shadow-secondary border-secondary");
  } else {
    card_.removeClass("card-shadow-danger border-danger");
    card_.addClass("card-shadow-secondary border-secondary");
  }

})

/** hide the processes details in the queue
**/
let display_mode = "l";

$("#change-queue-display").click(() => {
  $("#change-queue-display").toggleClass("btn-primary btn-secondary");

  if (display_mode === "l") {
    display_mode = "s";
    $("#active-process-table .card-pp").parent()
    .removeClass("col-lg-2 col-md-3 col-sm-6");
    $("#active-process-table .card-pp").parent()
    .addClass("col-lg-1 col-md-2 col-sm-4");
    $("#active-process-table .scroll-area-sm.mt-1").hide();
    $("#active-process-table .card-pp span").hide();
    $("#active-process-table .card-process").css("height", "128px");
  } else {
    display_mode = "l";
    $("#active-process-table .card-pp").parent()
    .addClass("col-lg-2 col-md-3 col-sm-6");
    $("#active-process-table .card-pp").parent()
    .removeClass("col-lg-1 col-md-2 col-sm-4");
    $("#active-process-table .scroll-area-sm.mt-1").show();
    $("#active-process-table .card-pp span").show();
    $("#active-process-table .card-process").css("height", "240px");
  }
})




$("#submit-process").click(e => {
  if ($("#worker-name").val() === "") {
    return;
  }
  const full_data = {
    name: $("#worker-name").val()
  }
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
  }

  if (! reader_data.params.filename) {
    const card_ = $($("#active-process-table .card-process")[0])
    card_.addClass("card-shadow-danger border-danger");
    card_.removeClass("card-shadow-secondary border-secondary");
    return;
  }

  const curr_reader = installedReaders.find(el => el.name === reader_data.name && el.package === reader_data.package);
  curr_reader.params.forEach(p => {
    reader_data.params[p.name] = p.default
  })


  const data = [reader_data];

  let integrity = true;
  process_order.forEach((order) => {
    const process = active_processing.find(e => e.pid === order);
    const target = {
      name: process.name,
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
    })
    data.push(target);
  })

  if (! integrity) {
    $("#modal-warning .modal-title").text("Integrity Check")
    $("#modal-warning .modal-body p").text("Exist required parameters that is not filled")
    $("#modal-warning").modal();
    return;
  }
  full_data.process = data;
  $.ajax({
    url: '/new-process',
    data: JSON.stringify(full_data),
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
    type: 'POST',
    success: (data) => {
      $("#modal-warning .modal-title").text("Work Deplyed")
      $("#modal-warning .modal-body p").text("Work has been successfully deployed, the deployment ID is " + data.info)
      $("#modal-warning").modal();
    }
  });
})
