# Web Portal
## Install
requires pip/conda, python3
```
pip install requirements.txt
python app.py
```

#### installed-methods
To add a function, add a specified json object to `/installed-methods/[FILE].json`. Then, the front end will be able to render the controls.

`reader.json` assumes the function's first parameter is a path and will return AnnData (or None if failed).  
`processings.json` assumes the function's first parameter is an AnnData object and will manipulate the AnnData object.  
`visualizatoins.json` assume the function's first parameter is an AnnData object
and will return an Plotly formated json string for ploting.

##### Specifications for each method
 `name:string, package:string` The exact function name and package name of the function.

 `description:string` a help string that explain what this function does

 `params:Array[Object]` necessary parameters for the function call excludes the first parameter, params will be an array of parameters. Each parameter will be a json object in the format specified

 `prerequisites: Array[Object] (optional)` if this method need to run after some other methods. Each prerequisite will be a json object in the form of name and package.


##### Specifications for parameter
 `name: string` parameter's name

 `type: [ text | number | option | bool ]` The type of the input,
  - `text` if the function parameter is a `str` or `List(str)`
  - `number` if the function parameter is `int`, `float` or other numerical type
  - `option` if the function parameter is one of several values
  - `bool` if the function parameter is a bool

`annotation: string (optional)` explaination for this parameter

`isList: bool (optional, type=text)`  if `List(str)` is expected for parameter input. Then the string will be splited by `, `

`options: Array[string] (required if type=option)` the options.

`default: string (optinoal)` the default value of the parameter.

`required: bool (optional)` if the parameter is required
