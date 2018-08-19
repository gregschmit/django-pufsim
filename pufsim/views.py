try:
    from django.contrib import messages
except ImportError:
    pass
from django.views import generic, View
import puflib as pl
from . import models


def try_message(request, level, msg):
    try: messages.add_message(request, level, msg)
    except NameError: pass


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
        context['bitflip_analyzers_fields'] = ['id', 'puf_generator', 'base_challenge', 'number_of_pufs']
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


class PUFGeneratorUpdate(CRUDMixin, EnvironmentMixin, PUFGeneratorMixin, generic.UpdateView):
    form_header = 'Edit PUF Generator'


class PUFGeneratorDelete(CRUDMixin, EnvironmentMixin, PUFGeneratorMixin, generic.DeleteView):
    form_message = "Are you sure you want to delete PUF Generator {obj}?"
    form_submit = 'Delete'


class PUFGeneratorQuicktest(generic.RedirectView):

    def get_redirect_url(self, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            try_message(self.request, messages.ERROR, "quicktest failed: object not specified")
            return '/environment/'
        try:
            obj = models.PUFGenerator.objects.get(pk=pk)
        except:
            try_message(self.request, messages.ERROR, "quicktest failed: object not found")
            return '/environment/'
        res = obj.generate_puf().quicktest()
        msg = "puf from pufg{0}: challenge {1} returned [{2}], {3:.0%} of the time".format(kwargs['pk'], *res)
        try_message(self.request, messages.INFO, msg)
        return '/environment/'


# Bitflip Analyzer

class BitflipAnalyzerMixin:
    model = models.BitflipAnalyzer
    fields = ['puf_generator', 'base_challenge', 'number_of_pufs']
    label = 'Bitflip Analyzer'


class BitflipAnalyzerCreate(CRUDMixin, AnalysisMixin, BitflipAnalyzerMixin, generic.CreateView):
    form_header = 'Create Bitflip Analyzer'


class BitflipAnalyzerUpdate(CRUDMixin, AnalysisMixin, BitflipAnalyzerMixin, generic.UpdateView):
    form_header = 'Edit Bitflip Analyzer'


class BitflipAnalyzerDelete(CRUDMixin, AnalysisMixin, BitflipAnalyzerMixin, generic.DeleteView):
    form_message = "Are you sure you want to delete PUF Generator {obj}?"
    form_submit = 'Delete'

class BitflipAnalyzerRun(generic.TemplateView):
    model = models.BitflipAnalyzer
    template_name = 'pufsim/show_image.html'

    def analyze(self):
        data = self.model.object.get(self.kwargs.get('pk')).run()
        return data  # return image data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['imgsrc'] = self.analyze()
        context['header'] = 'Bitflip Analyzer'
        return context


# run 100 pufs and for each, 0000, 0100, 1100 and see how often each change
# challenge pair analyzer
