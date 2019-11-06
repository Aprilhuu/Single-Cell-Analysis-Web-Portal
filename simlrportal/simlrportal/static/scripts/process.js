const dataset_table_option = {
  item: `<tr class="id">
    <td class="name"></td>
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

  $.get("/installed-methods", {
    type: 'reader',
    name: '_all'
  }, data => {
    data = JSON.parse(data);
    table.clear();
    table.add(data);
  });
})


$("#dataset-table .list").click(() => {
  let target = $(event.target);
  if (target.prop("tagName") === "TD") {
    target = target.parent()
  } else {
    return
  }
  $("#chosen-dataset").text($(target.children()[0]).text())
  $("#chosen-dataset").data("id", target.data("id"))
  $("#modal-dataset").modal("hide")
});


$("#reader-table .list").click(() => {
  let target = $(event.target);
  if (target.prop("tagName") === "TD") {
    target = target.parent()
  } else {
    return
  }
  $("#chosen-reader").text($(target.children()[0]).text())
  $("#modal-reader").modal("hide")
});
