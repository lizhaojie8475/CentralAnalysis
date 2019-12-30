from Src.SQLHelper.MySQLHelper import MySqlHelper
import pandas as pd
import matplotlib.pyplot as plt

CORE_CITIES = ["北京市", "上海市", "广州市", "沈阳市", "南京市", "武汉市", "成都市", "⻄安市"]

def getCityInfo():
    helper = MySqlHelper()
    helper.connect()
    sql = "SELECT county, latitude, longitude \
               FROM nationalCity \
               WHERE county in (SELECT city FROM china_dns)"

    results = helper.search(sql)
    helper.close()

    return list(results)

def calculateDistance(lat1, lat2, lon1, lon2):
    pass

if __name__ == "__main__":
    cityInfo = getCityInfo()
    cityInfo_df = pd.DataFrame({"city": [city[0] for city in cityInfo],
                                "latitude": [city[1] for city in cityInfo],
                                "longitude": [city[2] for city in cityInfo]})
    plt.scatter(x=cityInfo_df["latitude"], y=cityInfo_df["longitude"])
    plt.show()