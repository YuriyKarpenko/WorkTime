from datetime import date, datetime, timedelta


def date_fromisoformat(ISOstr: str):
	ss = ISOstr.split('-', 3)
	return date(int(ss[0]), int(ss[1]), int(ss[2]))


# TODO: надо разобраться с рефлесией    https://www.geeksforgeeks.org/reflection-in-python/
# def to_dict(o):
#     res = {}
#     for k in o:
#         v = o[k]
#         # t = type(v)
#         # if t.
#         res[k] = v
#     return res

def trim(td: timedelta) -> timedelta:
	""" обрезает значение с точностью до секунд """
	return timedelta(td.days, td.seconds // 1)
