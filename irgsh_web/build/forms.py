from django import forms

from . import utils
from .models import Distribution, SOURCE_TYPE

class SpecificationForm(forms.Form):
    distribution = forms.ChoiceField(choices=())
    source = forms.CharField(max_length=255)
    source_type = forms.ChoiceField(choices=SOURCE_TYPE)
    source_opts = forms.CharField(max_length=255, required=False)
    orig = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super(SpecificationForm, self).__init__(*args, **kwargs)

        distributions = [(dist.id, dist.name)
                         for dist in Distribution.objects.filter(active=True)]
        self.fields['distribution'].choices = distributions

    def clean_orig(self):
        value = self.cleaned_data['orig']

        if type(value) == str:
            value = value.strip()
            if len(value) == 0:
                value = None

        return value

    def clean_source_opts(self):
        data = self.cleaned_data

        source_opts = None
        try:
            source_opts = utils.build_source_opts(data['source_type'],
                                                  data['source_opts'])
        except ValueError, e:
            raise forms.ValidationError(str(e))

        return source_opts

