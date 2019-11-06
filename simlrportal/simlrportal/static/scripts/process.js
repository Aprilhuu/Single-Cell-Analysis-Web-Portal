const table_option = {
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

$("#choose-dataset").click(() => {
  $("#modal-dataset").modal("show");
  const table = new List('dataset-table', table_option, {});

  $.get("/datasets", {
    limit: 10,
    offset: 0
  }, data => {
    table.clear();
    table.add(data);
  });
})

$(".list").click(() => {
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
