# Single Cell Analysis Web Portal

## Install

```
conda env create -f environment.yml
python manage.py runserver
```

IMPORTANT: There is a dependency issue among h5py, annData packages. DON'T upgrade any packages yet. 

Major dependencies: django, scanpy, plotly, plotly-orca, requests

## Contribute

### iplot
__iplot__ is the package for interactive plot pipelines. The package aims to rewrite single cell research plotting APIs 
among different packages with plotly. 

The package will provide APIs as 
`iplot.[PACKAGE NAME].[FUNCTION NAME](annData, **params, save_static=None)`, the standard function should return a JSON string
for plotly package, and `**params` will be all the parameters as from the original plotting function, `save_static` should be `[str | None]`
 and indicates whether a static plot export should be saved to the provided path. 
 
 ### Calls to package functions
 All function calls will be provided as a JSON object as follows, write a parser or manually add them. If you add them manually, 
 you can click the top right corner inside the portal and in the installed method section there is the wizard for adding methods. 
 
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
