const progress_history_table_option = {
  item: `<div class="col-lg-3 col-md-4">
    <a class="status link" href="">
      <div class="card mb-3 widget-content">
        <div class="widget-content-outer">
          <div class="widget-content-wrapper">
            <div class="widget-content-left">
              <div class="widget-heading name"></div>
              <div class="widget-subheading">Last Modified:
                <span class="time"></span>
              </div>
            </div>
            <div class="widget-content-right">
              <div class="widget-numbers">
                <span class="curr"></span>/<span class="total"></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </a>
  </div>`,
  valueNames: ['time', 'curr', 'total', 'name', {
    name: 'status', attr: 'data-status'
  }, {
    name: 'link', attr: 'href'
  }]
}

const progress_history_table = new List('progress-history-table', progress_history_table_option, {});

$.get("/process-history", {
  type: 'processing',
  name: '_all',
}, data => {
  progress_history_table.clear()
  console.log(
    data.map(e => {
      e.link = "/process.html?name=" + e.id
      return e
    })
  )
  progress_history_table.add(data)
})
