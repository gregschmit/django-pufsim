from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.views.generic import RedirectView

from . import models


class PUFGeneratorQuicktest(RedirectView):
    """
    Perform the quicktest and add the message
    """

    def get_redirect_url(self, *args, **kwargs):
        try:
            obj = models.PUFGenerator.objects.get(pk=kwargs['pk'])
            res = obj.generate_puf().quicktest()
            msg = 'PUF from PUFGenerator[{}]: Challenge <b>{}</b> returned <b>{}</b> with <b>{:.0%}</b> frequency'.format(kwargs['pk'], *res)
            messages.add_message(self.request, messages.INFO, msg, extra_tags='safe')
        except KeyError:
            messages.add_message(self.request, messages.ERROR, "quicktest failed: object not specified")
        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.ERROR, "quicktest failed: object doesn't exist")
        return reverse('admin:pufsim_pufgenerator_changelist')
