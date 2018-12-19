def load():

    import csv
    from four_dates.models import Country, SubRegionUnit, SubRegion, Crop, FourDates

    print("start loading")

    with open('/Users/ruifan/Downloads/crop_calendar_lite.csv') as f:
        csvReader = csv.reader(f)
        next(csvReader)

        line_counter = 0
        for row in csvReader:
            # print("line: " + str(line_counter))

            #print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14])
            alpha_2_code = row[0]
            alpha_3_code = row[1]
            country_name = row[2]

            country, _created = Country.objects.get_or_create(name=country_name,
                                                              alpha_2_code=alpha_2_code,
                                                              alpha_3_code=alpha_3_code)
            sub_region_name = row[3]
            sub_region_unit_name = row[4]
            agro_eco_zone = row[5]
            try:
                lat = float(row[7])
                lng = float(row[8])
            except:
                lat = None
                lng = None

            if sub_region_unit_name == '':
                sub_region_unit =None
            else:
                sub_region_unit, _created = SubRegionUnit.objects.get_or_create(name=sub_region_unit_name)

            if sub_region_name == "ALL" or sub_region_name == "":
                sub_region_name = country.name + " - ALL"

            sub_region, _created = SubRegion.objects.get_or_create(name=sub_region_name,
                                                                   sub_region_unit=sub_region_unit,
                                                                   agro_eco_zone=agro_eco_zone,
                                                                   lat=lat,
                                                                   lng=lng,
                                                                   country=country)

            crop_name = row[6]

            crop, _created = Crop.objects.get_or_create(name=crop_name)

            source_file = row[9]
            try:
                plant_start = round(float(row[10]))
            except:
                plant_start = None

            try:
                plant_end = round(float(row[11]))
            except:
                plant_end = None

            try:
                harvest_start = round(float(row[12]))
            except:
                harvest_start = None

            try:
                harvest_end = round(float(row[13]))
            except:
                harvest_end = None

            flag = True if row[14] else False

            four_dates, _created = FourDates.objects.get_or_create(
                sub_region=sub_region,
                crop=crop,
                source_file=source_file,
                plant_start=plant_start,
                plant_end=plant_end,
                harvest_start=harvest_start,
                harvest_end=harvest_end,
                flag=flag,)


            print("Line: " + str(line_counter))
            line_counter += 1


    print("finish loading")

