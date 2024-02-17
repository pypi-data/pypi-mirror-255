# common_packages
封装了一些通用的功能

打包
```bash
python -m build
```
安装
```bash
pip install common_packages-0.1.0.tar.gz
```
pypi
https://pypi.org/project/common-packages/#description

依赖
```bash
    "requests",
    'pika',
    "tencentcloud-sdk-python-tmt",
    "kafka-python",
    "clickhouse-driver",
    "numpy",
    "pandas",
    "sqlalchemy",
    "pymysql",
    "azure-cognitiveservices-speech",
```
### sms
腾讯云
```python

```

## django_utils
logging_config 日志控制配置

支持`StreamHandler`控制台输出，和`KafkaHandler`消息队列输出,默认全部开启。

运行模式:
```
开发模式:
debug,info,warning,error

生产模式:
info,Warnning,error
```

日志格式
```bash
# 微服务名 [请求id] 日志等级  日志发生日期(2列)  被触发的源文件绝对路径  行号  被调用的函数或方法名  自定义消息(多列)
base_app [8382398239239] INFO 2023-08-17 15:35:38,858 /BaseApplication/user/serializers.py 200 validate The login user name or password is incorrect
```


部署方式:
- docker 部署:
1. terminal
2. kafka

- kubernetes 部署:
1. terminal
2. kafka [可选]
