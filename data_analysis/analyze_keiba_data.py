import pandas as pd
import numpy as np
import requests
import time
from bs4 import BeautifulSoup
import glob


#
#
#
#

datasets_dir="datasets_past/"

files = glob.glob(datasets_dir+"*.csv",recursive=True)
print(files)
# df=pd.read_csv()