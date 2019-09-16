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
