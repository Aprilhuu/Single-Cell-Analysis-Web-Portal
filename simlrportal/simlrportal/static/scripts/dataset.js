/**
JS Code for uploading
**/

const allowed_file = $("#allowed_file").text().split(", ")

$("#file").change(() => {
  if ($("#file")[0].files.length == 0) {
    return;
  }
  const file = $("#file")[0].files[0];
  if (file.name.lastIndexOf(".") == -1) {
    return;
  }
  const file_name = file.name.substring(0, file.name.lastIndexOf("."));
  const file_ext = file.name.substring(file.name.lastIndexOf(".") + 1, file.name.length);

  $("#file-text").text("File size: " + String(Math.round10(file.size / 1024 / 1024, -2)) + "MB")
  $("#name").val(file_name)
  $("#ext").val(file_ext)
})

const resetForm = () => {
  $('#form-upload').trigger('reset');
  $("#file-text").text("For .mtx, please upload the directory as a zip file")
}

const uploadFile = () => {
  const file = $("#file")[0].files[0];
  if (!file) {
    return;
  }
  const file_ext = file.name.substring(file.name.lastIndexOf(".") + 1, file.name.length);
  if (!allowed_file.includes(file_ext)) {
    $("#model_warning .modal-title").text("Incompatible file Extension")
    $("#model_warning .modal-body p").text("The uploading file does not have a recognizable extension, please upload a valid dataset file")
    $("#model_warning").modal();
    return
  }
  const formData = new FormData($("#form-upload")[0]);
  $.ajax({
    url: '/dataupload',
    data: formData,
    processData: false,
    contentType: false,
    type: 'POST',
    success: function(data) {
      $("#model_warning .modal-title").text("Uploaded")
      $("#model_warning .modal-body p").text("The file is uploaded")
      $("#model_warning").modal();
    }
  });
}

/**
JS Code for Listing
**/

const removeDataset = (id) => {
  if (id === ""){
    return
  }
  $.ajax({
    url: "/datasets",
    method: "DELETE",
    data: {
      'id': id
    },
  }).done(function(data) {
    table.remove('id', data.id);
  });
}

$("#dataset-table").click(e => {
  if (!e.target) {
    return;
  }
  const classes = $(e.target).attr("class")
  if (classes.includes("btn-danger")) {
    removeDataset($(e.target).data("id"))
  } else if (classes.includes("fa-times")) {
    removeDataset($(e.target).parent().data("id"))
  }
})
