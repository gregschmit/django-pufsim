from django.contrib import admin

from .base import AnalysisModelAdmin
from .. import models


@admin.register(models.BitflipAnalyzer)
class BitflipAnalyzerAdmin(AnalysisModelAdmin):
    list_filter = ('puf_generator',)
    list_display = ('name', 'id', 'pid', 'progress',) + list_filter + ('base_challenge',
        'number_of_pufs', 'operations',)
    search_fields = ('id', 'pid', 'progress') + list_filter
    readonly_fields = ('data',)


@admin.register(models.ChallengePairAnalyzer)
class ChallengePairAnalyzerAdmin(AnalysisModelAdmin):
    list_filter = ('puf_generator',)
    list_display = ('name', 'id', 'pid', 'progress',) + list_filter + ('base_challenge',
        'test_challenge', 'number_of_pufs', 'operations',)
    search_fields = ('id', 'pid', 'progress') + list_filter
    readonly_fields = ('data',)


@admin.register(models.NeighborPredictor)
class NeighborPredictorAdmin(AnalysisModelAdmin):
    list_filter = ('puf_generator',)
    list_display = ('name', 'id', 'pid', 'progress',) + list_filter + ('k', 'distance',
        'known_set_limit', 'number_of_pufs', 'iterations_per_puf',
        'hop_by_power_of_two', 'operations',)
    search_fields = ('id', 'pid', 'progress') + list_filter
    readonly_fields = ('data',)


@admin.register(models.BiasTester)
class BiasTesterAdmin(AnalysisModelAdmin):
    list_filter = ('puf_type',)
    list_display = ('name', 'id', 'pid', 'progress',) + list_filter + ('puf_type',
        'puf_id', 'number_of_pufs', 'n', 'operations',)
    search_fields = ('id', 'pid', 'progress')
    readonly_fields = ('data',)
