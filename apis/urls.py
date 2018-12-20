from . import views

from django.urls import path, include

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('test/', views.TestView.as_view(), name='test'),
    path('test-2/', csrf_exempt(views.TestView_2.as_view()), name='test_2'),

    path('load/', views.load_data, name='load'),

    #path('latlng2name/', views.latlng2name, name='latlng2name'),

    path('latlng2fourdates/', views.LatLng2FourDates.as_view(), name='latlng2fourdates'),
    path('latlng2fourdates-2/', views.LatLng2FourDates_2.as_view(), name='latlng2fourdates_2'),

    path('v0/', views.v0_doc, name='v0_doc'),

    #path('docs/', views.yaml2html, name='docs'),
]
