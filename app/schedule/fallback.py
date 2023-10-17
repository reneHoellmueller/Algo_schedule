from .models import Employee, OpeningTime, ShiftPreference
from django.utils import timezone
import calendar
from django.db.models import Q
from datetime import datetime
import pulp


def generate_binary_schedule(year, month, club_id, employee_id_to_idx):
    opening_times = OpeningTime.objects.filter(club_id=club_id)
    employees = Employee.objects.filter(club_id=club_id)
    _, num_days = calendar.monthrange(year, month)

    # Initialisierung der binären Matrix
    num_employees = len(employee_id_to_idx)
    binary_schedule = [[[0] * num_employees for _ in range(num_days)] for _ in range(24)]

    shift_preferences = ShiftPreference.objects.filter(employee__in=employees)
    pref_dict = {}
    for pref in shift_preferences:
        if pref.employee_id not in pref_dict:
            pref_dict[pref.employee_id] = []
        pref_dict[pref.employee_id].append(pref)

    for day in range(1, num_days + 1):
        current_date = timezone.datetime(year, month, day)
        opening_time = opening_times.filter(
            Q(date=current_date) | Q(weekday=current_date.weekday())
        ).first()

        if not opening_time:
            continue

        for hour in range(24):
            if opening_time.opening_time.hour <= hour < opening_time.closing_time.hour:
                for employee in employees:
                    employee_idx = employee_id_to_idx.get(employee.id)

                    # Überprüfen der nicht-Verfügbarkeit
                    is_not_available = any(
                        pref.start_time.hour <= hour < pref.end_time.hour and
                        pref.day_of_week == current_date.weekday() and
                        pref.preference_type == 'N'
                        for pref in pref_dict.get(employee.id, [])
                    )

                    # Überprüfen der Verfügbarkeit
                    is_preferred = any(
                        pref.start_time.hour <= hour < pref.end_time.hour and
                        pref.day_of_week == current_date.weekday() and
                        pref.preference_type == 'P'
                        for pref in pref_dict.get(employee.id, [])
                    )

                    # Setzen der Matrixwerte basierend auf Verfügbarkeitsüberprüfungen
                    if not is_not_available and is_preferred and employee_idx is not None:
                        binary_schedule[hour][day - 1][employee_idx] = 1

    start_date = datetime(year, month, 1)
    return binary_schedule, start_date


def employee_scheduling(year, month, club_id, employee_id_to_idx, employee_weekly_hours, penalty, overtime_penalty, n,
                        max_blocks):
    binary_schedule, _ = generate_binary_schedule(year, month, club_id, employee_id_to_idx)

    num_days = len(binary_schedule[0])
    num_hours_per_day = len(binary_schedule)
    num_employees = len(binary_schedule[0][0])

    prob = pulp.LpProblem("EmployeeScheduling", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x", (range(num_hours_per_day), range(num_days), range(num_employees)), cat='Binary')
    u = pulp.LpVariable.dicts("u", (range(num_hours_per_day), range(num_days)), cat='Continuous', lowBound=0)
    o = pulp.LpVariable.dicts("o", range(num_employees), cat='Continuous', lowBound=0)

    y = pulp.LpVariable.dicts("y", (range(num_hours_per_day), range(num_days), range(num_employees)), cat='Binary')
    z = pulp.LpVariable.dicts("z", (range(num_days), range(num_employees)), cat='Binary')

    prob += (
            pulp.lpSum(
                x[h][d][e] for h in range(num_hours_per_day) for d in range(num_days) for e in range(num_employees)) +
            penalty * pulp.lpSum(u[h][d] for h in range(num_hours_per_day) for d in range(num_days)) +
            overtime_penalty * pulp.lpSum(o[e] for e in range(num_employees))
    ), "TotalCost"

    # Vorhandene Nebenbedingungen
    for h in range(num_hours_per_day):
        for d in range(num_days):
            for e in range(num_employees):
                prob += x[h][d][e] <= binary_schedule[h][d][e], f"Availability_H{h}_D{d}_E{e}"

    for e in range(num_employees):
        prob += (
                        pulp.lpSum(x[h][d][e] for h in range(num_hours_per_day) for d in range(num_days)) -
                        employee_weekly_hours[e]
                ) <= o[e], f"Overtime_E{e}"

    for h in range(num_hours_per_day):
        for d in range(num_days):
            prob += pulp.lpSum(x[h][d][e] for e in range(num_employees)) + u[h][d] >= 1, f"MinStaff_H{h}_D{d}"

    # Neue Nebenbedingungen
    for h in range(num_hours_per_day - n + 1):
        for d in range(num_days):
            for e in range(num_employees):
                prob += y[h][d][e] <= x[h][d][e], f"BlockStart_H{h}_D{d}_E{e}"
                for k in range(n):
                    prob += x[h + k][d][e] >= y[h][d][e], f"ContinuousWork_H{h}K{k}_D{d}_E{e}"

    for d in range(num_days):
        for e in range(num_employees):
            total_hours_worked_today = pulp.lpSum(x[h][d][e] for h in range(num_hours_per_day))
            prob += total_hours_worked_today >= n * z[d][e], f"MinHours_D{d}_E{e}"
            prob += total_hours_worked_today <= num_hours_per_day * z[d][e], f"MaxPossibleHours_D{d}_E{e}"
            prob += pulp.lpSum(y[h][d][e] for h in range(num_hours_per_day)) >= z[d][e], f"AnyBlock_D{d}_E{e}"

    prob.solve()

    print("Status:", pulp.LpStatus[prob.status])
    for h in range(num_hours_per_day):
        for d in range(num_days):
            for e in range(num_employees):
                if pulp.value(x[h][d][e]) == 1:
                    print(f"Mitarbeiter {e} arbeitet am Tag {d}, Stunde {h}")

    return prob, x, u
