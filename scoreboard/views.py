# Accountancy_App/Accountancy_App/scoreboard/views.py
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.db.models import F, Window
from django.db.models.functions import DenseRank

from accounts.models import Team
from market.models import Item

def scoreboard(request):
    return render(request, 'scoreboard/scoreboard.html')

@require_GET
def scoreboard_data(request):
    teams = Team.objects.all()
    for team in teams:
        team.calculate_total_assets()

    teams_sorted = Team.objects.annotate(
        rank=Window(
            expression=DenseRank(),
            order_by=[F('total_assets').desc(), F('solved_questions').desc()]
        )
    ).order_by('rank')
    
    
    items = Item.objects.all()

    return render(request, 'scoreboard/data/scoreboard_table.html', {'teams': teams_sorted,
                                                                     'items' : items})
    
def items_data(request):
    items = Item.objects.all()
    return render(request, 'scoreboard/data/items_data.html', {'items' : items})