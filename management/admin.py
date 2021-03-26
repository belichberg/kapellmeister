from django.contrib import admin
from .models import Container, Project, Channel


@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'project', 'channel']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
