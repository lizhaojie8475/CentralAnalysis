import numpy as np
import pandas as pd
from Src.SQLHelper.MySQLHelper import MySqlHelper
import seaborn as sns
import matplotlib.pyplot as plt

def getRouteInfo():
    helper = MySqlHelper()
    helper.connect()
    sql = "SELECT source_ip, target_ip, routers, stability FROM trace_route WHERE TTL <> '0' and routers<>'' "
    results = list(helper.search(sql))
    return results


def getBackboneDf(df, threshold=2):
    validLinks = []
    for i in range(df.shape[0]):
        link = df.iloc[i]
        validNodes = link["stability"].split(";")
        validNodes = list(map(lambda node: int(node), validNodes))
        validNodes = np.array(validNodes) >= threshold
        validNodes = np.array(link["routers"].split(";"))[validNodes]
        validLinks.append(validNodes)
    backbone_df = pd.DataFrame({"sourceIP": df["sourceIP"].values,
                                "targetIP": df["targetIP"].values,
                                "validLink": validLinks})
    dropIndexList = backbone_df["validLink"].apply(lambda l: len(l) == 0)
    dropIndexList = backbone_df[dropIndexList].index.tolist()
    backbone_df.drop(index=dropIndexList, inplace=True)

    return backbone_df


def calculateSimilarity(df1, df2):
    def getLCS(routers1, routers2):
        """
        获取两个router列表的最长公共子序列
        input:
            routers: 分别是两条路由路径上经过的路由IP
        output:
            输出最长相同路由节点的个数
        """
        if len(routers1) == 0 or len(routers2) == 0:
            return 0

        lcs = np.ones((len(routers1) + 1, len(routers2) + 1))
        lcs[:, 0] = 0
        lcs[0, :] = 0
        for i in range(1, len(routers1) + 1):
            for j in range(1, len(routers2) + 1):
                if routers1[i - 1] == routers2[j - 1]:
                    lcs[i][j] = lcs[i - 1][j - 1] + 1
                else:
                    lcs[i][j] = max(lcs[i][j - 1], lcs[i - 1][j])
        return lcs[-1][-1]

    publicTarget = set(df1["targetIP"].values).intersection(set(df2["targetIP"].values))
    dict1 = dict(df1[["targetIP", "validLink"]].values)
    dict2 = dict(df2[["targetIP", "validLink"]].values)

    similarity = 0
    for target in publicTarget:
        routers1 = dict1[target]
        routers2 = dict2[target]
        similarity += getLCS(routers1, routers2) / min(len(routers1), len(routers2))

    similarity /= max(df1.shape[0], df2.shape[0])
    return similarity

def countIfDuplicate(mergedCities, index):
    """
    该函数从一个n*2的矩阵中，选出所有和index表示的城市有冲突关系的所有其他城市的数量。mergedCities中的每一行是两个城市的index，表示二者
    拓扑结构相似度超过阈值。index表示待查找的城市index，需要找出所有和该index成对出现在mergedCities中的不同city数量。
    """
    replication = []
    for mergedCity in mergedCities:
        if index in mergedCity:
            replication.append(mergedCity[0] if mergedCity[1] == index else mergedCity[1])
    return len(set(replication))


def mergeCenter(similarityMetrix, threshold, bacnbone_df, sourceList):
    """
    该函数是根据相似度矩阵找出相似度超过阈值的两个探测点，将二者合并为一个（看哪一个和其他节点的相似度超过阈值的数量更多，如果相同就选择有效路径更少的一方淘汰）。
    剩下的活跃探测点就可以认为都拥有区别较大的拓扑结构，所以无法确定他们所在的大区内是否还有新的拓扑结构，所以对留下的这些探测点需要在他们
    的大区内再寻找新的探测点位置。
    input:
        similarityMetrix: 相似度矩阵[n_samples, n_samples]， 每个位置表示两个探测点之间的距离。
        threshold: 相似度阈值
        sourceList: 所有的source名称
    output:
        activeCitySet: 表示与某一节点的拓扑结构相似度超过了阈值的city，但是这些city是在比较中胜出决定留下来作为探测点的city，只是他们
        所在的大区不用再参加下一次的探测点选举了。
        discardCitySet: 表示与某一节点拓扑结构相似度超过了阈值的city，并且在比较中失败，被排取消了成为探测点的资格。
    """
    similarityMetrix = np.array(similarityMetrix)
    mergedCities = np.argwhere(similarityMetrix > threshold)
    activeCitySet = set(np.unique(mergedCities))
    discardCitySet = []
    for pairCities in mergedCities:
        firstCityIndex = pairCities[0]
        secondCityIndex = pairCities[1]
        firstCity = sourceList[firstCityIndex]
        secondCity = sourceList[secondCityIndex]
        if firstCityIndex in activeCitySet and secondCityIndex in activeCitySet:
            if countIfDuplicate(mergedCities, firstCityIndex) > countIfDuplicate(mergedCities, secondCityIndex):
                discardCityIndex = firstCityIndex
            elif countIfDuplicate(mergedCities, firstCityIndex) < countIfDuplicate(mergedCities, secondCityIndex):
                discardCityIndex = secondCityIndex
            else:
                firstRouterNumber = backbone_df[backbone_df[firstCity]].shape[0]
                secondRouterNumber = backbone_df[backbone_df[secondCity]].shape[0]
                if firstRouterNumber < secondRouterNumber:
                    discardCityIndex = firstCityIndex
                else:
                    discardCityIndex = secondCityIndex
            discardCitySet.append(discardCityIndex)
            activeCitySet.discard(discardCityIndex)
    discardCitySet = set(discardCitySet)
    activeCitySet = map(lambda index: sourceList[index], activeCitySet)
    discardCitySet = map(lambda index: sourceList[index], discardCitySet)
    return activeCitySet, discardCitySet


if __name__ == "__main__":
    routerInfo = getRouteInfo()
    routerInfo_df = pd.DataFrame({"sourceIP": [info[0] for info in routerInfo],
                                  "targetIP": [info[1] for info in routerInfo],
                                  "routers": [info[2] for info in routerInfo],
                                  "stability": [info[3] for info in routerInfo]})
    backbone_df = getBackboneDf(routerInfo_df)

    sourceList = np.unique(backbone_df["sourceIP"].values)
    similarityMetrix = [
        [calculateSimilarity(backbone_df[backbone_df["sourceIP"] == source_i], backbone_df[backbone_df["sourceIP"] == source_i])
            for source_j in sourceList]
        for source_i in sourceList]

    sns.heatmap(similarityMetrix, annot=True)
    plt.show()