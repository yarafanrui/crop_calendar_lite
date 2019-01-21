from rest_framework import serializers

from background_task.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        #fields = ('id', 'name', )
        fields = '__all__'
        depth = 2


'''
class CompletedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedTask
        #fields = ('id',)
        fields = '__all__'
        depth = 2
'''

