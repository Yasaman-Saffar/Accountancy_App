from django.shortcuts import render, redirect
from django.db import transaction
from django.http import JsonResponse
from decimal import Decimal
from django.contrib import messages

from .models import Item, TeamItem
from accounts.models import Team


def get_team_item_info(request):
    team_id = request.GET.get('team_id')
    try:
        team = Team.objects.get(id=team_id)
        team_item = TeamItem.objects.filter(team=team)
        
        data = []
        for t_item in team_item:
            if t_item.quantity != 0:
                data.append({
                    'item': t_item.item.name,
                    'quantity': t_item.quantity,
                })
                
        return JsonResponse({'items': data})
    except Team.DoesNotExist:
        return JsonResponse({'error': 'تیمی با این شناسه وجود ندارد'})

@transaction.atomic
def dealing_items(request):
    teams = Team.objects.all()
    items = Item.objects.all()
    
    if request.method == 'POST':
        
        if not items:
            messages.error(
                request,
                'هیچی کالایی برای خرید و فروش وجود ندارد',
                extra_tags='alert-danger'
            )
            return redirect('market:dealing_items')
        
        team_id = request.POST.get('team')
        operation = request.POST.get('operation')

        team = Team.objects.get(id=team_id)
        
        team_items = []
        results = []
        cart = []
        buyOrSell = []
        items_price = Decimal(0)
        
        # Calculating the money that must be paid
        for item in items:
            qty_str = request.POST.get(f'item_{item.id}')
            if not qty_str or int(qty_str) == 0:
                continue
            quantity = int(qty_str)
            subtotal = item.current_price * quantity
            cart.append((item, quantity, subtotal))
        
        items_price = sum(subtotal for _, _, subtotal in cart)
    
        if not cart:
            messages.error(request, "هیچ کالایی برای معامله انتخاب نشده است", extra_tags='alert-danger')
            return redirect('market:dealing_items')
        
        # ---------------- Buying ----------------
        if operation == 'buying':
            if team.bank_balance < items_price:
                messages.error(
                    request,
                    f'موجودی حساب گروه {team.team_number} برای خرید کالا (های) انتخابی کافی نیست',
                    extra_tags='alert-danger'
                )
                return redirect('market:dealing_items')
            
            for item, quantity, subtotal in cart:
                team_item, _ = TeamItem.objects.get_or_create(team=team, item=item)
                
                team_item.quantity += quantity
                team_items.append(team_item)
                buyOrSell.append(f'{quantity} عدد {item.name}')
                    
            team.bank_balance -= items_price
            TeamItem.objects.bulk_update(team_items, ['quantity'])
            team.save()
            
            items_str = '\n'.join(buyOrSell)
            messages.success(
                request,
                f"گروه {team.group_name} \n {items_str} \n خریداری کرد".replace("\n", "<br>"),
                extra_tags='alert-success'
            )

        # ---------------- Selling ----------------
        elif operation == 'selling':
            for item, quantity, subtotal in cart:
                try:
                    team_item = TeamItem.objects.get(team=team, item=item)
                except TeamItem.DoesNotExist:
                    messages.error(request, f"تیم {team.group_name} موجودی از {item.name} ندارد", extra_tags='alert-danger')
                    return redirect('market:dealing_items')
                
                if team_item.quantity < quantity:
                    messages.error(request,
                    f"تیم موجودی کافی از {item.name} ندارد",
                    extra_tags='alert-danger')
                    return redirect('market:dealing_items')
                
                team_item.quantity -= quantity
                team_items.append(team_item)
                buyOrSell.append(f'{quantity} عدد {item.name}')
                
            team.bank_balance += items_price
            TeamItem.objects.bulk_update(team_items, ['quantity'])
            team.save()
            
            items_str = '\n'.join(buyOrSell)
            messages.success(
                request,
                f"فروش \n {items_str} \n توسط تیم {team.group_name} انجام شد".replace("\n", "<br>"),
                extra_tags='alert-success'
            )

        return redirect('market:dealing_items')

    return render(request, 'market/dealing_items.html', {
        'teams': teams,
        'items': items,
    })

        
    
            