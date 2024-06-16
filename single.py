
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

singleFurnitureDirPath = os.path.join(outputBaseDirPath, "single_furniture")
if not os.path.exists(singleFurnitureDirPath):
    os.mkdir(singleFurnitureDirPath)


def findAllSingleFurniture(resourceDataDirPath: str):
    # 元素为 (furnitureID, furnitureIconID)
    allSingleFurnitureIDAndIconIDs = []

    if "customData" in buildingDataDic and "furnitures" in buildingDataDic["customData"]:
        allFurnitures = buildingDataDic["customData"]["furnitures"]
        for furID in allFurnitures:
            furModel = allFurnitures[furID]
            if "themeId" in furModel and furModel["themeId"] == "":
                if "id" in furModel:
                    theFurnitureID = furModel["id"]
                else:
                    print(f"Warning: 这个家具（{furID}）数据格式不合预期-4")
                    theFurnitureID = furID
                if "iconId" in furModel:
                    theFurnitureIconID = furModel["iconId"]
                else:
                    print(f"Warning: 这个家具（{furID}）数据格式不合预期-4")
                    theFurnitureIconID = furID
                allSingleFurnitureIDAndIconIDs.append((theFurnitureID, theFurnitureIconID))
    else:
        print("Error: 数据文件格式不合预期")
        return

    def copyFileToOutputDir(filePath: str, outputDirPath: str):
        if not os.path.exists(filePath):
            return
        if not os.path.exists(outputDirPath):
            os.mkdir(outputDirPath)
        if os.path.isdir(filePath):
            fileList = os.listdir(filePath)
            for item in fileList:
                copyFileToOutputDir(os.path.join(filePath, item), outputDirPath)
        else:
            _, name = os.path.split(filePath)
            with open(filePath, "rb") as f:
                content = f.read()
            outputFilePath = os.path.join(outputDirPath, name)
            if os.path.exists(outputFilePath):
                theMd5 = hashlib.md5(content).hexdigest().upper()
                with open(outputFilePath, "rb") as f:
                    beforeContent = f.read()
                    beforeMd5 = hashlib.md5(beforeContent).hexdigest().upper()
                if theMd5 != beforeMd5:
                    theSize = os.path.getsize(filePath)
                    beforeSize = os.path.getsize(outputFilePath)
                    if theSize > beforeSize:
                        with open(outputFilePath, "wb") as f:
                            f.write(content)
                    print(f"Warning: 去重失败！出现了同名但不同内容的文件（{name}），已保留较大的文件")
            else:
                with open(outputFilePath, "wb") as f:
                    f.write(content)

    foundFurnitureIDArray = []
    foundFurnitureIconIDArray = []

    def searchPath(path: str):
        if not os.path.exists(path):
            return
        name = path.split(os.path.sep)[-1]
        if os.path.isdir(path):
            # 如果是文件夹，并且文件夹名含有家具ID，就把里面的文件都copy走
            fileList = os.listdir(path)
            for furnitureID, _ in allSingleFurnitureIDAndIconIDs:
                if furnitureID in name:
                    for item in fileList:
                        copyFileToOutputDir(os.path.join(path, item), os.path.join(singleFurnitureDirPath, furnitureID))
                    if furnitureID not in foundFurnitureIDArray:
                        foundFurnitureIDArray.append(furnitureID)
                    print(f"找到一个含家具ID的文件夹：{path}")
                    return
            for item in fileList:
                searchPath(os.path.join(path, item))

    def searchIconWithPath(path: str):
        if not os.path.exists(path):
            return
        if os.path.isdir(path):
            fileList = os.listdir(path)
            for item in fileList:
                searchIconWithPath(os.path.join(path, item))
        else:
            _, fileName = os.path.split(path)
            for furnitureID, iconID in allSingleFurnitureIDAndIconIDs:
                if iconID + ".png" == fileName:
                    copyFileToOutputDir(path, os.path.join(singleFurnitureDirPath, furnitureID))
                    if iconID not in foundFurnitureIconIDArray:
                        foundFurnitureIconIDArray.append(iconID)
                    print(f"找到家具图标文件：{path}")
                    break

    print("=====================================")
    print(f"开始处理\n")

    searchPath(resourceDataDirPath)
    searchIconWithPath(resourceDataDirPath)

    print(f"\n处理结束")
    print(f"共有{len(allSingleFurnitureIDAndIconIDs)}个单品家具，其中{len(foundFurnitureIDArray)}个单品家具找到了含家具ID的文件夹，{len(foundFurnitureIconIDArray)}个单品家具找到了家具图标文件。\n")


def runGUI():

    layout = [
        [sg.Text("资源所在文件夹路径："), sg.InputText(key="resourceDataDirPath"), sg.FolderBrowse("选择文件夹")],
        [sg.Text(f"点击执行，将会搜索所有的单品家具（不属于任何主题的家具），放在{singleFurnitureDirPath}路径下")],
        [sg.Button("执行")],
        [sg.Output(size=(100, 20))]
    ]

    window = sg.Window("single_furniture_filter", layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "执行":
            resourceDataDirPath = values.get("resourceDataDirPath")
            threading.Thread(target=findAllSingleFurniture, args=(resourceDataDirPath,)).start()

    window.close()


if __name__ == "__main__":
    runGUI()

