import random

from django.http.response import HttpResponse
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from rest_framework.views import APIView

from MyStore.libs.captcha.captcha import Captcha
from celery_tasks.sms.tasks import send_sms_code
from . import constants, serializers


# Create your views here.
class ImageCodeAPIView(APIView):
    """
    图片验证码
    访问方式： GET /image_codes/{image_code_id}/
    """

    @staticmethod
    def get(request, image_code_id):
        """
        获取验证码
        :param request: 客户端请求
        :param image_code_id: 验证码
        :return: 响应生成的验证码图片
        """
        captcha = Captcha()
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection('verify')
        redis_conn.setex('img_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type='image/jpg')


class SMSCodeGAPIView(GenericAPIView):
    """
    短信验证码
    访问方式： GET /sms_codes/{mobile}/?image_code_id=xxx&text=xxx
    """
    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 校验数据
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成6位数字短信验证码
        sms_code = '%06d' % random.randint(0, 999999)

        # 保存短信验证码和发送短信的时间记录到redis中
        redis_conn = get_redis_connection('verify')
        # 使用管道提高性能
        pl = redis_conn.pipeline()
        # 声明将在管道中执行多条操作
        pl.multi()
        # 将要执行的redis操作全部放到管道中
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行管道中的命令
        pl.execute()

        # 发送短信验证码
        sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
        send_sms_code.delay(mobile, sms_code, sms_code_expires)

        return Response({'message': 'OK'}, status=status.HTTP_200_OK)
