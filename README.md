# Single Cell Analysis Web Portal

## Install

```
conda env create -f environment.yml
python manage.py runserver
```

IMPORTANT: There is a dependency issue among h5py, annData packages. DON'T upgrade any packages yet. 

Major dependencies: django, scanpy, plotly, plotly-orca, requests

## Contribute
See the development decumentation on https://lihd1003.github.io/Single-Cell-Analysis-Web-Portal/
