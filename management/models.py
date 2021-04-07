from django.db import models


class Project(models.Model):

    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, unique=True)
    description = models.TextField(max_length=512, null=True, blank=True)

    def __str__(self):
        return self.name


class Channel(models.Model):

    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64)
    description = models.TextField(max_length=512, null=True, blank=True)
    project = models.ForeignKey(
        Project,
        related_name="channels",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["project"]
        unique_together = [
            ("slug", "project"),
        ]

    def __str__(self):
        return self.name


class Container(models.Model):

    slug = models.CharField(max_length=128)
    auth = models.CharField(max_length=2000, null=True, blank=True)
    hash = models.CharField(max_length=255)
    parameters = models.CharField(max_length=2000)
    project = models.ForeignKey(
        Project,
        related_name="containers",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    channel = models.ForeignKey(
        Channel,
        related_name="containers",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        ordering = ["slug"]
        unique_together = [
            ("slug", "project", "channel"),
        ]
