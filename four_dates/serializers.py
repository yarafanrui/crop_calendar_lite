from rest_framework import serializers

from .models import Country, FourDates


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name', )
        #fields = '__all__'


class FourDatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FourDates
        #fields = ('id',)
        fields = '__all__'
        depth = 2


