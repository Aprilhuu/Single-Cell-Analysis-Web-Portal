const url = {
  name:  new URLSearchParams(window.location.search).get("name")
}
$.get("/process-history", url, (data) => {
  console.log(data)
})
