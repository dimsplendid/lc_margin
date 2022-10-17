from django import forms
from django.core.cache import cache

import pandas as pd

from .tools.utils import liquid_crystal_margin_calculator

class BatchCalculatorForm(forms.Form):
    input_file = forms.FileField(
        help_text='Excel file(.xlsx)',
        widget=forms.FileInput(attrs={'accept': '.xlsx'})
    )
    
    def calc(self):
        input_data = pd.read_excel(self.cleaned_data['input_file'])
        cache.set('result', liquid_crystal_margin_calculator(input_data))