# serializers.py
from rest_framework import serializers
from .models import Shift


class ShiftSerializer(serializers.ModelSerializer):
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    title = serializers.CharField(source='employee.first_name')
    color = serializers.CharField(source='employee.color')

    class Meta:
        model = Shift
        fields = ['title', 'start', 'end', 'color']

    def get_start(self, obj):
        # Construct full datetime string for start using the Dienstplan year and month
        year_month_str = f"{obj.dienstplan.year}-{str(obj.dienstplan.month).zfill(2)}"
        return f"{year_month_str}-{str(obj.day_of_month).zfill(2)}T{obj.start_time}"

    def get_end(self, obj):
        # Construct full datetime string for end using the Dienstplan year and month
        year_month_str = f"{obj.dienstplan.year}-{str(obj.dienstplan.month).zfill(2)}"
        return f"{year_month_str}-{str(obj.day_of_month).zfill(2)}T{obj.end_time}"


