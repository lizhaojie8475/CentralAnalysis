import json
import sys, os
import re
from Src.SQLHelper.MySQLHelper import MySqlHelper
import pandas as pd
import numpy as np
import Src.Analyzer.chooseNewProbes as cp
import math

def insertCityInfo():
    dirPath = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dirPath += "/Data/"

    with open(dirPath + "nationalCities.txt") as cityFile:
        cityStrings = cityFile.readlines()
        cityStrings = map(lambda city: re.sub(r"\s+", "", city)[:-1], cityStrings)
        cityStrings = filter(lambda city: city != "", cityStrings)

        cityObjs = map(lambda cityString: json.loads(cityString), cityStrings)
        cityObjs = list(cityObjs)

    helper = MySqlHelper()
    helper.connect()
    for obj in cityObjs:
        sql = "INSERT INTO nationalCity_1(provinceName, cityName, county, longitude, latitude) VALUES (%s, %s, %s, %s, %s)"
        helper.insert(sql, obj["province"], obj["city"], obj["county"], obj["longitude"], obj["latitude"])

    helper.close()


if __name__ == "__main__":
    a = np.array([[1,3,3], [4,5,6]])
    print(np.unique(a))
