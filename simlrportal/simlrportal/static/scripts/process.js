'use strict'
/**
  For Process Section
**/


let installedReaders;

$.get("/installed-methods", {
  type: 'reader',
  name: '_all'
}, data => {
  installedReaders = JSON.parse(data);
});

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

$(".options").click(() => {
  let target = $(event.target)
  if (target.prop("tagName") === "I") {
    target = target.parent()
  }
  const reader = installedReaders.find(el => {
    return el.name === target.data("name") && el.package === target.data("package")
  })
  if (!reader) return;
  $("#option-content").empty()
  $("#option-bool").empty()
  constructOptions($("#option-content"), $("#option-bool"), reader.params)
  $("#modal-option").modal("show");
})
