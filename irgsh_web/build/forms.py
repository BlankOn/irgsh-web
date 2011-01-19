from django import forms
from django.utils.translation import ugettext as _

from . import utils
from .models import Distribution, SOURCE_TYPE

class SpecificationForm(forms.Form):
    distribution = forms.ChoiceField(label=_('Distribution'),
                                     choices=())
    source = forms.CharField(label=_('Source URL'), max_length=255)
    source_type = forms.ChoiceField(label=_('Source Type'),
                                    choices=SOURCE_TYPE)
    source_opts = forms.CharField(label=_('Source Options'),
                                  max_length=255, required=False)
    orig = forms.CharField(label=_('Original URL'), max_length=255,
                           required=False)

    def __init__(self, *args, **kwargs):
        super(SpecificationForm, self).__init__(*args, **kwargs)

        distributions = [(dist.id, dist.name())
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
            utils.build_source_opts(data['source_type'],
                                    data['source_opts'])
        except ValueError, e:
            raise forms.ValidationError(str(e))

        return data['source_opts']

