from django import forms
from django.core.cache import cache

from .models import (
    Fab,
    Glass,
    PSModel,
    MPSType,
    LCType,
)

class CalculatorForm(forms.Form):
    fab = forms.ChoiceField(choices=Fab.choices)
    glass = forms.ChoiceField(choices=Glass.choices)
    ps_model = forms.ChoiceField(label='PS Model', choices=PSModel.choices)
    mps_type = forms.ChoiceField(label='MPS Type', choices=MPSType.choices)
    lc_type = forms.ChoiceField(label='LC Type', choices=LCType.choices)
    
    def calc(self):
        print(self.cleaned_data['fab'])
        print(self.cleaned_data['glass'])
        print(self.cleaned_data['ps_model'])
        print(self.cleaned_data['mps_type'])
        print(self.cleaned_data['lc_type'])