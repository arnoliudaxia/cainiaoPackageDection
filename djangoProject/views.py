import base64
import json
import time
from io import BytesIO

from PIL import Image
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from matplotlib import pyplot as plt
from djangoProject.ocr.main import *


def imageOCR(request):
    return agcmapedit_picture(request)


def agcmapedit_picture(request):
    # 获取图片文件
    file = request.FILES['image']
    # 打印输出文件名
    print(file)
    # 返回响应
    return HttpResponse(file, content_type="image/jpeg")


@require_http_methods(["POST"])
def filere(request):
    body = json.loads(request.body)
    img = body['img']
    package=body['package']
    isFlip=body['isFlip']
    isVertical=body['isVertical']
    img = base64.b64decode(img)
    # img = Image.open(BytesIO(img))
    result_img=ocrTarget(img,package,isFlip,isVertical)

    return HttpResponse("data:image;base64,"+result_img,content_type="image/jpg")

def postimg(request):
    return render(request, 'imgupload.html')

