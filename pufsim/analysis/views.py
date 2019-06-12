from base64 import b64encode
from django.urls import reverse
from django.views import generic, View
from io import BytesIO
from matplotlib import pyplot as plt
import numpy as np
import puflib as pl
from . import models


def bar_graph(data, top=1, title='', xlabel='', ylabel=''):
    b = BytesIO()
    fig, ax = plt.subplots()
    values = list(filter(lambda x: isinstance(x, (int, float)), data.values()))
    indices = list(range(len(values)))
    bar_width = 0.4
    bar = ax.bar(indices, values, bar_width, color='black')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(indices)
    ax.set_xticklabels([str(x) for x in data.keys()])
    fig.tight_layout()
    plt.ylim(0, top)
    plt.savefig(b, format='png')
    return 'data:image/png;base64, ' + b64encode(b.getvalue()).decode()


class AnalysisMixin:
    """Helper for going back to analysis."""

    @property
    def listing_url(self):
        app = self.model._meta.app_label
        cls = self.model.__name__.lower()
        return reverse(f'admin:{app}_{cls}_changelist')

# Challenge Pair Analyzer

class ChallengePairAnalyzerShowData(AnalysisMixin, generic.RedirectView):
    model = models.ChallengePairAnalyzer

    def get_redirect_url(self, *args, **kwargs):
        obj = self.model.objects.get(pk=self.kwargs.get('pk'))
        try:
            data = int(obj.data)
            percent = 100 * (data / obj.number_of_pufs)
        except ValueError:
            messages.add_message(self.request, messages.WARNING, "ChallengePairAnalyzer not done running")
            return '/analysis/'
        if obj.pid:
            messages.add_message(self.request, messages.WARNING, "ChallengePairAnalyzer not done running")
            return '/analysis/'
        messages.add_message(self.request, messages.SUCCESS, "ChallengePairAnalyzer returned {0}, or {1}%".format(data, percent))
        return '/analysis/'


class ChallengePairAnalyzerRun(AnalysisMixin, generic.RedirectView):
    model = models.ChallengePairAnalyzer

    def get_redirect_url(self, *args, **kwargs):
        obj = self.model.objects.get(pk=self.kwargs.get('pk'))
        # if already running, throw notice
        if obj.pid:
            messages.add_message(self.request, messages.WARNING, "ChallengePairAnalyzer already running")
            return '/analysis/'
        # if needed, spawn the running process & redirect
        obj.spawn()
        messages.add_message(self.request, messages.INFO, "ChallengePairAnalyzer spawned; refresh to update progress")
        return '/analysis/'


# Neighbor Predictor

class NeighborPredictorShowData(AnalysisMixin, generic.TemplateView):
    model = models.NeighborPredictor
    template_name = 'pufsim_analysis/data_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.model.objects.get(pk=self.kwargs.get('pk'))
        data = eval(obj.data.encode())
        if obj.pid:
            context['header'] = 'Neighbor Predictor'
            context['text'] = "Data not ready"
        else:
            context['header'] = 'Neighbor Predictor'
            context['title'] = str(obj)
            context['src'] = bar_graph(data, top=100)
            context['data'] = data
        return context


class NeighborPredictorRun(AnalysisMixin, generic.RedirectView):
    model = models.NeighborPredictor

    def get_redirect_url(self, *args, **kwargs):
        obj = self.model.objects.get(pk=self.kwargs.get('pk'))
        # if already running, throw notice
        if obj.pid:
            messages.add_message(self.request, messages.WARNING, "NeighborPredictorAnalyzer already running")
            return '/analysis/'
        # if needed, spawn the running process & redirect
        obj.spawn()
        messages.add_message(self.request, messages.INFO, "NeighborPredictor spawned; refresh to update progress")
        return '/analysis/'


# Bias Tester Analyzer

class BiasTesterShowData(AnalysisMixin, generic.TemplateView):
    model = models.BiasTester
    template_name = 'pufsim_analysis/data_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.model.objects.get(pk=self.kwargs.get('pk'))
        data = eval(obj.data.encode())
        if obj.pid:
            context['header'] = 'Bias Tester'
            context['text'] = "Data not ready"
        else:
            context['header'] = 'Bias Tester'
            context['title'] = str(obj)
            context['src'] = bar_graph(data, top=100)
            context['data'] = data
        return context


class BiasTesterRun(AnalysisMixin, generic.RedirectView):
    model = models.BiasTester

    def get_redirect_url(self, *args, **kwargs):
        obj = self.model.objects.get(pk=self.kwargs.get('pk'))
        # if already running, throw notice
        if obj.pid:
            messages.add_message(self.request, messages.WARNING, "BiasTester already running")
            return '/analysis/'
        # if needed, spawn the running process & redirect
        obj.spawn()
        messages.add_message(self.request, messages.INFO, "BiasTester spawned; refresh to update progress")
        return '/analysis/'
