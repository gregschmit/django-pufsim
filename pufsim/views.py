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


def graph_histogram(data, bins=None, top=1):
    b = BytesIO()
    fig = plt.figure()
    print("range is {0} to {1}".format(0, top))
    plt.hist([x for x in range(len(data))], weights=data, bins=[x-0.5 for x in range(len(data)+1)], color='black', rwidth=0.5, ec='black')
    plt.ylim(0, top)
    plt.savefig(b, format='png')
    return 'data:image/png;base64, ' + b64encode(b.getvalue()).decode()


class Test(generic.TemplateView):
    template_name = 'pufsim/data_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = [np.random.randint(0, 8) for x in range(50)]
        image = graph_histogram(data, top=8)
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
        context['pdfs'] = models.PDF.objects.all()
        context['pdfs_fields'] = ['id', 'distribution', 'mean', 'sigma', 'lbound', 'rbound',]
        context['pufgs'] = models.PUFGenerator.objects.all()
        context['pufgs_fields'] = ['id', 'architecture', 'stages', 'production_pdf', 'sample_pdf', 'sensitivity',]
        return context


class Analysis(generic.TemplateView):
    """
    View for showing models in the statistical analysis.
    """
    template_name = 'pufsim/analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bitflip_analyzers'] = models.BitflipAnalyzer.objects.all()
        context['bitflip_analyzers_fields'] = ['id', 'puf_generator', 'base_challenge', 'number_of_pufs', 'progress', 'pid']
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
        try: messages.add_message(self.request, messages.SUCCESS, msg)
        except NameError: pass
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_header'] = getattr(self, 'form_header', '')
        context['form_message'] = getattr(self, 'form_message', '').format(obj=getattr(getattr(self, 'object', None), 'id', None))
        context['form_submit'] = getattr(self, 'form_submit', 'Submit')
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
    fields = ['distribution', 'mean', 'sigma', 'lbound', 'rbound',]


class PDFCreate(CRUDMixin, EnvironmentMixin, PDFMixin, generic.CreateView):
    form_header = 'Create PDF'


class PDFShow(CRUDMixin, EnvironmentMixin, PDFMixin, generic.DetailView):
    form_header = 'Show PDF'


class PDFUpdate(CRUDMixin, EnvironmentMixin, PDFMixin, generic.UpdateView):
    form_header = 'Edit PDF'


class PDFDelete(CRUDMixin, EnvironmentMixin, PDFMixin, generic.DeleteView):
    form_message = "Are you sure you want to delete PDF {obj}?"
    form_submit = 'Delete'


# PUFGenerator

class PUFGeneratorMixin:
    model = models.PUFGenerator
    fields = ['architecture', 'stages', 'production_pdf', 'sample_pdf', 'sensitivity']


class PUFGeneratorCreate(CRUDMixin, EnvironmentMixin, PUFGeneratorMixin, generic.CreateView):
    form_header = 'Create PUF Generator'


class PUFGeneratorShow(CRUDMixin, EnvironmentMixin, PUFGeneratorMixin, generic.DetailView):
    form_header = 'Show PUF Generator'


class PUFGeneratorUpdate(CRUDMixin, EnvironmentMixin, PUFGeneratorMixin, generic.UpdateView):
    form_header = 'Edit PUF Generator'


class PUFGeneratorDelete(CRUDMixin, EnvironmentMixin, PUFGeneratorMixin, generic.DeleteView):
    form_message = "Are you sure you want to delete PUF Generator {obj}?"
    form_submit = 'Delete'


class PUFGeneratorQuicktest(generic.RedirectView):

    def get_redirect_url(self, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            try: messages.add_message(self.request, messages.ERROR, "quicktest failed: object not specified")
            except NameError: pass
            return '/environment/'
        try:
            obj = models.PUFGenerator.objects.get(pk=pk)
        except:
            try: messages.add_message(self.request, messages.ERROR, "quicktest failed: object not found")
            except NameError: pass
            return '/environment/'
        res = obj.generate_puf().quicktest()
        msg = "puf from pufg{0}: challenge {1} returned [{2}], {3:.0%} of the time".format(kwargs['pk'], *res)
        try: messages.add_message(self.request, messages.INFO, msg)
        except NameError: pass
        return '/environment/'


# Bitflip Analyzer

class BitflipAnalyzerMixin:
    model = models.BitflipAnalyzer
    fields = ['puf_generator', 'base_challenge', 'number_of_pufs']
    label = 'Bitflip Analyzer'


class BitflipAnalyzerCreate(CRUDMixin, AnalysisMixin, BitflipAnalyzerMixin, generic.CreateView):
    form_header = 'Create Bitflip Analyzer'


class BitflipAnalyzerShow(generic.TemplateView):
    model = models.BitflipAnalyzer
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
            context['src'] = graph_histogram(data, top=obj.number_of_pufs)
            context['data'] = data
        return context


class BitflipAnalyzerUpdate(CRUDMixin, AnalysisMixin, BitflipAnalyzerMixin, generic.UpdateView):
    form_header = 'Edit Bitflip Analyzer'


class BitflipAnalyzerDelete(CRUDMixin, AnalysisMixin, BitflipAnalyzerMixin, generic.DeleteView):
    form_message = "Are you sure you want to delete PUF Generator {obj}?"
    form_submit = 'Delete'


class BitflipAnalyzerRun(generic.RedirectView):
    model = models.BitflipAnalyzer

    def get_redirect_url(self, *args, **kwargs):
        obj = self.model.objects.get(pk=self.kwargs.get('pk'))
        # if already running, throw notice
        if obj.pid:
            try: messages.add_message(self.request, messages.WARNING, "BitflipAnalyzer already running")
            except NameError: pass
            return '/analysis/'
        # if needed, spawn the running process & redirect
        obj.run_bg()
        try: messages.add_message(self.request, messages.INFO, "BitflipAnalyzer spawned; refresh to update progress")
        except NameError: pass
        return '/analysis/'


# run 100 pufs and for each, 0000, 0100, 1100 and see how often each change
# challenge pair analyzer
