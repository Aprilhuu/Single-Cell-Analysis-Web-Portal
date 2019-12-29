import os
from SIMLR.settings import BASE_DIR
from shutil import get_archive_formats

INSTALLED_METHODS_PATH = {
    'reader': os.path.join(BASE_DIR, 'installed-methods/reader.json'),
    'processing': os.path.join(BASE_DIR, 'installed-methods/processing.json')
}

ALLOWED_EXTENSIONS = set(['h5ad', 'csv', 'h5', 'loom', 'mtx', 'txt'] + [x[0] for x in get_archive_formats()])
UPLOAD_FOLDER = os.path.join(BASE_DIR, "datafile")

TEMP_FOLDER = os.path.join(BASE_DIR, "temp")
