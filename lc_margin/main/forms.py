from django import forms
from django.core.cache import cache

import pandas as pd

from .models import (
    Fab,
    Glass,
    PSModel,
    MPSType,
    LCType,
)
from .tools.utils import LCMarginCalculator

class CalculatorForm(forms.Form):
    fab = forms.ChoiceField(choices=Fab.choices)
    glass = forms.ChoiceField(choices=Glass.choices)
    ps_model = forms.ChoiceField(label='PS Model', choices=PSModel.choices)
    mps_type = forms.ChoiceField(label='MPS Type', choices=MPSType.choices)
    lc_type = forms.ChoiceField(label='LC Type', choices=LCType.choices)
    others = forms.FileField(
        help_text='Excel file(.xlsx)',
        widget=forms.FileInput(attrs={'accept': '.xlsx'})
    )
    
    def calc(self):
        # print(self.cleaned_data['fab'])
        # print(self.cleaned_data['glass'])
        # print(self.cleaned_data['ps_model'])
        # print(self.cleaned_data['mps_type'])
        # print(self.cleaned_data['lc_type'])
        # print(self.cleaned_data['others'])
        
        calculator = LCMarginCalculator(
            self.cleaned_data['fab'],
            self.cleaned_data['glass'],
            self.cleaned_data['ps_model'],
            self.cleaned_data['mps_type'],
            self.cleaned_data['lc_type'],
            pd.read_excel(self.cleaned_data['others']),
        )
        
        cache.set('result', calculator.predict[0])
        cache.set('lc_margin', calculator.lc_margin)