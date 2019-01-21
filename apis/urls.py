from . import views

from django.urls import path, include

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # The following URL can be deleted.
    # path('test/', views.TestView.as_view(), name='test'),

    # The following URL serves as a general entrance of data handling,
    # and should not be open to public.
    # GET, POST, PUT and DELETE methods are defined.
    # Uncomment when necessary.
    path('test-2/', csrf_exempt(views.TestView_2.as_view()), name='test_2'),

    # Uncomment the following line when necessary
    # path('load/', views.load_data, name='load'),

    # The following URL is a middle product
    # path('latlng2name/', views.latlng2name, name='latlng2name'),

    # The following URL can be deleted.
    # path('latlng2fourdates/', views.LatLng2FourDates.as_view(), name='latlng2fourdates'),

    # The following URL is the 'end product'
    path('latlng2fourdates-2/', views.LatLng2FourDates_2.as_view(), name='latlng2fourdates_2'),

    # The following is the doc.
    path('v0/', views.v0_doc, name='v0_doc'),

    # path('docs/', views.yaml2html, name='docs'),

    # maybe TODO ?
    # perhaps a nicer interface for admins to review the pending Create, Update
    # and Delete queue.
    # path('task_list/', views.task_list, name='task_list'),
]
