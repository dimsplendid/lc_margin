from typing import Any, Dict

from django.views.generic import FormView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.core.cache import cache

from .forms import CalculatorForm

class CalculatorView(FormView):
    template_name = 'form_generic.html'
    success_url = reverse_lazy('main:calculator')
    form_class = CalculatorForm
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'LC Margin Calculotor'
        context['submit'] = 'Calculate'
        context['result'] = cache.get('result')
        return context
    
    def form_valid(self, form: CalculatorForm) -> HttpResponse:
        form.calc()
        return super().form_valid(form)
    
    