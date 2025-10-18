from django.shortcuts import render, redirect
from .forms import TeamForm

def add_new_group(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    
    else:
        form = TeamForm()
    return render(request, 'accounts/add_new_group.html', {'form':form})
