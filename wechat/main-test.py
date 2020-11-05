# coding:utf-8

import flask, json
import redis
from kafka import KafkaProducer
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("stdout.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

redis_host = os.getenv('redis_host')
redis_pwd = os.getenv('redis_pwd')
bootstrap_servers = os.getenv('kafka_host')
topic_name = os.getenv('topic_name')

#redis_host = '192.168.0.49'
#redis_pwd = 'Huawei@123!'
#
#bootstrap_servers = '192.168.0.213:9092,192.168.0.62:9092,192.168.0.6:9092,192.168.0.144:9092,192.168.0.46:9092'
#topic_name = 'topic-test'

conf = {
    'bootstrap_servers': bootstrap_servers,
    'topic_name': topic_name
}

rd = redis.Redis(host=redis_host,port=6379,password=redis_pwd)
kf = KafkaProducer(bootstrap_servers=conf['bootstrap_servers'],value_serializer=lambda v: json.dumps(v).encode('utf-8'))

server = flask.Flask(__name__, static_url_path="")  # __name__代表当前的python文件。把当前的python文件当做一个服务启动
server.debug = True

@server.route('/')
def home():
    return server.send_static_file('button.html')

# 第一个参数就是路径,第二个参数支持的请求方式，不写的话默认是get，
# 加了@server.route才是一个接口，不然就是一个普通函数
@server.route('/login', methods=['get', 'post'])
def login():
    key = flask.request.values.get('key')
    value = flask.request.values.get('value')

    data = {
        key:value
    }
    print(data)

    if key and value:
        rd.set(key,value)
        kf.send(conf['topic_name'], data)
        kf.flush()
        res = {'msg': u'写入成功', 'key': key, 'value': value}
        logger.info(str(res).encode("utf-8"))
    else:
        res = {'msg': u'写入失败'}
        logger.info(str(res).encode("utf-8"))
    # json.dumps 序列化时对中文默认使用的ascii编码，输出中文需要设置ensure_ascii=False
    return json.dumps(res, ensure_ascii=False)


@server.route('/find', methods=['get', 'post'])
def find():
    findkey = flask.request.values.get('findkey')
    findvalue = rd.get(findkey)
    print(findvalue)
    print(findkey,findvalue)
    if findvalue != None:
        res = {'msg': u'查找成功', 'key': findkey, 'value':findvalue.decode('utf-8')}
        logger.info(str(res).encode("utf-8"))
    if findvalue == None:
        res = {'msg': u'查找失败'}
        logger.info(str(res).encode("utf-8"))
    if findkey == '':
        res = {'msg': u'调用失败'}
        logger.info(str(res).encode("utf-8"))
    # json.dumps 序列化时对中文默认使用的ascii编码，输出中文需要设置ensure_ascii=False
    return json.dumps(res, ensure_ascii=False)


if __name__ == '__main__':
    # port可以指定端口，默认端口是5000
    # host默认是服务器，默认是127.0.0.1
    # debug=True 修改时不关闭服务
    server.run(host="0.0.0.0", port=8080, debug=True)

