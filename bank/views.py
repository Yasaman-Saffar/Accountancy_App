from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from decimal import Decimal

from .models import Question
from accounts.models import Team


def bank_home(request):
    return render(request, 'bank/bank_home.html')

def get_team_info(request):
    team_id = request.GET.get('team_id')
    try:
        team = Team.objects.get(id=team_id)
        data = {
            'name': team.group_name,
            'unsolved': team.unsolved_questions,
            'solved': team.solved_questions,
        }
        return JsonResponse(data)
    except Team.DoesNotExist:
        return JsonResponse({'error': 'تیمی با این شناسه وجود ندارد'})

@transaction.atomic
def buying_questions(request):
    teams = Team.objects.all()
    questions = Question.objects.all()
    
    if request.method == 'POST':
        team_id = request.POST.get('team')
        level = request.POST.get('level')
        
        team = Team.objects.get(id=team_id)
        team_balance = team.bank_balance
        question = Question.objects.get(level=level)
        price = question.buy_price
        

        if team_balance < price:
            messages.error(
                request,
                'موجودی گروه برای خرید سوال کافی نیست',
                extra_tags='alert-danger'
            )
            return redirect('bank:buying_questions')
        
        if question.stock <= 0:
            messages.error(
                request,
                'سؤالی در بانک موجود نیست',
                extra_tags='alert-danger'
            )
            return redirect('bank:buying_questions')
        

        # Apply changes
        team.bank_balance -= price
        team.unsolved_questions += 1
        team.save()

        question.stock -= 1
        question.save()

        messages.success(
            request,
            f" گروه {team.team_number} یک سؤال {question.get_level_display()} خرید.",
            extra_tags='alert-success'
        )
        return redirect('bank:buying_questions')
    
    return render(request, 'bank/buying_questions.html', {
        'teams': teams,
        'questions': questions,
    })
    

@transaction.atomic
def trading_questions(request):
    teams = Team.objects.all()
    questions = Question.objects.all()
    
    if request.method == 'POST':
        seller_team_id = request.POST.get('seller_team')
        recipient_team_id = request.POST.get('recipient_team')
        if seller_team_id == recipient_team_id:
            messages.error(
                request,
                f'گروه خریدار و فروشنده یکسان است',
                extra_tags='alert-danger'
            )
            return redirect('bank:trading_questions')
            
        consensual_price = Decimal(request.POST.get('consensual_price') or 0)

        seller_team = Team.objects.get(id=seller_team_id)
        recipient_team = Team.objects.get(id=recipient_team_id)
        recipient_balance = recipient_team.bank_balance
        
        if seller_team.unsolved_questions <= 0:
            messages.error(
                request,
                f'سؤال حل نشده‌ای در بانک گروه {recipient_team.team_number} موجود نیست.',
                extra_tags='alert-danger'
            )
            return redirect('bank:trading_questions')
        
        if recipient_balance < consensual_price:
            messages.error(
                request,
                'موجودی گروه خریدار برای خرید سوال کافی نیست',
                extra_tags='alert-danger'
            )
            return redirect('bank:trading_questions')
         
        
        recipient_team.bank_balance -= consensual_price
        recipient_team.unsolved_questions += 1
        
        seller_team.bank_balance += consensual_price
        seller_team.unsolved_questions -= 1
        
        recipient_team.save()
        seller_team.save()
        
        messages.success(
            request,
            f"گروه {seller_team.team_number} یک سؤال با قیمت {consensual_price} به گروه {recipient_team.team_number} فروخت.",
            extra_tags='alert-success'
        )
        return redirect('bank:trading_questions')
    
    return render(request, 'bank/trading_questions.html', {
        'teams': teams,
        'questions': questions,
    })
    

@transaction.atomic
def receive_award(request):
    teams = Team.objects.all()
    questions = Question.objects.all()
    
    if request.method == 'POST':
        team_id = request.POST.get('team')
        level = request.POST.get('level')
        
        team = Team.objects.get(id=team_id)
        question = Question.objects.get(level=level)
        price = question.sell_price
        
        if team.unsolved_questions == 0:
            messages.error(
                request,
                f"گروه {team.team_number} سوال حل نشده‌ای ندارد.",
                extra_tags='alert-danger'
            )
            return redirect('bank:receive_award')
            
        team.bank_balance += price
        team.solved_questions += 1
        team.unsolved_questions -= 1
        team.save()
        
        messages.success(
            request,
            f" گروه {team.team_number} جایزه یک سؤال {question.get_level_display()} را دریافت کرد.",
            extra_tags='alert-success'
        )
        return redirect('bank:receive_award')
        
    return render(request, 'bank/receive_award.html', {
        'teams': teams,
        'questions': questions,
    })