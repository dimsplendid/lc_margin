from io import BytesIO
from typing import Any, Dict

import pandas as pd

from django.views.generic import FormView, View
from django.http import HttpResponse, HttpRequest, Http404
from django.urls import reverse_lazy
from django.core.cache import cache

from .forms import BatchCalculatorForm
from .models import Fab

from config.settings.base import TEMPLATES_DIRS
    
class TemplateDownload(View):
    
    def get(self,  request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # file_name = 'upload_template.xlsx'
        file_name = 'upload_batch.xlsx'
        file_path = TEMPLATES_DIRS / file_name
        with open(file_path, 'rb') as f:
            response = HttpResponse(
                f.read(),
                content_type="application/vnd.ms-excel",
            )
            response['Content-Disposition'] = f'attachment; filename={file_name}'
            return response
            
class BatchCalculatorView(FormView):
    template_name = 'form_generic.html'
    success_url = reverse_lazy('main:batch_calculator')
    form_class = BatchCalculatorForm
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'LC Margin Calculotor'
        context['download_path'] = reverse_lazy('main:template_download')
        context['submit'] = 'Calculate'
        result:Dict[Fab, pd.DataFrame] = cache.get('result')
        if result:
            for fab, data in result.items():
                if len(data) == 0:
                    continue
                context[f"result_{fab.label}"] = data[[
                    'Density',
                    '允壓量範圍(um)',
                    'LC Margin',
                ]].to_html(
                    float_format=lambda x: f'{x:.3f}',
                    classes=['table', 'table-hover', 'text-center', 'table-striped'],
                    justify='center',
                    index=False,
                    escape=False,
                )
                context['result_download'] = True
        
        
        return context
    
    def form_valid(self, form: BatchCalculatorForm) -> HttpResponse:
        form.calc()
        return super().form_valid(form)
    
class ResultDownloadView(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        result:Dict[Fab, pd.DataFrame] = cache.get('result')
        if not result:
            raise Http404
        with BytesIO() as b:
            writer = pd.ExcelWriter(b, engine='openpyxl')
            for fab, data in result.items():
                data.to_excel(writer, sheet_name=fab.label)
            writer.save()
            file_name = f'result.xlsx'
            response = HttpResponse(
                b.getvalue(),
                content_type="application/vnd.ms-excel",
            )
            response['Content-Disposition'] = f'attachment; filename={file_name}'
            return response
    