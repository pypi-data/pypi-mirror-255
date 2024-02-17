import sys

sys.path.append("..")
from common_packages.email_utils import SendEmail

from . import get_config

config: dict = get_config()
content = "test content"
subject = "title123"


class TestEmail:
    def test_163(self):
        receivers = config["email"]["receivers"]
        config_163 = config["email"]["config_163"]
        e_163 = SendEmail(config_163)
        status, _ = e_163.send_txt_message(receivers, subject, content)
        assert status == True

    def test_feishu(self):
        receivers = config["email"]["receivers"]
        config_feishu = config["email"]["config_feishu"]
        e_feishu = SendEmail(config_feishu)
        status, _ = e_feishu.send_txt_message(receivers, subject, content)
        assert status == True
