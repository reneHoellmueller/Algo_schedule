from rest_framework import serializers
from schedule.models import ShiftPreference, NonWorkingDay


class ShiftPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftPreference
        fields = ['start_time', 'end_time', 'day_of_week', 'preference_type']

    def create(self, validated_data):
        # Hier könnte eine zusätzliche Logik zum Setzen des `employee` eingefügt werden,
        return super().create(validated_data)


class NonWorkingDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = NonWorkingDay
        fields = ['id', 'date', 'note']
