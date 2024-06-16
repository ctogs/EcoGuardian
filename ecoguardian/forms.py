from django import forms
from django.utils import timezone
from .models import IncidentCategory, IncidentReport
from django.forms import ModelForm

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class IncidentReportForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea)
    location = forms.CharField(required=False)
    date = forms.DateField(widget=forms.SelectDateWidget)
    incident_categories = forms.MultipleChoiceField(
        choices=IncidentCategory.CATEGORY_CHOICES,
        widget=forms.SelectMultiple,
        required=False,
        label='Incident category'
    )
    # evidence = forms.FileField(widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}), required=False)
    evidence = MultipleFileField()

    def __init__(self, *args, **kwargs):
        initial_date = kwargs.pop('initial_date', None)
        super(IncidentReportForm, self).__init__(*args, **kwargs)
        if initial_date:
            self.initial['date'] = initial_date

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError("The date cannot be in the future. Please choose a valid date.")
        return date

class AdminDescriptionForm(ModelForm):
    class Meta:
        model = IncidentReport
        fields = ['admin_description', 'status']
        widgets = {
            'admin_description': forms.Textarea(attrs={'rows': 6, 'cols': 40, 'class': 'form-control'}),
        }
