import re
import xlrd
import numpy
import pandas
import string
import random
import datetime
import itertools
import openpyxl


# import matplotlib.pyplot as plt
# from matplotlib.font_manager import fontManager
REGEX_DATETIME = {
    '[\d]{4}-[\d]{2}-[\d]{2}.[A-Z]{2}[\d]{1,2}:[\d]{1,2}:[\d]{1,2}':
    '%Y-%m-%d.%p%I:%M:%S', # '2022-07-31.AM3:02:30'
    '[\d]{4}\.[\d]{2}\.[\d]{2}\.[A-Z]{2}[\d]{1,2}:[\d]{1,2}':
    '%Y.%m.%d.%p%I:%M',    # '2022.07.31.AM3:02',
    "^[0-9]{4}/[0-9]{1,2}/[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}":
    '%Y/%m/%d %H:%M:%S',    # '2023/03/28 10:40:00',
}
