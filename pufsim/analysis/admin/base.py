from django.apps import apps
from django.contrib import admin, messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from base64 import b64encode
from functools import update_wrapper
from io import BytesIO
from matplotlib import pyplot as plt
import numpy as np
import puflib as pl

from .. import models


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


class AnalysisModelAdmin(admin.ModelAdmin):

    class Meta:
        abstract = True

    def get_queryset(self, *args, **kwargs):
        for model in apps.get_app_config('pufsim_analysis').get_models():
            model.check_pids()
        return super().get_queryset(*args, **kwargs)

    def operations(self, obj):
        ops = obj.get_operations()
        cls = obj.__class__.__name__.lower()
        rev = 'admin:{}_{}'
        link = '<a class="button" href="{}">{}</a>'
        html_opts = []
        for op in ops:
            html_opts.append(link.format(
                reverse(rev.format(cls, op.lower()), args=[obj.pk]), op
            ))
        return format_html(' '.join(html_opts))

    def get_list_url(self):
        app = self.model._meta.app_label
        cls = self.model.__name__.lower()
        return reverse(f'admin:{app}_{cls}_changelist')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = []
        cls_name = self.model.__name__.lower()
        for op in self.model.get_all_operations():
            op = op.lower()
            view = getattr(self, f'{op}_view', None)
            custom_urls.append(
                path(f'<int:pk>/{op}', view, name=f'{cls_name}_{op}')
            )
        return urls + custom_urls

    def showdata_view(self, request, **kwargs):
        return None

    def get_model_instance(self, request, **kwargs):
        model = self.model
        try:
            pk = kwargs['pk']
            obj = model.objects.get(pk=pk)
            r = (pk, obj)
        except KeyError:
            messages.add_message(request, messages.ERROR, 'no primary key')
            r = HttpResponseRedirect(self.get_list_url())
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'non-existant')
            r = HttpResponseRedirect(self.get_list_url())
        return r

    def run_view(self, request, **kwargs):
        inst = self.get_model_instance(request, **kwargs)
        if not type(inst) is tuple:
            return inst
        (pk, obj) = inst
        if obj.pid:
            messages.add_message(
                request,
                messages.WARNING,
                f'{obj} is already running',
            )
        else:
            obj.spawn()
            messages.add_message(
                request,
                messages.INFO,
                f'{obj} spawned'
            )
        return HttpResponseRedirect(self.get_list_url())

    def showdata_view(self, request, **kwargs):
        inst = self.get_model_instance(request, **kwargs)
        if not type(inst) is tuple:
            return inst
        (pk, obj) = inst
        data_display = obj.get_data_display()
        try:
            if data_display['type'] == 'message':
                messages.add_message(request, messages.SUCCESS, data_display['msg'])
                return HttpResponseRedirect(self.get_list_url())
            elif data_display['type'] == 'bar_graph':
                # get context for django admin template
                context = self.admin_site.each_context(request)
                context['opts'] = self.opts
                context['original'] = obj
                # get custom context for data renderer
                data = eval(data_display['data'])
                context['data_graph'] = bar_graph(data, top=data_display['graph_top'])
                context['data_raw'] = data
                return TemplateResponse(
                    request,
                    'pufsim_analysis/data_renderer.html',
                    context,
                )
        except KeyError:
            pass
        messages.add_message(request, messages.ERROR, 'model get_data_display not formatted properly')
        return HttpResponseRedirect(self.get_list_url())
