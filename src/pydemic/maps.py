"""Definitions of maps."""

from collections import namedtuple

CityAttrs = namedtuple('CityAttr', ['neighbors', 'color', 'population'])

# fmt: off
_default = {'atlanta': [['chicago', 'miami', 'washington'], 'blue', 4715000],
           'san_francisco': [['chicago', 'los_angeles', 'manila', 'tokyo'], 'blue', 5864000],
           'chicago': [['atlanta', 'los_angeles', 'mexico_city', 'montreal', 'san_francisco'], 'blue', 9121000],
           'montreal': [['chicago', 'new_york', 'washington'], 'blue', 3429000],
           'washington': [['atlanta', 'miami', 'montreal', 'new_york'], 'blue', 4679000],
           'new_york': [['london', 'madrid', 'montreal', 'washington'], 'blue', 20464000],
           'london': [['essen', 'madrid', 'new_york', 'paris'], 'blue', 8586000],
           'madrid': [['algiers', 'london', 'new_york', 'paris', 'sao_paulo'], 'blue', 5427000],
           'paris': [['algiers', 'essen', 'london', 'madrid', 'milan'], 'blue', 10755000],
           'milan': [['essen', 'istanbul', 'paris'], 'blue', 5232000],
           'essen': [['milan', 'london', 'paris', 'st_petersburg'], 'blue', 575000],
           'st_petersburg': [['essen', 'istanbul', 'moscow'], 'blue', 4879000],
           'algiers': [['cairo', 'istanbul', 'madrid', 'paris'], 'black', 2946000],
           'istanbul': [['algiers', 'baghdad', 'cairo', 'milan', 'moscow', 'st_petersburg'], 'black', 13576000],
           'moscow': [['istanbul', 'st_petersburg', 'tehran'], 'black', 15512000],
           'cairo': [['algiers', 'baghdad', 'istanbul', 'khartoum', 'riyadh'], 'black', 14718000],
           'baghdad': [['cairo', 'istanbul', 'karachi', 'riyadh', 'tehran'], 'black', 6204000],
           'tehran': [['baghdad', 'delhi', 'karachi', 'moscow'], 'black', 7419000],
           'riyadh': [['baghdad', 'cairo', 'karachi'], 'black', 5037000],
           'karachi': [['baghdad', 'delhi', 'mumbai', 'riyadh', 'tehran'], 'black', 20711000],
           'delhi': [['chennai', 'karachi', 'kolkata', 'mumbai', 'tehran'], 'black', 22242000],
           'mumbai': [['chennai', 'delhi', 'karachi'], 'black', 16910000],
           'chennai': [['bangkok', 'delhi', 'jakarta', 'kolkata', 'mumbai'], 'black', 8865000],
           'kolkata': [['bangkok', 'chennai', 'delhi', 'hong_kong'], 'black', 14374000],
           'bangkok': [['chennai', 'ho_chi_minh_city', 'hong_kong', 'jakarta'], 'red', 7151000],
           'jakarta': [['bangkok', 'chennai', 'ho_chi_minh_city', 'sydney'], 'red', 26063000],
           'ho_chi_minh_city': [['bangkok', 'hong_kong', 'jakarta', 'manila'], 'red', 8314000],
           'hong_kong': [['bangkok', 'ho_chi_minh_city', 'kolkata', 'manila', 'shanghai', 'taipei'], 'red', 7106000],
           'shanghai': [['beijing', 'hong_kong', 'seoul', 'taipei', 'tokyo'], 'red', 13482000],
           'beijing': [['seoul', 'shanghai'], 'red', 17311000],
           'seoul': [['beijing', 'shanghai', 'tokyo'], 'red', 22547000],
           'tokyo': [['osaka', 'seoul', 'shanghai'], 'red', 13189000],
           'osaka': [['taipei', 'tokyo'], 'red', 2871000],
           'taipei': [['hong_kong', 'manila', 'osaka', 'shanghai'], 'red', 8338000],
           'manila': [['ho_chi_minh_city', 'hong_kong', 'san_francisco', 'sydney', 'taipei'], 'red', 20767000],
           'sydney': [['jakarta', 'los_angeles', 'manila'], 'red', 3785000],
           'los_angeles': [['chicago', 'mexico_city', 'san_francisco', 'sydney'], 'yellow', 14900000],
           'mexico_city': [['bogota', 'chicago', 'lima', 'los_angeles', 'miami'], 'yellow', 19463000],
           'miami': [['atlanta', 'bogota', 'mexico_city', 'washington'], 'yellow', 5582000],
           'bogota': [['buenos_aires', 'lima', 'mexico_city', 'miami', 'sao_paulo'], 'yellow', 8702000],
           'lima': [['bogota', 'mexico_city', 'santiago'], 'yellow', 9121000],
           'santiago': [['lima'], 'yellow', 6015000],
           'buenos_aires': [['bogota', 'sao_paulo'], 'yellow', 13639000],
           'sao_paulo': [['bogota', 'buenos_aires', 'lagos', 'madrid'], 'yellow', 20186000],
           'lagos': [['khartoum', 'kinshasa', 'sao_paulo'], 'yellow', 11547000],
           'kinshasa': [['johannesburg', 'khartoum', 'lagos'], 'yellow', 9046000],
           'johannesburg': [['khartoum', 'kinshasa'], 'yellow', 3888000],
           'khartoum': [['cairo', 'johannesburg', 'kinshasa', 'lagos'], 'yellow', 4887000]}
# fmt: on

default = {}
for city_name, attrs in _default.items():
    default[city_name] = CityAttrs(*attrs)

maps = {'default': default}
