'use strict'
/**
  Construct Options Setting for initializing process
**/


const constructOptions = (target, params) => {
  params.forEach(el => {
    if (el.type === "text" || el.type === "number") {
      target.append(optionTextFactory(el, el.type))
    } else if (el.type === "option") {
      target.append(optionRadioFactory(el))
    }
  })
}

const optionTextFactory = (obj, input_type) => {
  const form_group = $('<div class="form-group col-md-6"></div>')

  const label_ = $('<label></label>')
  label_.attr("for", "option" + obj.name)
  label_.text(obj.name)

  const input_ = $('<input class="form-control">')
  input_.attr("id", "option" + obj.name)
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

const optionRadioFactory = (obj) => {
  const form_group = $('<div class="form-group col-md-6"></div>')
  const label_ = $('<label></label>')
  label_.attr("for", "option" + obj.name)
  label_.text(obj.name)

  const select_ = $('<select class="form-control"></select>')
  select_.attr("id", "option" + obj.name)

  const option_selected = $('<option selected></option>')
  option_selected.text(obj.options[0])
  select_.append(option_selected)

  obj.options.slice(1).forEach(opt => {
    const option_ = $('<option></option>')
    option_.text(opt)
    select_.append(option_)
  })

  form_group.append(label_, select_)
  return form_group
}
