import datetime

def dd_time(str_time):
    return datetime.datetime.strptime(str(datetime.datetime.now().date()) + ' ' + str_time, '%Y-%m-%d %H:%M')

def custom_dd_time(date, str_time):
    custom_datetime = convert_to_datetime(date)
    return datetime.datetime.strptime(str(custom_datetime.date()) + ' ' + str_time, '%Y-%m-%d %H:%M')

def convert_to_datetime(str_time, format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(str_time, format)

def is_time_in_range(_from, _to, str_time=None):
    if str_time is None:
        d_time = dd_time(_from)
        d_time1 = dd_time(_to)
        
        n_time = datetime.datetime.now()
    else:
        d_time = custom_dd_time(str_time, _from)
        d_time1 = custom_dd_time(str_time, _to)
        
        n_time = convert_to_datetime(str_time, format='%Y-%m-%d %H:%M:%S')

    if n_time > d_time and n_time < d_time1:
        return True
    else:
        return False