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


class NeighborPredictorAdmin(admin.ModelAdmin):
    list_filter = ()
    list_display = ('id',) + list_filter + ('distance', 'group', 'match_range', 'known_set_limit', 'number_of_pufs')
    search_fields = list_display

    fieldsets = (
        ('General', {'fields': ('distance', 'group', 'match_range', 'known_set_limit', 'number_of_pufs', 'data',)}),
    )
    readonly_fields = ('data',)


admin.site.register(models.PDF, PDFAdmin)
admin.site.register(models.PUFGenerator, PUFGeneratorAdmin)
admin.site.register(models.NeighborPredictor, NeighborPredictorAdmin)
