from base64 import b64encode
try:
    from django.contrib import messages
except ImportError:
    pass
from django.views import generic, View
from io import BytesIO
from matplotlib import pyplot as plt
import numpy as np
import puflib as pl
from . import models


def bar_graph(data, top=1, title='', xlabel='', ylabel=''):
    b = BytesIO()
    fig, ax = plt.subplots()
    values = list(data.values())
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


class Test(generic.TemplateView):
    template_name = 'pufsim/data_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = [np.random.randint(0, 8) for x in range(50)]
        image = bar_graph(data, top=8)
        context['src'] = image
        return context


class Index(generic.TemplateView):
    template_name = 'pufsim/index.html'


class Environment(generic.TemplateView):
    """
    View for showing models in the environment.
    """
    template_name = 'pufsim/environment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pdf'] = models.PDF
        context['pdfs'] = models.PDF.objects.all()
        context['puf_generator'] = models.PUFGenerator
        context['puf_generators'] = models.PUFGenerator.objects.all()
        context['composite_puf_generator'] = models.CompositePUFGenerator
        context['composite_puf_generators'] = models.CompositePUFGenerator.objects.all()
        return context


class Analysis(generic.TemplateView):
    """
    View for showing models in the statistical analysis.
    """
    template_name = 'pufsim/analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        models.BitflipAnalyzer.check_pids()
        models.ChallengePairAnalyzer.check_pids()
        models.NeighborPredictor.check_pids()
        models.BiasTester.check_pids()
        context['bitflip_analyzer'] = models.BitflipAnalyzer
        context['bitflip_analyzers'] = models.BitflipAnalyzer.objects.all()
        context['challenge_pair_analyzer'] = models.ChallengePairAnalyzer
        context['challenge_pair_analyzers'] = models.ChallengePairAnalyzer.objects.all()
        context['neighbor_predictor'] = models.NeighborPredictor
        context['neighbor_predictors'] = models.NeighborPredictor.objects.all()
        context['bias_tester'] = models.BiasTester
        context['bias_testers'] = models.BiasTester.objects.all()
        return context


class CRUDMixin:
    """
    CRUD helper. Override `template_name` in show/display view.
    """
    template_name = 'pufsim/form.html'

    def get_success_url(self, **kwargs):
        o = self.model._meta.verbose_name
        try:
            msg = self.msg
        except AttributeError:
            if type(self).__bases__[-1] is generic.CreateView:
                msg = '{0} {1}'.format(o, 'created')
            elif type(self).__bases__[-1] is generic.UpdateView:
                msg = '{0} {1}'.format(o, 'updated')
            elif type(self).__bases__[-1] is generic.DeleteView:
                msg = '{0} {1}'.format(o, 'deleted')
            else:
                msg = 'action success'
        messages.add_message(self.request, messages.SUCCESS, msg)
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # determine if CreateView, DetailsView, UpdateView, or DeleteView
        name = self.model._meta.verbose_name
        if generic.CreateView in type(self).__bases__:
            form_header = "Create {0}".format(name)
            form_message = ''
            form_submit = 'Create'
        elif generic.UpdateView in type(self).__bases__:
            form_header = "Update {0}".format(name)
            form_message = ''
            form_submit = 'Update'
        elif generic.DetailView in type(self).__bases__:
            form_header = "Show {0}".format(name)
            form_message = ''
            form_submit = ''
        else:
            form_header = "Delete {0}".format(name)
            form_message = "Are you sure you want to delete {0} {1}?".format(name, getattr(getattr(self, 'object', None), 'id', None))
            form_submit = 'Delete'
        context['form_header'] = form_header
        context['form_message'] = form_message
        context['form_submit'] = form_submit
        return context


class EnvironmentMixin:
    """Helper for going back to environment."""
    success_url = '/environment/'


class AnalysisMixin:
    """Helper for going back to analysis."""
    success_url = '/analysis/'


# PDF

class PDFMixin:
    model = models.PDF
    fields = [x.name for x in model.get_edit_fields()]

class PDFCreate(CRUDMixin, EnvironmentMixin, PDFMixin, generic.CreateView): pass
class PDFShow(CRUDMixin, EnvironmentMixin, PDFMixin, generic.DetailView): pass
class PDFUpdate(CRUDMixin, EnvironmentMixin, PDFMixin, generic.UpdateView): pass
class PDFDelete(CRUDMixin, EnvironmentMixin, PDFMixin, generic.DeleteView): pass


# PUFGenerator

class PUFGeneratorMixin:
    model = models.PUFGenerator
    fields = [x.name for x in model.get_edit_fields()]

class PUFGeneratorCreate(CRUDMixin, EnvironmentMixin, PUFGeneratorMixin, generic.CreateView): pass
class PUFGeneratorShow(CRUDMixin, EnvironmentMixin, PUFGeneratorMixin, generic.DetailView): pass
class PUFGeneratorUpdate(CRUDMixin, EnvironmentMixin, PUFGeneratorMixin, generic.UpdateView): pass
class PUFGeneratorDelete(CRUDMixin, EnvironmentMixin, PUFGeneratorMixin, generic.DeleteView): pass

class PUFGeneratorQuicktest(generic.RedirectView):

    def get_redirect_url(self, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            messages.add_message(self.request, messages.ERROR, "quicktest failed: object not specified")
            return '/environment/'
        try:
            obj = models.PUFGenerator.objects.get(pk=pk)
        except:
            messages.add_message(self.request, messages.ERROR, "quicktest failed: object not found")
            return '/environment/'
        res = obj.generate_puf().quicktest()
        msg = "puf from pufg{0}: challenge {1} returned [{2}], {3:.0%} of the time".format(kwargs['pk'], *res)
        messages.add_message(self.request, messages.INFO, msg)
        return '/environment/'


# PUFGenerator

class CompositePUFGeneratorMixin:
    model = models.CompositePUFGenerator
    fields = [x.name for x in model.get_edit_fields()]

class CompositePUFGeneratorCreate(CRUDMixin, EnvironmentMixin, CompositePUFGeneratorMixin, generic.CreateView): pass
class CompositePUFGeneratorShow(CRUDMixin, EnvironmentMixin, CompositePUFGeneratorMixin, generic.DetailView): pass
class CompositePUFGeneratorUpdate(CRUDMixin, EnvironmentMixin, CompositePUFGeneratorMixin, generic.UpdateView): pass
class CompositePUFGeneratorDelete(CRUDMixin, EnvironmentMixin, CompositePUFGeneratorMixin, generic.DeleteView): pass


# Bitflip Analyzer

class BitflipAnalyzerMixin:
    model = models.BitflipAnalyzer
    fields = [x.name for x in model.get_edit_fields()]

class BitflipAnalyzerCreate(CRUDMixin, AnalysisMixin, BitflipAnalyzerMixin, generic.CreateView): pass

class BitflipAnalyzerShow(BitflipAnalyzerMixin, generic.TemplateView):
    template_name = 'pufsim/data_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.model.objects.get(pk=self.kwargs.get('pk'))
        data = eval(obj.data.encode())
        if obj.pid:
            context['header'] = 'Bitflip Analyzer'
            context['text'] = "Data not ready"
        else:
            context['header'] = 'Bitflip Analyzer'
            context['title'] = str(obj)
            context['src'] = bar_graph(data, top=obj.number_of_pufs)
            context['data'] = data
        return context

class BitflipAnalyzerUpdate(CRUDMixin, AnalysisMixin, BitflipAnalyzerMixin, generic.UpdateView): pass
class BitflipAnalyzerDelete(CRUDMixin, AnalysisMixin, BitflipAnalyzerMixin, generic.DeleteView): pass

class BitflipAnalyzerRun(generic.RedirectView):
    model = models.BitflipAnalyzer

    def get_redirect_url(self, *args, **kwargs):
        obj = self.model.objects.get(pk=self.kwargs.get('pk'))
        # if already running, throw notice
        if obj.pid:
            messages.add_message(self.request, messages.WARNING, "BitflipAnalyzer already running")
            return '/analysis/'
        # if needed, spawn the running process & redirect
        obj.spawn()
        messages.add_message(self.request, messages.INFO, "Bitflip Analyzer spawned; refresh to update progress")
        return '/analysis/'


# Challenge Pair Analyzer

class ChallengePairAnalyzerMixin:
    model = models.ChallengePairAnalyzer
    fields = [x.name for x in model.get_edit_fields()]

class ChallengePairAnalyzerCreate(CRUDMixin, AnalysisMixin, ChallengePairAnalyzerMixin, generic.CreateView): pass

class ChallengePairAnalyzerShow(ChallengePairAnalyzerMixin, generic.RedirectView):

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


class ChallengePairAnalyzerUpdate(CRUDMixin, AnalysisMixin, ChallengePairAnalyzerMixin, generic.UpdateView): pass
class ChallengePairAnalyzerDelete(CRUDMixin, AnalysisMixin, ChallengePairAnalyzerMixin, generic.DeleteView): pass

class ChallengePairAnalyzerRun(ChallengePairAnalyzerMixin, generic.RedirectView):

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

class NeighborPredictorMixin:
    model = models.NeighborPredictor
    fields = [x.name for x in model.get_edit_fields()]

class NeighborPredictorCreate(CRUDMixin, AnalysisMixin, NeighborPredictorMixin, generic.CreateView): pass

class NeighborPredictorShow(NeighborPredictorMixin, generic.TemplateView):
    template_name = 'pufsim/data_result.html'

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

class NeighborPredictorUpdate(CRUDMixin, AnalysisMixin, NeighborPredictorMixin, generic.UpdateView): pass
class NeighborPredictorDelete(CRUDMixin, AnalysisMixin, NeighborPredictorMixin, generic.DeleteView): pass

class NeighborPredictorRun(NeighborPredictorMixin, generic.RedirectView):

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

class BiasTesterMixin:
    model = models.BiasTester
    fields = [x.name for x in model.get_edit_fields()]

class BiasTesterCreate(CRUDMixin, AnalysisMixin, BiasTesterMixin, generic.CreateView): pass

class BiasTesterShow(BiasTesterMixin, generic.TemplateView):
    template_name = 'pufsim/data_result.html'

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


class BiasTesterUpdate(CRUDMixin, AnalysisMixin, BiasTesterMixin, generic.UpdateView): pass
class BiasTesterDelete(CRUDMixin, AnalysisMixin, BiasTesterMixin, generic.DeleteView): pass

class BiasTesterRun(BiasTesterMixin, generic.RedirectView):

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

class BiasTesterMaxAverage(generic.RedirectView):

    def get_redirect_url(self, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            messages.add_message(self.request, messages.ERROR, "object not specified")
            return '/analysis/'
        try:
            obj = models.BiasTester.objects.get(pk=pk)
        except:
            messages.add_message(self.request, messages.ERROR, "object not found")
            return '/analysis/'
        res = obj.max_average()
        if isinstance(res, str):
            messages.add_message(self.request, messages.ERROR, res)
        else:
            msg = "calculated bias: %{0}".format(res)
            messages.add_message(self.request, messages.INFO, msg)
        return '/analysis/'
