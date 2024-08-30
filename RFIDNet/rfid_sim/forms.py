from django import forms

from leaflet.forms.widgets import LeafletWidget

from .models import RFIDReader




class RFIDForm(forms.ModelForm):
    class Meta:
        model = RFIDReader
        fields = ('location', 'chip_class',)
        widgets = {
            'location': LeafletWidget(),
            'chip_class': forms.RadioSelect
            }