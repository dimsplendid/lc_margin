from typing import Any, Dict

from django.views.generic import FormView, View
from django.http import HttpResponse, HttpRequest, Http404
from django.urls import reverse_lazy
from django.core.cache import cache

from .forms import CalculatorForm
from config.settings.base import TEMPLATES_DIRS

class CalculatorView(FormView):
    template_name = 'form_generic.html'
    success_url = reverse_lazy('main:calculator')
    form_class = CalculatorForm
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'LC Margin Calculotor'
        context['download_path'] = reverse_lazy('main:download')
        context['submit'] = 'Calculate'
        context['result'] = cache.get('result')
        context['lc_margin'] = cache.get('lc_margin')
        return context
    
    def form_valid(self, form: CalculatorForm) -> HttpResponse:
        form.calc()
        return super().form_valid(form)
    
class SampleDownload(View):
    
    def get(self,  request: HttpRequest, *args, **kwargs) -> HttpResponse:
        file_name = 'upload_template.xlsx'
        file_path = TEMPLATES_DIRS / file_name
        with open(file_path, 'rb') as f:
            response = HttpResponse(
                f.read(),
                content_type="application/vnd.ms-excel",
            )
            response['Content-Disposition'] = f'attachment; filename={file_name}'
            return response
        raise Http404
            
    