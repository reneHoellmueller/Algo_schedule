from datetime import datetime
from .models import Employee, Shift
import pulp


def save_shifts_to_database(prob, x, u, dienstplan, employee_id_to_idx):
    num_hours_per_day = len(x)
    num_days = len(x[0])
    num_employees = len(x[0][0])

    for h in range(num_hours_per_day):
        for d in range(num_days):
            for e in range(num_employees):
                if pulp.value(x[h][d][e]) == 1:
                    # Finde die entsprechende Mitarbeiter-ID
                    employee_id = [k for k, v in employee_id_to_idx.items() if v == e][0]

                    # Laden Sie das Mitarbeiterobjekt
                    employee = Employee.objects.get(id=employee_id)

                    # Erstellen Sie ein neues Schichtobjekt
                    shift = Shift(
                        dienstplan=dienstplan,
                        employee=employee,
                        start_time=datetime.time(datetime(2023, 1, 1, h)),
                        end_time=datetime.time(datetime(2023, 1, 1, h + 1)),
                        # Hier nehmen wir an, dass eine Schicht eine Stunde dauert
                        day_of_month=d + 1  # +1, weil d von 0 startet
                    )

                    # Speichern Sie das Schichtobjekt in der Datenbank
                    shift.save()
