from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from . import models


@admin.register(models.PDF)
class PDFAdmin(admin.ModelAdmin):
    list_filter = ('distribution',)
    list_display = ('name', 'id',) + list_filter + ('mean', 'sigma', 'lbound', 'rbound')
    search_fields = list_display


@admin.register(models.PUFGenerator)
class PUFGeneratorAdmin(admin.ModelAdmin):
    list_filter = ('architecture',)
    list_display = ('name', 'id',) + list_filter + ('stages', 'production_pdf', 'sample_pdf', 'operations')
    search_fields = list_display

    def operations(self, obj):
        return format_html(
            '<a class="button" href="{}">Quicktest</a>',
            reverse('pufgenerator_quicktest', args=[obj.pk]),
        )


@admin.register(models.CompositePUFGenerator)
class CompositePUFGeneratorAdmin(admin.ModelAdmin):
    list_filter = ('architecture', 'child_architecture')
    list_display = ('name', 'id',) + list_filter + ('levels',)
    search_fields = list_display
