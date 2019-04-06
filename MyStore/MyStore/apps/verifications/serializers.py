import logging

from django_redis import get_redis_connection
from redis import RedisError
from rest_framework import serializers

logger = logging.getLogger('django')


class ImageCodeCheckSerializer(serializers.Serializer):
    """
    图片验证码序列化器
    """
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        """
        校验图片验证码
        :param attrs: 客户端提交过来的数据
        :return: 校验通过的attrs
        """
        image_code_id = attrs.get('image_code_id')
        text = attrs.get('text')

        # 取出redis中缓存的图片验证码
        redis_conn = get_redis_connection('verify')
        real_text = redis_conn.get('img_%s' % image_code_id)
        if not real_text:
            raise serializers.ValidationError('图片验证码无效！')

        try:
            # 删除取到的验证码
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)

        # 从redis中取出的数据是bytes类型，进行解码
        real_text = real_text.decode()
        if real_text.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误！')

        # 获取客户端请求对象传过来的手机号码
        mobile = self.context['view'].kwargs['mobile']

        # 判断是否在60秒内重复发送
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('短信发送过于频繁！请稍后再试')

        return attrs
