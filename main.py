
import json
import os
import hashlib
from typing import Optional
import threading
import PySimpleGUI as sg


with open("building_data.json", "r", encoding="utf-8") as f:
    buildingDataDic = json.loads(f.read())

outputBaseDirPath = "output"
if not os.path.exists(outputBaseDirPath):
    os.mkdir(outputBaseDirPath)

buildingDirPath = os.path.join(outputBaseDirPath, "building")
if not os.path.exists(buildingDirPath):
    os.mkdir(buildingDirPath)

furnitureIconDirPath = os.path.join(outputBaseDirPath, "furniture_icon")
if not os.path.exists(furnitureIconDirPath):
    os.mkdir(furnitureIconDirPath)


def getAllThemeIDs() -> list[str]:
    if "customData" in buildingDataDic and "themes" in buildingDataDic["customData"]:
        return list(buildingDataDic["customData"]["themes"].keys())
    else:
        print("Error: 数据文件格式不合预期")
        return []


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


def unionFurniture(themeID: str, resourceDataDirPath: str, furnitureIDArray: list[str]):
    outputDirPath = os.path.join(buildingDirPath, themeID)
    if not os.path.exists(outputDirPath):
        os.mkdir(outputDirPath)

    themeShortID = themeID[10:]

    # key 为文件名，value 为 (文件md5, 文件大小)
    existFileDic = {}
    foundFurnitureIDArray = []
    foundSinglePngFileArray = []

    def copyFileToOutputDir(filePath: str):
        if os.path.isdir(filePath):
            fileList = os.listdir(filePath)
            for item in fileList:
                copyFileToOutputDir(os.path.join(filePath, item))
        else:
            name = filePath.split(os.path.sep)[-1]
            with open(filePath, "rb") as f:
                content = f.read()
            theMd5 = hashlib.md5(content).hexdigest().upper()
            theSize = os.path.getsize(filePath)
            if name in existFileDic:
                beforeMd5, beforeSize = existFileDic[name]
                if theMd5 != beforeMd5:
                    if theSize > beforeSize:
                        with open(os.path.join(outputDirPath, name), "wb") as f:
                            f.write(content)
                        existFileDic[name] = (theMd5, theSize)
                    print(f"Warning: 去重失败！出现了同名但不同内容的文件（{name}），已保留较大的文件")
            else:
                with open(os.path.join(outputDirPath, name), "wb") as f:
                    f.write(content)
                existFileDic[name] = (theMd5, theSize)

    def searchPath(path: str):
        name = path.split(os.path.sep)[-1]
        if os.path.isdir(path):
            # 如果是文件夹，并且文件夹名含有主题ID，就把里面的文件都copy走
            fileList = os.listdir(path)
            for furnitureID in furnitureIDArray:
                if furnitureID in name:
                    for item in fileList:
                        copyFileToOutputDir(os.path.join(path, item))
                    foundFurnitureIDArray.append(furnitureID)
                    return
            for item in fileList:
                searchPath(os.path.join(path, item))
        else:
            # 如果是文件，则如果文件名包含主题简名并且是png，则copy走
            if name.startswith(f"TX_{themeShortID}") and name.endswith("png"):
                copyFileToOutputDir(path)
                foundSinglePngFileArray.append(path)

    searchPath(resourceDataDirPath)
    print(f"找到含家具ID的文件夹{len(foundFurnitureIDArray)}个，找到含主题简名的png文件{len(foundSinglePngFileArray)}个。")


def unionFurnitureIcon(themeID: str, resourceDataDirPath: str, furnitureIDArray: list[str]):
    outputDirPath = os.path.join(furnitureIconDirPath, themeID)
    if not os.path.exists(outputDirPath):
        os.mkdir(outputDirPath)

    furnitureIconIDArray = []
    if "customData" in buildingDataDic and "furnitures" in buildingDataDic["customData"]:
        for furID in furnitureIDArray:
            if furID not in buildingDataDic["customData"]["furnitures"]:
                print(f"Warning: 主题内的这个家具（{furID}）不在数据文件内")
                furnitureIconIDArray.append(furID)
            else:
                furModel = buildingDataDic["customData"]["furnitures"][furID]
                if "iconId" in furModel:
                    furnitureIconIDArray.append(furModel["iconId"])
                else:
                    print(f"Warning: 主题内的这个家具（{furID}）数据格式不合预期-3")
                    furnitureIconIDArray.append(furID)
    else:
        print("Error: 数据文件格式不合预期")
        furnitureIconIDArray = furnitureIDArray

    # key 为文件名，value 为 (文件md5, 文件大小)
    existFileDic = {}
    foundFurnitureIconIDArray = []

    def copyFileToOutputDir(filePath: str):
        if os.path.isdir(filePath):
            fileList = os.listdir(filePath)
            for item in fileList:
                copyFileToOutputDir(os.path.join(filePath, item))
        else:
            _, name = os.path.split(filePath)
            with open(filePath, "rb") as f:
                content = f.read()
            theMd5 = hashlib.md5(content).hexdigest().upper()
            theSize = os.path.getsize(filePath)
            if name in existFileDic:
                beforeMd5, beforeSize = existFileDic[name]
                if theMd5 != beforeMd5:
                    if theSize > beforeSize:
                        with open(os.path.join(outputDirPath, name), "wb") as f:
                            f.write(content)
                        existFileDic[name] = (theMd5, theSize)
                    print(f"Warning: 去重失败！出现了同名但不同内容的文件（{name}），已保留较大的文件")
            else:
                with open(os.path.join(outputDirPath, name), "wb") as f:
                    f.write(content)
                existFileDic[name] = (theMd5, theSize)

    def searchPath(path: str):
        if not os.path.exists(path):
            return
        if os.path.isdir(path):
            fileList = os.listdir(path)
            for item in fileList:
                searchPath(os.path.join(path, item))
        else:
            _, fileName = os.path.split(path)
            for iconID in furnitureIconIDArray:
                if iconID + ".png" == fileName:
                    copyFileToOutputDir(path)
                    foundFurnitureIconIDArray.append(iconID)
                    break

    searchPath(resourceDataDirPath)
    print(f"找到家具图标{len(foundFurnitureIconIDArray)}个。")


def runWithThemeID(themeID: str, resourceDataDirPath: str):
    print("=====================================")
    print(f"开始处理 {themeID}")
    if len(themeID) > 10 and len(resourceDataDirPath) > 0:
        furnitureIDArray = filterFurnitureWithTheme(themeID)
        if furnitureIDArray is not None:
            print(f"The length of furnitureIDArray is {len(furnitureIDArray)}.")
            unionFurniture(themeID, resourceDataDirPath, furnitureIDArray)
            unionFurnitureIcon(themeID, resourceDataDirPath, furnitureIDArray)
            print(f"{themeID} Done")
    else:
        print(f"Error: themeID（{themeID}）或resourceDataDirPath（{resourceDataDirPath}）非法")
    print("\n")


def runGUI():
    allThemeIDs = getAllThemeIDs()
    comboList = allThemeIDs.copy()
    comboList.insert(0, "all")

    layout = [
        [sg.Text("资源所在文件夹路径："), sg.InputText(key="resourceDataDirPath"), sg.FolderBrowse("选择文件夹")],
        [sg.Text("选择主题（选择\"all\"以处理所有主题）："), sg.Combo(comboList, default_value="all", key="themeID")],
        [sg.Button("执行")],
        [sg.Output(size=(100, 20))]
    ]

    window = sg.Window("furniture_filter", layout)

    def innerRun(themeID: str, resourceDataDirPath: str):
        if themeID == "all":
            for item in allThemeIDs:
                runWithThemeID(item, resourceDataDirPath)
        else:
            runWithThemeID(themeID, resourceDataDirPath)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "执行":
            resourceDataDirPath = values.get("resourceDataDirPath")
            themeID = values.get("themeID")
            threading.Thread(target=innerRun, args=(themeID, resourceDataDirPath)).start()

    window.close()


if __name__ == "__main__":
    runGUI()

