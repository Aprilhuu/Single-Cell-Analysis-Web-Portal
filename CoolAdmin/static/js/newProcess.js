const toggleDataset = (condition) => {
  let target = $(this.event.target)
  if (target.prop("tagName") == "I") {
      target = target.parent()
  }
  if (condition) {
    $("#title-chosen").text("Chosen Dataset: ")
    $("#title-dataset").text(target.parent().parent().children()[0].innerText)
    $("#search-data").hide()
    $("#dataset-table").hide()
    $("#cancel-data").fadeIn()
    $(".processes").fadeIn()
  } else {
    $("#title-chosen").text("Chose The Dataset")
    $("#title-dataset").text("")
    $("#search-data").fadeIn()
    $("#dataset-table").fadeIn()
    $("#cancel-data").hide()
    $(".processes").hide()
  }
}

$(".process-card").click((e) => {
  target = $(e.target)
  while (!target.hasClass("process-card")){
    target = target.parent()
  }
  target = $(target.children()[0])
  if (target.hasClass("bg-success")) {
    target.removeClass("bg-success");
    target.addClass("bg-secondary")
  } else if (target.hasClass("bg-secondary")) {
    target.removeClass("bg-secondary");
    target.addClass("bg-success")
  }
})

$("#sortable").sortable()
$( "#sortable" ).disableSelection();
