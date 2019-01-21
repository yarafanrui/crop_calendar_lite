# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from four_dates.serializers import LocationSerializer, FourDatesSerializer
from .serializers import TaskSerializer

from django.db.models.fields.related import ForeignKey
from django.db.models import CharField, DecimalField, IntegerField
from django.apps import apps

from background_task.models import Task

from . import crud

import json


class TestView(APIView):

    def get(self, request, ):

        installed_apps = ['four_dates']
        try:
            app_name = request.GET['app']
            class_name = request.GET['class']
        except:
            return Response([])

        # If this app is not installed then return a []
        if app_name not in installed_apps:
            return Response([])

        # Get all models under that app
        data_models = apps.get_app_config(app_name).get_models()

        # Get the model name passed through URL with the key "class"
        # If request.GET['class'] does not exist, return a []

        for data_model in data_models:
            if data_model.__name__ == class_name:
                data_model_to_return = data_model
                break

        try:
            data_model_to_return
        except NameError:
            return Response([])

        # Get fields with the given model.
        fields = data_model_to_return._meta.fields

        field_names = [field.name if not isinstance(field, ForeignKey) else field.name + '_id' for field in fields]

        key_words = {}
        for item in request.GET:
            if item == "class":
                continue

            if item == "app":
                continue

            if item not in field_names:
                return Response([])

            '''
            "_id" indicates a ForeignKey.

            IntegerField, FloatField, CharField... 

            '''
            if "_id" in str(item):
                key_words[item] = int(request.GET[item])
            else:
                if isinstance(fields[field_names.index(item)], IntegerField):
                    key_words[item] = int(request.GET[item])
                elif isinstance(fields[field_names.index(item)], DecimalField):
                    key_words[item] = float(request.GET[item])
                else:
                    key_words[item] = str(request.GET[item])

        try:
            objList = data_model_to_return.objects.filter(**key_words)
        except:
            objList = []

        if data_model_to_return.__name__ in ['SubRegion', 'Country']:
            ser = LocationSerializer(objList, many=True)
        else:
            ser = FourDatesSerializer(objList, many=True)

        return Response(ser.data)


class TestView_2(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, ):

        key_words = {}
        for item in request.GET:
            key_words[item] = request.GET[item]

        obj_list = crud.retrieve_list(**key_words)

        if obj_list.model.__name__ in ['Country']:
            ser = LocationSerializer(obj_list, many=True)

        elif obj_list.model.__name__ in ['Task']:
            ser = TaskSerializer(obj_list, many=True)

        else:
            ser = FourDatesSerializer(obj_list, many=True)

        return Response(ser.data)

    def post(self, request, ):

        import json

        info_received = json.loads(request.body)

        # test_background()
        #pending_thing(info_received)
        crud.create_one(**info_received)
        return JsonResponse({"info": "pending creating"})

    def put(self, request, ):
        import json

        info_received = json.loads(request.body)

        crud.update_one(**info_received)
        return JsonResponse({"info": "pending updating"})

    def delete(self, request, ):
        import json

        info_received = json.loads(request.body)

        crud.delete_one(**info_received)
        return JsonResponse({"info": "pending deleting"})


'''
def yaml2html(request):
    import yaml, json, sys

    with open('templates/test.yaml', 'r') as stream:
        try:
            yaml_string = json.dumps(yaml.load(stream))

        except yaml.YAMLError as e:
            print(e)
            return HttpResponse("Error!")

    return render(request, 'yaml-template.html', {'yaml_string': yaml_string})

'''

def load_data(request):

    from helperScripts import load_crop_calendar_lite

    load_crop_calendar_lite.load()

    return HttpResponse("Finished Loading!")


def latlng2name(request):

    import psycopg2

    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))

    except:
        return HttpResponse("Invalid lat-lng!")

    keyword_args = {
        "host": "localhost",
        "port": "5432",
        "dbname": "gadm",
        "user": "postgres",
        "password": "postgres"
    }

    with psycopg2.connect(**keyword_args) as conn:

        sql_1 = "SELECT * FROM level1 WHERE ST_Intersects(geom, ST_SetSRID(ST_MakePoint(%f, %f), 4326));" % (lng, lat)

        print(sql_1)

        cursor_1 = conn.cursor()
        cursor_1.execute(sql_1)

        # rows = cursor_1.fetchall()
        row = cursor_1.fetchone()

        json_to_return = {}

        json_to_return["country_name"] = str(row[2])
        json_to_return["sub_region_name"] = str(row[4])

    return JsonResponse(json_to_return)


def latlng2name_basic(lat, lng):
    import psycopg2

    """
    lat, lng should be float.
    """

    keyword_args = {
        "host": "localhost",
        "port": "5432",
        "dbname": "gadm",
        "user": "postgres",
        "password": "postgres"
    }

    with psycopg2.connect(**keyword_args) as conn:

        sql_1 = "SELECT * FROM level1 WHERE ST_Intersects(geom, ST_SetSRID(ST_MakePoint(%f, %f), 4326));" % (lng, lat)

        print(sql_1)

        cursor_1 = conn.cursor()
        cursor_1.execute(sql_1)

        row = cursor_1.fetchone()

        if row == None:
            return {}

        json_to_return = {}

        json_to_return["alpha_3_code"] = str(row[1])
        json_to_return["country_name"] = str(row[2])
        json_to_return["sub_region_name"] = str(row[4])

    return json_to_return


class LatLng2FourDates(APIView):

    def get(self, request, ):

        try:
            lat = float(request.GET.get('lat'))
            lng = float(request.GET.get('lng'))

        except:
            return HttpResponse("Invalid lat-lng!")

        data_fetched = latlng2name_basic(lat, lng)
        try:
            country_name = data_fetched["country_name"]
            sub_region_name = data_fetched["sub_region_name"]
            alpha_3_code = data_fetched["alpha_3_code"]
        except:
            return HttpResponse("Lat-Lng invalid.")

        print("country_name: " + country_name)
        print("alpha_3_code: " + alpha_3_code)

        from four_dates.models import Country, SubRegion, FourDates

        # Look Up for the Country
        try:
            country = Country.objects.get(name=country_name)
        except:
            try:
                country = Country.objects.get(alpha_3_code=alpha_3_code)
            except:
                return HttpResponse("Country Not Found")

        # Look up for the sub-region
        try:
            sub_region = SubRegion.objects.get(name=sub_region_name, country=country)
        except:
            sub_region = SubRegion.objects.filter(country=country)[0]

        print("sub_region.name: " + sub_region.name)
        try:
            four_dates_list = FourDates.objects.filter(sub_region=sub_region)
        except:
            four_dates_list = []

        ser = FourDatesSerializer(four_dates_list, many=True)

        return Response(ser.data)


def general_query(**kwargs):
    installed_apps = ['four_dates']

    try:
        app_name = kwargs['app']
        class_name = kwargs['class']
    except:
        return []

    #print("app: " + app_name)
    #print("class: " + class_name)

    # If this app is not installed then return a []
    if app_name not in installed_apps:
        return []

    # Get all models under that app
    data_models = apps.get_app_config(app_name).get_models()

    # Get the model name passed through URL with the key "class"
    # If kwargs['class'] does not exist, return a []
    #print("data_models. ")
    for data_model in data_models:
        if data_model.__name__ == class_name:
            data_model_to_return = data_model
            break

    try:
        data_model_to_return
    except NameError:
        return Response([])

    # Get fields with the given model.
    fields = data_model_to_return._meta.fields

    field_names = [field.name if not isinstance(field, ForeignKey) else field.name + '_id' for field in fields]

    key_words = {}
    for item in kwargs:
        if item == "class":
            continue

        if item == "app":
            continue

        if item not in field_names:
            return []

        '''
        "_id" indicates a ForeignKey.

        IntegerField, FloatField, CharField... 

        '''
        if "_id" in str(item):
            key_words[item] = int(kwargs[item])
        else:
            if isinstance(fields[field_names.index(item)], IntegerField):
                key_words[item] = int(kwargs[item])
            elif isinstance(fields[field_names.index(item)], DecimalField):
                key_words[item] = float(kwargs[item])
            else:
                key_words[item] = str(kwargs[item])

    try:
        objList = data_model_to_return.objects.filter(**key_words)
    except:
        objList = []

    return objList


class LatLng2FourDates_2(APIView):

    def get(self, request, ):
        try:
            lat = float(request.GET.get('lat'))
            lng = float(request.GET.get('lng'))

            print("lat: " + str(lat))
            print("lng: " + str(lng))
        except:
            return HttpResponse("Invalid lat-lng!")

        data_fetched = latlng2name_basic(lat, lng)

        try:
            country_name = data_fetched["country_name"]
            sub_region_name = data_fetched["sub_region_name"]
            alpha_3_code = data_fetched["alpha_3_code"]
        except:
            return HttpResponse("Lat-Lng invalid.")

        print("country_name: " + country_name)
        print("alpha_3_code: " + alpha_3_code)


        # Look Up for the Country
        try:
            kw = {"app": "four_dates",
                  "class": "Country",
                  "name": country_name}

            country = general_query(**kw)
            print(country)
            country = country[0]

            print("Country Found")
        except:
            try:
                kw = {"app": "four_dates",
                      "class": "Country",
                      "alpha_3_code": alpha_3_code}
                country = general_query(**kw)[0]

            except:
                return HttpResponse("Country Not Found")

        # Look up for the sub-region
        try:
            kw = {"app": "four_dates", "class": "SubRegion", "name": sub_region_name}
            sub_region = general_query(**kw)[0]
        except:
            kw = {"app": "four_dates", "class": "SubRegion", "country_id": country.id}
            sub_region = general_query(**kw)[0]

        # print("sub_region.name: " + sub_region.name)

        # get four_dates for sub-region
        try:
            kw = {"app": "four_dates", "class": "FourDates", "sub_region_id": sub_region.id}
            four_dates_list = general_query(**kw)
        except:
            four_dates_list = []

        # Look up four_dates_list_2 for sub-region "Country - ALL"
        try:
            kw = {"app": "four_dates", "class": "SubRegion", "name": country.name + " - ALL"}
            sub_region_country_all = general_query(**kw)[0]
            kw = {"app": "four_dates", "class": "FourDates", "sub_region_id": sub_region_country_all.id}
            four_dates_list_2 = general_query(**kw)
        except:
            four_dates_list_2 = []

        # Important: This is the way to combine QuerySet in Django
        four_dates_list = four_dates_list | four_dates_list_2

        ser = FourDatesSerializer(four_dates_list, many=True)

        return Response(ser.data)

    def post(self, request, ):
        import json

        info_received = json.loads(request.body)

        try:
            lat = float(info_received['data']['lat'])
            lng = float(info_received['data']['lng'])

            crop_name = str(info_received['data']['crop_name'])

            print("lat: " + str(lat))
            print("lng: " + str(lng))
        except:
            return HttpResponse("Invalid lat-lng!")

        data_fetched = latlng2name_basic(lat, lng)

        try:
            country_name = data_fetched["country_name"]
            sub_region_name = data_fetched["sub_region_name"]
            alpha_3_code = data_fetched["alpha_3_code"]
        except:
            return HttpResponse("Lat-Lng invalid.")

        print("country_name: " + country_name)
        print("alpha_3_code: " + alpha_3_code)

        # Look Up for the Country
        try:
            kw = {"app": "four_dates",
                  "class": "Country",
                  "name": country_name}

            country = general_query(**kw)
            print(country)
            country = country[0]

            print("Country Found")
        except:
            try:
                kw = {"app": "four_dates",
                      "class": "Country",
                      "alpha_3_code": alpha_3_code}
                country = general_query(**kw)[0]

            except:
                return HttpResponse("Country Not Found")

        # Look up for the sub-region
        try:
            kw = {"app": "four_dates", "class": "SubRegion", "name": sub_region_name}
            sub_region = general_query(**kw)[0]
        except:
            kw = {"app": "four_dates", "class": "SubRegion", "country_id": country.id}
            sub_region = general_query(**kw)[0]

        print("sub_region.name: " + sub_region.name)

        # Look up for the Crop
        try:
            kw = {"app": "four_dates", "class": "Crop", "name": crop_name}
            crop = general_query(**kw)[0]
        except:
            return HttpResponse("Crop Not Found")

        # Create new FourDate Record
        kw = {"app": "four_dates", "class": "FourDates", "data": {}}
        kw["data"]["plant_start"] = info_received["data"]["plant_start"]
        kw["data"]["plant_end"] = info_received["data"]["plant_end"]
        kw["data"]["harvest_start"] = info_received["data"]["harvest_start"]
        kw["data"]["harvest_end"] = info_received["data"]["harvest_end"]
        kw["data"]["sub_region_id"] = sub_region.id
        kw["data"]["crop_id"] = crop.id

        crud.create_one(**kw)
        return JsonResponse({"info": "pending creating"})

    def put(self, request, ):
        import json

        info_received = json.loads(request.body)

        kw = info_received
        kw["app"] = "four_dates"
        kw["class"] = "FourDates"

        crud.update_one(**kw)
        return JsonResponse({"info": "pending updating"})

    def delete(self, request, ):
        import json

        info_received = json.loads(request.body)
        kw = info_received
        kw["app"] = "four_dates"
        kw["class"] = "FourDates"

        crud.delete_one(**info_received)
        return JsonResponse({"info": "pending deleting"})


def v0_doc(request):
    import yaml, json

    with open('templates/v0.yaml', 'r') as stream:
        try:
            yaml_string = json.dumps(yaml.load(stream))

        except yaml.YAMLError as e:
            print(e)
            return HttpResponse("Error!")

    return render(request, 'yaml-template.html', {'yaml_string': yaml_string})


def task_list(request):
    task_list = Task.objects.all()
    tasks_to_return = []
    for task in task_list:
        single_task = dict()

        single_task['action'] = task.task_name
        task_data = json.loads(task.task_params)[1]

        if task.task_name == "apis.crud.create_one":
            print("create_one")
            new_item = task_data

            single_task['app'] = new_item['app']
            single_task['class'] = new_item['class']

            try:
                app_name = single_task['app']
                class_name = single_task['class']
            except:
                return []

            data_models = apps.get_app_config(app_name).get_models()

            for data_model in data_models:
                if data_model.__name__ == class_name:
                    data_model_to_return = data_model
                    break
            try:
                data_model_to_return
            except NameError:
                return []

            obj = data_model_to_return(**new_item['data'])

            single_task['old'] = {}
            single_task['new'] = dict()

            for item in new_item['data']:

                if item == 'crop_id':
                    print(item[:item.index('_id')])
                    single_task['new']['crop'] = obj.crop.name
                elif item == 'sub_region_id':
                    single_task['new']['sub_region'] = obj.sub_region.name
                
                '''

                if '_id' in item:
                    print(item[:item.index('_id')])
                    field_object = data_model_to_return._meta.get_field(item[:item.index('_id')])
                    field_value = field_object.value_from_object(obj)
                    single_task['new'][item[:item.index('_id')]] = field_value.name
                '''
                single_task['new'][item] = new_item['data'][item]

            tasks_to_return = tasks_to_return + [single_task]

        elif task.task_name == "apis.crud.delete_one":
            print("delete_one")
            old_item = task_data

            single_task['app'] = old_item['app']
            single_task['class'] = old_item['class']

            try:
                app_name = single_task['app']
                class_name = single_task['class']
            except:
                return []

            data_models = apps.get_app_config(app_name).get_models()

            for data_model in data_models:
                if data_model.__name__ == class_name:
                    data_model_to_return = data_model
                    break
            try:
                data_model_to_return
            except NameError:
                return []

            old_id = old_item['id']
            single_task['old'] = dict()
            old_item = crud.retrieve_list(**{'app': app_name, 'class': class_name, 'id': old_id})[0]

            # crud.retrieve_list(**{'app': app_name, 'class': class_name, 'id': old_id})  # TODO
            single_task['new'] = dict()

            single_task['old']['harvest_end'] = old_item.harvest_end
            single_task['old']['harvest_start'] = old_item.harvest_start
            single_task['old']['plant_end'] = old_item.plant_end
            single_task['old']['plant_start'] = old_item.plant_start
            single_task['old']['crop_id'] = old_item.crop_id
            single_task['old']['sub_region_id'] = old_item.sub_region_id
            single_task['old']['crop'] = old_item.crop.name
            single_task['old']['sub_region'] = old_item.sub_region.name

            # TODO
            # Hard Coded First

            tasks_to_return = tasks_to_return + [single_task]


        elif task.task_name == "apis.crud.update_one":
            print("update_one")
            new_item = task_data

            single_task['app'] = new_item['app']
            single_task['class'] = new_item['class']

            try:
                app_name = single_task['app']
                class_name = single_task['class']
            except:
                return []

            data_models = apps.get_app_config(app_name).get_models()

            for data_model in data_models:
                if data_model.__name__ == class_name:
                    data_model_to_return = data_model
                    break
            try:
                data_model_to_return
            except NameError:
                return []

            obj = data_model_to_return(**new_item['data'])

            old_id = new_item['id']
            single_task['old'] = dict()
            old_item = crud.retrieve_list(**{'app': app_name, 'class': class_name, 'id': old_id})[0]

            # crud.retrieve_list(**{'app': app_name, 'class': class_name, 'id': old_id})  # TODO
            single_task['new'] = dict()

            for item in new_item['data']:
                if item == 'crop_id':
                    print(item[:item.index('_id')])
                    single_task['new']['crop'] = obj.crop.name
                elif item == 'sub_region_id':
                    single_task['new']['sub_region'] = obj.sub_region.name
                single_task['new'][item] = new_item['data'][item]

            single_task['old']['harvest_end'] = old_item.harvest_end
            single_task['old']['harvest_start'] = old_item.harvest_start
            single_task['old']['plant_end'] = old_item.plant_end
            single_task['old']['plant_start'] = old_item.plant_start
            single_task['old']['crop_id'] = old_item.crop_id
            single_task['old']['sub_region_id'] = old_item.sub_region_id
            single_task['old']['crop'] = old_item.crop.name
            single_task['old']['sub_region'] = old_item.sub_region.name

            # TODO
            # Hard Coded First

            tasks_to_return = tasks_to_return + [single_task]


    print(len(tasks_to_return))
    #return HttpResponse("<h1> Task List. </h1>")
    return JsonResponse({"tasks": tasks_to_return})

