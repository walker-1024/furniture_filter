
# 根据给定的主题ID，将这个主题里的各个家具在资源文件夹内的相关资源文件（fbx、png等）找出来，并复制输出到一个新的文件夹里，同时对资源文件用md5去重

import json
import os
import hashlib
from typing import Optional


with open("building_data.json", "r", encoding="utf-8") as f:
    buildingDataDic = json.loads(f.read())

if not os.path.exists("output"):
    os.mkdir("output")


def getAllThemeIDs() -> Optional[list[str]]:
    if "customData" in buildingDataDic and "themes" in buildingDataDic["customData"]:
        return buildingDataDic["customData"]["themes"]
    else:
        print("Error: 数据文件格式不合预期")
        return None


def filterFurnitureWithTheme(themeID: str) -> Optional[list[str]]:
    if "customData" in buildingDataDic and "furnitures" in buildingDataDic["customData"] and "themes" in buildingDataDic["customData"]:
        if themeID in buildingDataDic["customData"]["themes"]:
            if "furnitures" in buildingDataDic["customData"]["themes"][themeID]:
                allFurniture = buildingDataDic["customData"]["themes"][themeID]["furnitures"]
                for furID in allFurniture:
                    if furID not in buildingDataDic["customData"]["furnitures"]:
                        print(f"Warning: 主题内的这个家具（{furID}）不在数据文件内")
                return allFurniture
            else:
                print("Error: 数据文件格式不合预期-2")
        else:
            print("Error: 这个主题不存在")
    else:
        print("Error: 数据文件格式不合预期")


def unionFurniture(themeShortID: str, resourceDataDirPath: str, furnitureIDArray: list[str], outputDirPath: str):

    existFileDic = {}
    foundFurnitureIDArray = []
    foundSinglePngFileArray = []

    def copyFileToOutputDir(filePath: str):
        name = filePath.split(os.path.sep)[-1]
        with open(filePath, "rb") as f:
            content = f.read()
        theMd5 = hashlib.md5(content).hexdigest().upper()
        if name in existFileDic:
            if theMd5 != existFileDic[name]:
                print(f"Warning: 去重失败！出现了同名但不同内容的文件（{name}）")
        else:
            with open(os.path.join(outputDirPath, name), "wb") as f:
                f.write(content)
            existFileDic[name] = theMd5

    def searchPath(path: str):
        if os.path.isdir(path):
            # 如果是文件夹，并且文件夹名含有主题ID，就把里面的文件都copy走
            fileList = os.listdir(path)
            for furnitureID in furnitureIDArray:
                if furnitureID in path:
                    for item in fileList:
                        copyFileToOutputDir(os.path.join(path, item))
                    foundFurnitureIDArray.append(furnitureID)
                    return
            for item in fileList:
                searchPath(os.path.join(path, item))
        else:
            # 如果是文件，则如果文件名包含主题简名并且是png，则copy走
            if themeShortID in path and path.endswith("png"):
                copyFileToOutputDir(path)
                foundSinglePngFileArray.append(path)

    searchPath(resourceDataDirPath)
    print(f"找到含家具ID的文件夹{len(foundFurnitureIDArray)}个，找个含主题简名的png文件{len(foundSinglePngFileArray)}个。")


def runWithThemeID(themeID: str, resourceDataDirPath: str):
    print("=====================================")
    print(f"开始处理 {themeID}")
    if len(themeID) > 10 and len(resourceDataDirPath) > 0:
        themeShortID = themeID[10:]
        furnitureIDArray = filterFurnitureWithTheme(themeID)
        if furnitureIDArray is not None:
            print(f"The length of furnitureIDArray is {len(furnitureIDArray)}.")
            outputDirPath = os.path.join("output", themeShortID)
            if not os.path.exists(outputDirPath):
                os.mkdir(outputDirPath)
            unionFurniture(themeShortID, resourceDataDirPath, furnitureIDArray, outputDirPath)
            print(f"{themeID} Done")
    else:
        print(f"Error: themeID（{themeID}）或resourceDataDirPath（{resourceDataDirPath}）非法")
    print("\n")


if __name__ == "__main__":
    themeID = input("输入主题ID（输入\"all\"以处理所有主题）：")
    resourceDataDirPath = input("输入资源所在文件夹路径：")
    if themeID == "all":
        allThemeIDs = getAllThemeIDs()
        if allThemeIDs is not None:
            for item in allThemeIDs:
                runWithThemeID(item, resourceDataDirPath)
    else:
        runWithThemeID(themeID, resourceDataDirPath)


