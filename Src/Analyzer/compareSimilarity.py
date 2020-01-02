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


if __name__ == "__main__":
    routerInfo = getRouteInfo()
    routerInfo_df = pd.DataFrame({"sourceIP": [info[0] for info in routerInfo],
                                  "targetIP": [info[1] for info in routerInfo],
                                  "routers": [info[2] for info in routerInfo],
                                  "stability": [info[3] for info in routerInfo]})
    backbone_df = getBackboneDf(routerInfo_df)

    sourceList = np.unique(backbone_df["sourceIP"].values)
    disMetrix = [
        [calculateSimilarity(backbone_df[backbone_df["sourceIP"] == source_i], backbone_df[backbone_df["sourceIP"] == source_i])
            for source_j in sourceList]
        for source_i in sourceList]

    sns.heatmap(disMetrix, annot=True)
    plt.show()