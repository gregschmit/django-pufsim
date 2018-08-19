from django.contrib import admin
from . import models


class PDFAdmin(admin.ModelAdmin):
    list_filter = ('distribution',)
    list_display = ('id',) + list_filter + ('mean', 'sigma', 'lbound', 'rbound')
    search_fields = list_display

    fieldsets = (
        ('Setup', {'fields': ('distribution', 'mean', 'sigma', 'lbound', 'rbound',)}),
    )


class PUFGeneratorAdmin(admin.ModelAdmin):
    list_filter = ('architecture',)
    list_display = ('id',) + list_filter + ('stages', 'production_pdf', 'sample_pdf',)
    search_fields = list_display

    fieldsets = (
        ('Setup', {'fields': ('architecture', 'stages', 'production_pdf', 'sample_pdf',)}),
    )


admin.site.register(models.PDF, PDFAdmin)
admin.site.register(models.PUFGenerator, PUFGeneratorAdmin)
