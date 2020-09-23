import pandas as pd
from timefhuman import timefhuman
from numerizer import numerize

class Time:
    def __init__(self):
        self.datetime = None
        self.dayofweek = None
        self.mealtype = None

time = Time()

data = pd.read_csv("data/business_extract_filter_clean1.csv")
# weekday_mealtype columns have 33 NAs
# dropping rows
# there are 34 rows with missing names, so i will drop all

data = data.dropna()
data[data.filter(regex = 'mealtype|PriceRange').columns] = data[data.filter(regex = 'mealtype|PriceRange').columns].astype(int)


def is_open_breakfast(day, biz_id):
    # let's assume the day is already formatted properly
    # e.g. Monday, Tuesday, etc.
    col_name = "{}_mealtype".format(day)

def parse_datetime(datetime):
    #return three items, datetime, day of week and time of meal
    dt = timefhuman(datetime) #datetime object returns list if empty, object if not

    return timefhuman(datetime)

def get_recommendation(rec_obj):
    return "these are the slots {}".format(vars(rec_obj))

def get_enquiry(enq_obj):
    #check if restaurant name is found in database
    return "this is the restaurant name {}".format(vars(enq_obj))

def get_reservation(res_obj):
    #check if restaurant is available for that datetimeslot
    return "these are the reservation details {}".format(vars(res_obj))

def filter_food_type(term, df):
    pass

def filter_meal_type(term, df):
    pass

def filter_price(term, df):
    pass

def filter_rating(term, df):
    pass

def set_if_found(in_dict, ref):
    ref_keys = set(vars(ref).keys())
    in_keys = set(in_dict.keys())
    shared_keys = in_keys.intersection(ref_keys)
    
    for key in shared_keys:
        setattr(ref, key, in_dict[key])
    
    return