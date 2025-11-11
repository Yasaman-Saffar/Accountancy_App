from django.shortcuts import render, redirect
from .forms import TeamForm
from core.models import CompetitionSetting
from django.contrib import messages


def add_new_group(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            setting = CompetitionSetting.objects.first()
            team.bank_balance = setting.initial_capital if setting else 0
            team.save()
            
            messages.success(
                request,
                f'گروه {team.group_name} با موفقیت افزوده شد',
                extra_tags='alert-success'
            )
            return redirect('account:add_new_group')
        else:
            messages.error(
                request,
                'لطفا خطا های فرم را برطرف کنید',
                extra_tags='alert-danger'
            )
    else:
        form = TeamForm()
    return render(request, 'accounts/add_new_group.html', {'form': form})
