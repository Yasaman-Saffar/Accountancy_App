from django import forms
from .models import Team

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['group_name', 'members', 'team_number']
        labels = {
            'group_name' : 'نام گروه',
            'members': 'اعضای گروه',
            'team_number': 'شماره گروه',
        }
        widgets = {
            'group_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام گروه را وارد کنید'}),
            'members': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'نام اعضای گروه را وارد کنید'}),
            'team_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }