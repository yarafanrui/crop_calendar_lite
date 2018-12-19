from django.apps import apps
from django.db.models.fields.related import ForeignKey
from django.db.models import CharField, DecimalField, IntegerField

from django.core.exceptions import FieldError

from django.http import HttpResponse

from background_task import background


def retrieve_list(**kwargs):
    # TODO
    # How to define the app-model opened
    # installed_apps = ['books']

    # TODO
    # Enable "xx__gt", "xx__lt" query


    try:
        app_name = kwargs['app']
        class_name = kwargs['class']
    except:
        return []

    # TODO
    # if app_name not in installed_apps:
    #    return []

    # Get all models under that app
    data_models = apps.get_app_config(app_name).get_models()

    # Get the model name passed through URL with the key "class"
    # If kwargs['class'] does not exist, return a []
    # print("data_models. ")
    for data_model in data_models:
        if data_model.__name__ == class_name:
            data_model_to_return = data_model
            break

    try:
        data_model_to_return
    except NameError:
        return []

    # Get fields with the given model.
    fields = data_model_to_return._meta.fields

    field_names = [field.name if not isinstance(field, ForeignKey) else field.name + '_id' for field in fields]

    key_words = {}
    for item in kwargs:
        if item == "class":
            continue

        if item == "app":
            continue

        '''
        if "__" not in item:
            print("No __")
        '''

        if item not in field_names:
            return []


        # "_id" indicates a ForeignKey.

        # IntegerField, FloatField, CharField...

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
        obj_list = data_model_to_return.objects.filter(**key_words)
    except FieldError:
        obj_list = []

    return obj_list

"""
def get_one(**kwargs):
    try:
        app_name = kwargs['app']
        class_name = kwargs['class']
    except:
        return []

    # TODO
    # if app_name not in installed_apps:
    #    return []

    # Get all models under that app

    try:
        data_models = apps.get_app_config(app_name).get_models()
    except:
        return []

    # Get the model name passed through URL with the key "class"
    # If kwargs['class'] does not exist, return a []
    # print("data_models. ")
    for data_model in data_models:
        if data_model.__name__ == class_name:
            data_model_to_return = data_model
            break

    try:
        data_model_to_return
    except NameError:
        return []

    # Get fields with the given model.
    fields = data_model_to_return._meta.fields

    field_names = [field.name if not isinstance(field, ForeignKey) else field.name + '_id' for field in fields]
    print("field_names: " + str(field_names))
    key_words = {}
    for item in kwargs:
        if item == "class":
            continue

        if item == "app":
            continue

        '''
        if "__" not in str(item):
            print("No __")
            if item not in field_names:
                return []
        '''

        if item not in field_names:
            return []


        # "_id" indicates a ForeignKey.
        # IntegerField, FloatField, CharField...

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
        obj = data_model_to_return.objects.get(**key_words)
    except:
        obj = []

    return obj

"""


@background(queue="create-queue")
def create_one(**kwargs):
    print("start post_one")
    print(kwargs)

    app_name = kwargs["app"]
    class_name = kwargs["class"]

    # Get all models under that app
    try:
        data_models = apps.get_app_config(app_name).get_models()
        print('data_models retrieved')
    except:
        # TODO
        # What to return here?
        # return HttpResponse("wrong app name")
        return []


    # Get the model name passed through URL with the key "class"
    # If kwargs['class'] does not exist, return a []
    # print("data_models. ")
    for data_model in data_models:
        if data_model.__name__ == class_name:
            data_model_to_add = data_model
            break

    try:
        data_model_to_add
    except NameError:
        # TODO
        # What to return here?
        #return HttpResponse("wrong class name")
        return []

    print("data model selected")
    # Get fields with the given model.
    fields = data_model_to_add._meta.fields

    field_names = [field.name if not isinstance(field, ForeignKey) else field.name + '_id' for field in fields]

    print(field_names)

    key_words = {}
    for item in kwargs["data"]:

        if item not in field_names:
            return HttpResponse("Wrong Field name(s).")

        print(item)

        key_words[item] = kwargs["data"][item]

    print(key_words)
    data_model_to_add_1 = data_model_to_add(**key_words)

    print('data model initiated')

    data_model_to_add_1.save()
    print('data model saved')


@background(queue="update-queue")
def update_one(**kwargs):
    print("start update_one")
    print(kwargs)

    # TODO
    # If not, What to return here?
    # return HttpResponse("wrong app name")
    app_name = kwargs["app"]
    class_name = kwargs["class"]

    _id = kwargs["id"]

    # Get all models under that app
    try:
        data_models = apps.get_app_config(app_name).get_models()
        print('data_models retrieved')
    except:
        # TODO
        # What to return here?
        # return HttpResponse("wrong app name")
        return []

    # Get the model name passed through URL with the key "class"
    # If kwargs['class'] does not exist, return a []
    # print("data_models. ")
    for data_model in data_models:
        if data_model.__name__ == class_name:
            data_model_to_update = data_model
            break

    try:
        data_model_to_update
    except NameError:
        # TODO
        # What to return here?
        # return HttpResponse("wrong class name")
        return []

    print("data model selected")
    # Get fields with the given model.
    fields = data_model_to_update._meta.fields

    field_names = [field.name if not isinstance(field, ForeignKey) else field.name + '_id' for field in fields]

    print(field_names)

    key_words = {}
    for item in kwargs["data"]:

        if item not in field_names:
            return HttpResponse("Wrong Field name(s).")

        print(item)

        key_words[item] = kwargs["data"][item]

    print(key_words)

    # The following line must use filter, not get
    data_model_to_update_1 = data_model_to_update.objects.filter(id=_id)

    print('data model initiated')

    data_model_to_update_1.update(**key_words)
    print('data model saved')


@background(queue="delete-queue")
def delete_one(**kwargs):
    print("start delete_one")
    print(kwargs)

    # TODO
    # If not, What to return here?
    # return HttpResponse("wrong app name")
    app_name = kwargs["app"]
    class_name = kwargs["class"]

    _id = kwargs["id"]

    # Get all models under that app
    try:
        data_models = apps.get_app_config(app_name).get_models()
        print('data_models retrieved')
    except:
        # TODO
        # What to return here?
        # return HttpResponse("wrong app name")
        return []

    # Get the model name passed through URL with the key "class"
    # If kwargs['class'] does not exist, return a []
    # print("data_models. ")
    for data_model in data_models:
        if data_model.__name__ == class_name:
            data_model_to_update = data_model
            break

    try:
        data_model_to_update
    except NameError:
        # TODO
        # What to return here?
        # return HttpResponse("wrong class name")
        return []

    print("data model selected")
    # Get fields with the given model.

    # The following line must use filter, not get
    data_model_to_delete_1 = data_model_to_update.objects.filter(id=_id)

    print('data model object found')

    data_model_to_delete_1.delete()
    print('data model object deleted')

