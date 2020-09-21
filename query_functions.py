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

# for reservations, i want to find business_id given 4 criteria

# for enquiry, i want a business name to attributes match

# for reservation, i need to check that restaurant is open

# parsing functions, price, date, time, food type, meal type
# food type has been done by eugene in the mdl_similarities.py
# but will need to amend his function

# for date, we need to convert "today, next week, tomorrow, Wednesday" into a date
# that seems a bit convoluted

# time and meal type will use the same column, so i need to convert
# "afternoon, 7pm, etc" into a number?

#can use timefhuman to parse, but will have to pay attention to the time "tues at 4"
#would return the number 4, but we have to check if that's am/pm

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