'use strict'
/**
  Construct Options Setting for initializing process
**/


const constructOptions = (opt, boolopt, params) => {
  params.forEach(el => {
    if (el.type === "text" || el.type === "number") {
      opt.append(optionTextFactory(el, el.type))
    } else if (el.type === "option") {
      opt.append(optionOptionFactory(el))
    } else if (el.type === "bool") {
      boolopt.append(optionBoolFactory(el))
    }
  })
}

const optionTextFactory = (obj, input_type) => {
  const form_group = $('<div class="form-group col-md-6"></div>')

  const label_ = $('<label></label>')
  label_.attr("for", "option-" + obj.name)
  label_.text(obj.name)

  const input_ = $('<input class="form-control">')
  input_.attr("id", "option-" + obj.name)
  input_.attr("type", input_type)

  form_group.append(label_, input_)

  if (obj.annotation) {
    input_.attr("aria-describedby", "annotation-" + obj.name)
    const small_ = $('<small class="form-text text-muted">')
    small_.attr("id", "annotation-" + obj.name)
    small_.text(obj.annotation)
    form_group.append(small_)
  }

  if (obj.default) {
    input_.val(obj.default)
  }

  return form_group
}

const optionOptionFactory = (obj) => {
  const form_group = $('<div class="form-group col-md-6"></div>')
  const label_ = $('<label></label>')
  label_.attr("for", "option-" + obj.name)
  label_.text(obj.name)

  const select_ = $('<select class="form-control"></select>')
  select_.attr("id", "option-" + obj.name)

  const option_selected = $('<option selected></option>')
  option_selected.text(obj.options[0])
  select_.append(option_selected)

  obj.options.slice(1).forEach(opt => {
    const option_ = $('<option></option>')
    option_.text(opt)
    select_.append(option_)
  })

  form_group.append(label_, select_)

  if (obj.annotation) {
    select_.attr("aria-describedby", "annotation-" + obj.name)
    const small_ = $('<small class="form-text text-muted">')
    small_.attr("id", "annotation-" + obj.name)
    small_.text(obj.annotation)
    form_group.append(small_)
  }
  return form_group
}

const optionBoolFactory = (obj) => {
  const form_group = $('<div class="form-check form-check-inline" data-toggle="tooltip"></div>')

  const input_ = $('<input type="checkbox" class="custom-control-input"/>')
  input_.attr("id", "option-" + obj.name)
  if (obj.default) {
    input_.prop("checked", true)
  }
  const label_ = $('<label class="custom-control-label"></label>')
  label_.attr("for", "option-" + obj.name)
  label_.text(obj.name)


  const toggle_ = $('<div class="custom-control custom-switch"></div>')
  toggle_.append(input_, label_)

  form_group.append(toggle_)

  if (obj.annotation) {
    form_group.prop('title', obj.annotation)
  }



  return form_group
}
