import pandas as pd
from timefhuman import timefhuman

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


