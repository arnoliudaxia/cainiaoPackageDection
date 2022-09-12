import base64
import re
import cv2 as cv
import numpy as np
from djangoProject.ocr.utlity import *

from djangoProject.ocr.aip import AipOcr

""" 你的 APPID AK SK """
APP_ID = '27426789'
API_KEY = 'NdWLP2GqDmAqkSgkYAs6oGXY'
SECRET_KEY = '8aRvyOhdSBO0a8Rcl5dDGbUF9VuG8G35'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def findPackagesByBaidu(inputimage,IMAGE_WIDTH,IMAGE_HEIGHT,rot=None):
    # 如果有可选参数
    options = {}
    options["probability"] = "true"
    packages=[]
    res_image = client.general(inputimage, options)
    print("获取结果完成")
    for word in res_image["words_result"]:
        if(re.match("^[0-9]{4}$",word["words"])): #匹配四位数字
            print(f"找到{word['words']},置信度为{word['probability']['average']}")
            #位置还原
            xx,yy=word["location"]["left"],word["location"]["top"]
            ww,hh=word["location"]["width"],word["location"]["height"]

            if(rot=="L"):
                word["location"]["left"]=IMAGE_WIDTH-yy-hh
                word["location"]["top"]=xx
                word["location"]["width"]=hh
                word["location"]["height"]=ww

            if(rot=="R"):
                word["location"]["left"]=yy
                word["location"]["top"]=IMAGE_HEIGHT-xx-ww

                word["location"]["width"] = hh
                word["location"]["height"] = ww
            if(rot=="V"):
                word["location"]["left"]=IMAGE_WIDTH-xx-ww
                word["location"]["top"]=IMAGE_HEIGHT-yy-hh
            packages.append({
                "取货码":word["words"],
                "location":word["location"]
            })
    return packages


def ocrTarget(image,packageLookingFor,isFlip,isVertical):
    image=cv.imdecode(np.array(bytearray(image),dtype="uint8"),cv.IMREAD_UNCHANGED)
    print("图片解析完成")

    IMAGE_WIDTH=image.shape[1]
    IMAGE_HEIGHT=image.shape[0]

    #读取所有图片bin
    imageO = cv.imencode(".jpg", image)[1].tobytes()
    imageL =cv.imencode(".jpg", cv.rotate(image, cv.ROTATE_90_COUNTERCLOCKWISE))[1].tobytes()
    imageR =cv.imencode(".jpg", cv.rotate(image, cv.ROTATE_90_CLOCKWISE))[1].tobytes()
    imageV =cv.imencode(".jpg", cv.rotate(image, cv.ROTATE_180))[1].tobytes()
    print("旋转图片完成")

    #访问百度API获取结果
    packages=[]
    packages.extend(findPackagesByBaidu(imageO,IMAGE_WIDTH,IMAGE_HEIGHT))
    if isVertical:
        packages.extend(findPackagesByBaidu(imageL,IMAGE_WIDTH,IMAGE_HEIGHT,"L"))
    # packages.extend(findPackagesByBaidu(imageR,IMAGE_WIDTH,IMAGE_HEIGHT,"R"))
    if isFlip:
        packages.extend(findPackagesByBaidu(imageV,IMAGE_WIDTH,IMAGE_HEIGHT,"V"))
    del imageO,imageV,imageR,imageL #手动GC
    print("获取所有结果")

    #可视化找到的包裹
    blk = np.zeros(image.shape, np.uint8)
    for package in packages:
        BLUE=(255,0,0)#非目标填充蓝色
        RED=(0,0,255)#目标为红色
        findTarget=[]
        x1,y1=package["location"]["left"],package["location"]["top"]
        x2,y2=package["location"]["width"]+x1,package["location"]["height"]+y1
        if package["取货码"]==packageLookingFor:
            findTarget.append([x1,y1])
            cv.rectangle(blk, [x1, y1], [x2, y2], RED, -1)
            break
        cv.rectangle(blk,[x1,y1],[x2,y2],BLUE,-1)



    image=cv.addWeighted(image, 1, blk, 0.5, 1)
    image=cv.imencode(".jpg", image)[1]
    return str(base64.b64encode(image))[2:-1]
