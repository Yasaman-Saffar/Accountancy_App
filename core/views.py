from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import CompetitionSetting
from .models import InflationPrice
from bank.models import Question
from market.models import Item
from accounts.models import Team

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin', False):
            return HttpResponseForbidden("شما به این صفحه دسترسی ندارید.")
        return view_func(request, *args, **kwargs)
    return wrapper


# inflation and interest functions
@admin_required
def apply_inflation_interest(request):
    inflation_done = False
    first_inflation_record = CompetitionSetting.objects.all().first()
    current_round = first_inflation_record.applied_round + 1
    total_rounds = first_inflation_record.total_inflation_rounds if first_inflation_record else 1
    
    if current_round > total_rounds:
        inflation_done = True
    first_interest_record = CompetitionSetting.objects.all().first()
    interest_rate = first_interest_record.bank_interest_rate
    return render(request, 'core/inflation&interest_apply.html', {'current_round' : current_round,
                                                                  'interest_rate' : interest_rate,
                                                                  'inflation_done' : inflation_done})
    
@admin_required
def apply_inflation_view(request):
    first_record = CompetitionSetting.objects.all().first()
    if not first_record:
        messages.warning(request, "هیچ تورمی تعریف نشده است", extra_tags='alert-danger')
        return redirect('core:home')
    
    current_round = first_record.applied_round + 1
    total_rounds = first_record.total_inflation_rounds if first_record else 1
    
    inflation_done = False
    
    if current_round > total_rounds:
        inflation_done = True
        
    if request.method == 'POST':
        items = list(Item.objects.all())
        applied_any = False
        for item in items:
            inf = InflationPrice.objects.filter(item=item, round_number=current_round).first()
            if inf:
                item.current_price = inf.price
                item.save()
                applied_any = True
        if applied_any:
            first_record.applied_round = current_round
            first_record.save()
            messages.success(request, f"تورم {current_round} با موفقیت اعمال شد", extra_tags='alert-success')
            return redirect('core:apply_inflation_interest')
        else:
            messages.warning(request, f"هیچ تورمی برای راند {current_round} پیدا نشد.", extra_tags='alert-danger')
            return redirect('core:apply_inflation_interest')

    return redirect('core:apply_inflation_interest')
    
def reset_inflation(request):
    if request.method == 'POST':
        # reseting round
        first_record = CompetitionSetting.objects.all().first()  
        if not first_record:
            messages.warning(request, "هیچ تورمی تعریف نشده است", extra_tags='alert-danger')
            return redirect('core:home')
        first_record.applied_round = 0
        first_record.save()
        
        reset_done = False
        #reseting items' prices
        items = list(Item.objects.all())
        for item in items:
            item.current_price = item.base_price
            reset_done = True
            item.save()
        if reset_done:
            messages.success(request, 'همۀ تورم ها برداشته شدند', extra_tags='alert-success')
            return redirect('core:apply_inflation_interest')
        
    return redirect('core:apply_inflation_interest')
    

@admin_required
def apply_interest_view(request):
    first_record = CompetitionSetting.objects.all().first()
    interest_rate = first_record.bank_interest_rate
    teams = list(Team.objects.all())
    
    if not interest_rate:
        messages.warning(request, f"درصد سودی وارد نشده است", extra_tags='alert-danger')
        return redirect('core:apply_interest')
    if not teams:
        messages.warning(request, f"تیمی وارد نشده است", extra_tags='alert-danger')
        return redirect('core:apply_inflation_interest')
    
    if request.method == 'POST':
        applied_any = False
        for team in teams:
            team_bank_balance = team.bank_balance
            team_bank_balance += team_bank_balance * (interest_rate/100)
            team.bank_balance = round(team_bank_balance, 0)
            team.save()
            applied_any = True
            
        if applied_any:
            messages.success(request, f"سود {interest_rate} درصد با موفقیت اعمال شد", extra_tags='alert-success')
        return redirect('core:apply_inflation_interest')
    
    return redirect('core:apply_inflation_interest')



# Authorization
def admin_or_user(request):
    request.session['is_admin'] = False
    request.session['is_banker'] = False
    return render(request, 'core/admin_or_user.html')

def admin_login(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == '4321nimda': 
            request.session['is_banker'] = False
            request.session['is_admin'] = True
            return redirect('core:Entry_page')
        else:
            return render(request, 'core/admin_login.html', {'error': 'رمز اشتباه است'})
    return render(request, 'core/admin_login.html')


def admin_logout(request):
    request.session['is_admin'] = False
    return redirect('core:admin_or_user')

def banker_login(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'banker6789': 
            request.session['is_admin'] = False
            request.session['is_banker'] = True
            return redirect('core:Entry_page')
        else:
            return render(request, 'core/admin_login.html', {'error': 'رمز اشتباه است'})
    return render(request, 'core/banker_login.html')


def banker_logout(request):
    request.session['is_banker'] = False
    return redirect('core:admin_or_user')


# main views
def Entry_page(request):
    return render(request, 'core/Entry_page.html')

def setting(request):
    return render(request, 'core/setting.html')

def Home(request):
    return render(request, 'core/Home.html')

# setting data
def setup_step1(request):
    setting = CompetitionSetting.objects.first()
    inflations = InflationPrice.objects.all()
    items = Item.objects.all()
    questions = Question.objects.all()
    is_admin = request.session.get('is_admin', False)
    
    if is_admin:
        if request.method == "POST":
            hours = request.POST.get('hours') or 0
            minutes = request.POST.get('minutes') or 0
            bank_rate = request.POST.get('bank_rate') or 0
            bank_interval = request.POST.get('bank_interval') or 0
            initial_capital = request.POST.get('initial_capital') or 0

            CompetitionSetting.objects.all().delete()

            CompetitionSetting.objects.create(
                duration_hours=int(hours),
                duration_minutes=int(minutes),
                bank_interest_rate=bank_rate,
                bank_interest_interval=bank_interval,
                initial_capital=initial_capital
            )
            return redirect('core:setup_step2')

        return render(request, 'core/step1_base.html', {
                'is_admin': True})
        
    return render(request, 'core/view_only.html', {
        'setting': setting,
        'inflations': inflations,
        'items': items,
        'questions': questions,
        'is_admin': False,
})


@admin_required
def setup_step2(request):
    levels = [('easy', 'سؤالات آسان'), ('medium', 'سؤالات متوسط'), ('hard', 'سؤالات سخت')]
    if request.method == "POST":
        Question.objects.all().delete()
        for level, _ in levels:
            Question.objects.create(
                level=level,
                stock=int(request.POST[f'count_{level}'] or 0),
                buy_price=int(request.POST[f'buy_{level}'] or 0),
                sell_price=int(request.POST[f'reward_{level}'] or 0),
            )
        return redirect('core:setup_step3')
    return render(request, 'core/step2_questions.html', {'levels': levels})

@admin_required
def setup_step3(request):
    if request.method == "POST":
        InflationPrice.objects.all().delete()
        Item.objects.all().delete()
        count = int(request.POST.get('count') or 0)
        for i in range(1, count + 1):
            name = request.POST.get(f'name_{i}', f'کالا {i}')
            price = request.POST.get(f'price_{i}', 0) or 0
            Item.objects.create(
                name=name,
                base_price=price,
                current_price=price
            )
        return redirect('core:setup_step4')
    return render(request, 'core/step3_items.html')

@admin_required
def setup_step4(request):
    items = Item.objects.all()
    if request.method == 'POST':
        
        InflationPrice.objects.all().delete()
        rounds = int(request.POST.get('rounds') or 0)
        
        obj = CompetitionSetting.objects.all().first()
        obj.total_inflation_rounds = rounds
        obj.save()
        
        for r in range(1, rounds + 1):
            for item in items:
                price = request.POST.get(f"price_{item.id}_{r}") or 0
                InflationPrice.objects.create(
                    item=item,
                    round_number=r,
                    price=price
                )
        return render(request, 'core/step4_inflation.html', {
            'items': items,
            'success': True})
    return render(request, 'core/step4_inflation.html', {'items': items})
