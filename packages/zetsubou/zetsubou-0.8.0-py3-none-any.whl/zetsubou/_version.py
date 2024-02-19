from datetime import date

__version__ = "0.8.0"
__author__ = 'BentouDev'

def get_author_desc():
     return f'{__author__} @ 2021-{date.today().year}'
