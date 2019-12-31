from Src.SQLHelper.MySQLHelper import MySqlHelper
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import silhouette_score, silhouette_samples
from math import asin, acos, sin, cos, pi, fabs, sqrt


def getCityInfo():
    helper = MySqlHelper()
    helper.connect()
    sql = "SELECT county, latitude, longitude, center, state \
               FROM nationalCity \
               WHERE county in (SELECT city FROM china_dns)"

    results = list(helper.search(sql))
    helper.close()

    coreCity = np.array([(result[0], result[4]) for result in results])
    coreCity = coreCity[coreCity[:, 1] == "active"][:, 0]
    return coreCity, results


def calculateDistance(lat1, lat2, lon1, lon2, mode=2):
    EARTH_RADIUS = 6371.393
    def angle2radian(angle):
        return angle / 180.0 * pi

    radian_lat1 = angle2radian(lat1)
    radian_lat2 = angle2radian(lat2)
    radian_lon1 = angle2radian(lon1)
    radian_lon2 = angle2radian(lon2)

    def GreatCircleDistance():
        delta = acos(sin(radian_lat1) * sin(radian_lat2) + cos(radian_lat1) * cos(radian_lat2) * cos(radian_lon1 - radian_lon2))
        return EARTH_RADIUS * delta

    def EuclideanDistance(lat1, lat2, lon1, lon2):
        diff_lat = fabs(lat1 - lat2) * cos((radian_lon1 + radian_lon2) / 2) * 111
        diff_lon = fabs(lon2 - lon1) * 111
        return sqrt(pow(diff_lat, 2) + pow(diff_lon, 2))

    if mode == 1:
        return GreatCircleDistance()
    elif mode == 2:
        return EuclideanDistance(lat1, lat2, lon1, lon2)


def getCenter(lat, lon, cityInfo_df, coreCity):
    minDis = float("INF")
    ans = ""
    for city in coreCity:
        cityObj = cityInfo_df.loc[city]
        dis = calculateDistance(cityObj["latitude"], lat, cityObj["longitude"], lon, 2)
        if dis < minDis:
            minDis = dis
            ans = city
    return ans


def drawPicture(df, coreCity):
    COLORS = ['b', 'g', 'r', 'c', 'm', 'y', 'k', '0.5']
    plt.scatter(df["latitude"], df["longitude"], c=df["center"])

    for city in coreCity:
        cityObj = df.loc[city]
        plt.scatter(cityObj["latitude"], cityObj["longitude"], c='r')

    plt.show()


def updateDB(df, field, tableName="nationalCity"):
    helper = MySqlHelper()
    helper.connect()
    helper.updateSamefieldDiffobj(field, df[field].values, tableName, "county",
                                   df["city"].values)
    helper.close()


def getSilhouetteScore(df):
    disMetrics = np.zeros((df.shape[0], df.shape[0]))
    for i in range(df.shape[0]):
        for j, lat, lon in zip(range(df.shape[0]), df["latitude"].values, df["longitude"].values):
            disMetrics[i][j] = calculateDistance(df.iloc[i]["latitude"], lat, df.iloc[i]["longitude"], lon)
    silhouetteScore = silhouette_samples(disMetrics, df["center"].values, metric="precomputed")
    df["silhouetteScore"] = silhouetteScore

    return df


def silhouette_m(cityObj, df):
    def calculateValueofA(city, label):
        cluster = df[df["center"] == label]
        disArray = [calculateDistance(city["latitude"], cluster.iloc[i]["latitude"], city["longitude"],
                                          cluster.iloc[i]["longitude"]) for i in range(cluster.shape[0])]
        a = np.array(disArray).mean()
        return a

    def calculateValueofB(city, label):
        diffClusterNumber = np.unique(df["center"].values)
        diffClusterNumber = diffClusterNumber[diffClusterNumber != label]
        disArray = [calculateValueofA(city, label) for label in diffClusterNumber]
        b = np.array(disArray)
        return b.min()

    a = calculateValueofA(cityObj, cityObj["center"])
    b = calculateValueofB(cityObj, cityObj["center"])
    return (b - a) / max(a, b)


def updateCoreCity(city_df):
    city_df = city_df[city_df["state"] == "inactive"]
    city_df["silhouetteScore"] = city_df["silhouetteScore"].apply(lambda x: fabs(x))
    array_groupby_center = city_df.groupby("center")["silhouetteScore"].min().values

    newCoreCity = city_df[city_df["silhouetteScore"].isin(array_groupby_center)]["city"].values
    return newCoreCity


if __name__ == "__main__":
    coreCity, cityInfo = getCityInfo()
    cityInfo_df = pd.DataFrame({"city": [city[0] for city in cityInfo],
                                "latitude": [city[1] for city in cityInfo],
                                "longitude": [city[2] for city in cityInfo],
                                "center": [city[3] for city in cityInfo],
                                "state": [city[4] for city in cityInfo]},
                                index=[city[0] for city in cityInfo])

    le = LabelEncoder()
    cityInfo_df["center"] = le.fit_transform(cityInfo_df["center"].values)
    cityInfo_df = getSilhouetteScore(cityInfo_df)

    coreCity = np.append(coreCity, updateCoreCity(cityInfo_df))
    cityInfo_df[cityInfo_df["city"].isin(coreCity)]["state"] = "active"
    centers = [getCenter(city[1], city[2], cityInfo_df, coreCity) for city in cityInfo]
    cityInfo_df["center"] = centers

    le = LabelEncoder()
    cityInfo_df["center"] = le.fit_transform(cityInfo_df["center"].values)

    drawPicture(cityInfo_df, coreCity)
