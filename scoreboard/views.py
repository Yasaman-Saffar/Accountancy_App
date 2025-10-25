# Accountancy_App/Accountancy_App/scoreboard/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from accounts.models import Team

def scoreboard(request):
    """
    صفحه‌ی اسکربرد اصلی — جدول داینامیک.
    """
    return render(request, 'scoreboard/scoreboard.html')


@require_GET
def scoreboard_data(request):
    """
    داده‌های جدول امتیازات.
    قبل از برگشت، total_assets و rank برای تمام تیم‌ها به‌روز می‌شود.
    """

    # گام 1: بروزرسانی total_assets و rank همه‌ی تیم‌ها
    teams = list(Team.objects.all())
    for team in teams:
        team.calculate_total_assets()  # محاسبه دارایی
        # اطمینان از اینکه rank هم همیشه به‌روز است (در صورت وجود منطق خاص)
        # اگر در مدل Team متد calculate_rank() دارید، صدا بزنید:
        if hasattr(team, "calculate_rank"):
            team.calculate_rank()
        team.save()

    # گام 2: مرتب‌سازی بر اساس rank (در صورتی که rank مساوی باشد، total_assets تعیین‌کننده است)
    teams_sorted = sorted(teams, key=lambda t: (t.rank, -float(t.total_assets)), reverse=False)

    # گام 3: ساخت خروجی JSON
    data = []
    for i, team in enumerate(teams_sorted, start=1):
        data.append({
            "rank": team.rank,
            "group_name": team.group_name,
            "team_number": team.team_number,
            "total_assets": str(team.total_assets),
        })

    return JsonResponse({"teams": data})
