
FROM ubuntu:16.04

MAINTAINER chenhong41@huawei.com

#添加目录
ADD wechat /root/

#调整工作目录
WORKDIR /root/

#安装依赖
RUN apt update -y
RUN apt install -y python3
RUN apt install -y python3-pip

RUN pip3 install redis
RUN pip3 install kafka
RUN pip3 install flask

#暴露端口
EXPOSE 8080

#ENTRYPOINT ['python3']

CMD ["python3","main-test.py","8080"]
