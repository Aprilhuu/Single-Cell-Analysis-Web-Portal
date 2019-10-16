const allowed_file = $("#allowed_file").text().split(", ")

const files = $("#file")[0].files;
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
  const file_ext = file.name.substring(file.name.lastIndexOf(".") + 1, file.name.length);
  if (!allowed_file.includes(file_ext)) {
    console.log("not allowed")
    return
  }
  const formData = new FormData($("#form-upload")[0]);
  $.ajax({
    url: 'dataupload',
    data: formData,
    processData: false,
    contentType: false,
    type: 'POST',
    success: function(data) {
      alert(data);
    }
  });
}