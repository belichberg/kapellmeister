from django.db import models


class Project(models.Model):

    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, unique=True)
    description = models.TextField(max_length=512, null=True, blank=True)

    def __str__(self):
        return self.name


class Channel(models.Model):

    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, unique=True)
    description = models.TextField(max_length=512, null=True, blank=True)
    project = models.ForeignKey(Project, related_name='channels', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Container(models.Model):

    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True)
    path = models.URLField(max_length=512, unique=True)
    auth = models.CharField(max_length=2000)
    hash = models.CharField(max_length=255)
    project = models.ForeignKey(Project, related_name='containers', null=True, blank=True, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, related_name='containers', null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name
