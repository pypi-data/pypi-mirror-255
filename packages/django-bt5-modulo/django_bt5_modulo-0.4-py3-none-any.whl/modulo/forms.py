from django import forms

from modulo.models import TestData


class TestDataForm(forms.ModelForm):
    departamentos = forms.ChoiceField(choices=(("Lima", "Lima"), ("Cajamarca", "Cajamarca")),
                                      widget=forms.RadioSelect(), required=False)
    search = forms.CharField(max_length=8, label='Search',widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'search', 'placeholder': 'Search'}), required=False)

    class Meta:
        model = TestData
        fields = ['name', 'is_enable']

    def __init__(self, *args, **kwargs):
        super(TestDataForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = "form-control"
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label
