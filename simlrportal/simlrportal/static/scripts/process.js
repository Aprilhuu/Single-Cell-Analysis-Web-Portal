'use strict'
/**
  For Process Section
**/


const new_steps_option = {
  item: `<div class="col-2">
            <div class="card-shadow-secondary border mb-3 card card-body border-secondary card-new-steps">
              <h5 class="card-title" style="text-transform: lowercase;">
                <span class="package"></span>.<span class="name">
              </h5>
              <span class="description"></span>
            </div>
          </div>`,
  valueNames: ['name', 'package', 'description']
}

const new_steps_table = new List('new-steps-table', new_steps_option, {});

const active_processing = []

let installedReaders;

$("#new-steps-table .list").click(() => {
  let target = $(event.target)
  if (! target.hasClass("card-new-steps")) {
    target = target.parent()
  }
  if (! target.hasClass("card-new-steps")) {
    return;
  }
  const process_info = constructProcess(target.find(".name").text(), target.find(".package").text())
  active_processing.push(process_info);
})

$.get("/installed-methods", {
    type: 'reader',
    name: '_all'
  }, data => {
  installedReaders = JSON.parse(data);
});

let installedMethods;

$.get("/installed-methods", {
    type: 'processing',
    name: '_all',
  }, data => {
  installedMethods = JSON.parse(data);
  new_steps_table.clear()
  new_steps_table.add(installedMethods)
})

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
  const name = target.find(".name")
  const pack = target.find(".package")
  $("#chosen-reader").text(name + "." + pack)
  $("#modal-reader").modal("hide")
  const options = $("#choose-reader").parent().find(".option")
  options.data("name", name)
  options.data("package", pack)
});

$("#active-process-table").click(e => {
  let target = $(event.target)
  if (target.hasClass("fa-cog")) {
    target = target.parent()
  }
  if (target.hasClass("option-btn")) {
    const params = active_processing.find(el => el.pid == target.parent().data("pid")).params
    $("#modal-option").data("type", "processing")
    $("#option-content").empty()
    $("#option-bool").empty()
    $("#modal-option").data("pid", target.parent().data("pid"))
    constructOptions($("#option-content"), $("#option-bool"), params);
    $("#modal-option").modal("show");
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

  for (let i = 0; i < obj.params.length; i++) {
    obj.params[i].default = retriveValue(obj.params[i])
  }

})
