from django.db import models
from django.forms import ModelForm, Textarea 
from django import forms 
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext as _
from irgsh_web.jobs.models import *

class JobForm(ModelForm):
    class Meta:
        model = Job 
        widgets = {
            "carbon_copy": Textarea(attrs={'cols': 80, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        self.fields['carbon_copy'].widget.attrs['cols'] = "80"
        self.fields['carbon_copy'].widget.attrs['rows'] = "3"

class TaskInlineFormSet(BaseInlineFormSet):
    def clean(self):
        count = 0
        
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
            except AttributeError:
                pass

        if count < 1:
            raise forms.ValidationError(_(u'You need to specify at least one task'))
