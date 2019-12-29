from django.db import models
from settings.settings import UPLOAD_FOLDER


# Create your models here.
class DataFile(models.Model):
    source = models.CharField(max_length=10)
    name = models.CharField(max_length=256)
    path = models.FilePathField(path=UPLOAD_FOLDER, match=True, allow_folders=True)
    description = models.TextField()
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "path: {path}, " \
               "name: {name}, " \
               "modified: {modified}".format(path=self.path,
                                             name=self.name,
                                             modified=self.modified.strftime("%m/%d/%Y %H:%M:%S"))
