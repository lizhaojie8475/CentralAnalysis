from Src.SQLHelper.MySQLHelper import MySqlHelper
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

CORE_CITIES = ["北京市", "上海市", "广州市", "沈阳市", "南京市", "武汉市", "成都市", "西安市"]

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
    return 1


def getCenter(lat, lon, cityInfo_df):
    minDis = float("INF")
    ans = ""
    for city in CORE_CITIES:
        cityObj = cityInfo_df.loc[city]
        dis = calculateDistance(cityObj["latitude"], lat, cityObj["longitude"], lon)
        if dis < minDis:
            minDis = dis
            ans = city
    return ans

if __name__ == "__main__":
    cityInfo = getCityInfo()
    cityInfo_df = pd.DataFrame({"city": [city[0] for city in cityInfo],
                                "latitude": [city[1] for city in cityInfo],
                                "longitude": [city[2] for city in cityInfo]})
    cityInfo_df.set_index("city", inplace=True)

    centers = [getCenter(city[1], city[2], cityInfo_df) for city in cityInfo]
    cityInfo_df["center"] = centers

    le = LabelEncoder()
    cityInfo_df["center"] = le.fit_transform(cityInfo_df["center"].values)


    # for i in range(cityInfo_df.shape[0]):
    #     citySeries = cityInfo_df.iloc[i]
    #     if(citySeries["city"] not in CORE_CITIES):
    #         plt.scatter(citySeries["latitude"], citySeries["longitude"], c='b')
    #
    # for i in range(cityInfo_df.shape[0]):
    #     citySeries = cityInfo_df.iloc[i]
    #     if(citySeries["city"] in CORE_CITIES):
    #         print(citySeries)
    #         plt.scatter(citySeries["latitude"], citySeries["longitude"], c='r')
    #
    #
    # plt.show()