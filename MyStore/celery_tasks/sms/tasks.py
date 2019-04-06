import logging

from .yuntongxun.sms import CCP
from celery_tasks.main import app

logger = logging.getLogger('django')


@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code, sms_code_expires):
    """
    异步发送短信验证码
    :param mobile: 手机号码
    :param sms_code: 短信验证码
    :param sms_code_expires: 有效期
    """
    ccp = CCP()
    try:
        print('sms_code: ', sms_code)
        result = ccp.send_template_sms(mobile, [sms_code, sms_code_expires], 1)
    except Exception as e:
        logger.error('发送验证码短信[异常][mobile: %s, message: %s]' % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
