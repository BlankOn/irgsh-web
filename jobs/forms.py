from django.db import models
from django.forms import ModelForm
from django import forms 
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext as _
from jobs.models import *

class JobForm(ModelForm):
    class Meta:
        model = Job 

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
