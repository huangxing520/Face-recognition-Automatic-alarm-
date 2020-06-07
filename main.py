#-*- coding: utf-8 -*
import os
from viapi.fileutils import FileUtils
import oss2
import time
import cv2
from aliyunsdkcore.client import AcsClient
import smtplib  # 邮件模块
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkfacebody.request.v20191230.SearchFaceRequest import SearchFaceRequest
import json

cap = cv2.VideoCapture(0)#参数为0时调用本地摄像头；url连接调取网络摄像头；文件地址获取本地视频
fps=cap.get(5)
i=0
auth = oss2.Auth('your key', 'your secert number')
bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai.aliyuncs.com', 'your oss')
file_utils = FileUtils('your key', 'your secert number')
client = AcsClient('your key', 'your secert number', 'cn-shanghai')

##########################################################
def send_emails(url):
    sender = '###@qq.com'  # 发件人邮箱
    receiver = '#######@qq.com'  # 收件人邮箱，可以多个（列表形式）群发
    username = '#####@qq.com'  # 发件人姓名
    subject = "警告，有陌生人正在入侵你家"  # 邮件标题
    e_content = url  # 邮件正文
    password = '####'  # smtp密码，qq是给你分配一串，163是自己设置
    smtpserver = 'smtp.qq.com'  # 邮箱服务器
    message = MIMEMultipart()
    message['From'] = sender  # 发送
    message['To'] = receiver  # 收件
    message['Subject'] = subject
    message.attach(MIMEText(e_content, 'plain', 'utf-8'))  # 邮件正文

    # 构造附件

    # 执行
    smtp = smtplib.SMTP()
    smtp = smtplib.SMTP_SSL('smtp.qq.com', port=465)  # 连接服务器
    smtp.login(username, password)  # 登录
    smtp.sendmail(sender, receiver, message.as_string())  # 发送
    smtp.quit()
    return True
####################################################################

def delect():
    for files in os.listdir():
        if files.endswith(".png"):
            os.remove(os.path.join(files))
#####################################################################
while(True):
    ret,frame=cap.read()
    # 转化为灰图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 设置导出文件名编号
    time1 = time.localtime(time.time())
    # 每1s导出一q张
    # 若想要导出灰图，则将下面frame改为gray即可
    i = i + 1
    #每1s导出一张
    if i/fps==int(i/fps):
        cv2.imwrite(str(time1.tm_year)+str(time1.tm_mon) +str(time1.tm_mday)+str(time1.tm_hour)+str(time1.tm_min)+str(time1.tm_sec)+ ".png", frame)
        name=str(time1.tm_year)+str(time1.tm_mon) +str(time1.tm_mday)+str(time1.tm_hour)+str(time1.tm_min)+str(time1.tm_sec)+ ".png"
        oss_url = file_utils.get_oss_url(name, "png", True)

        bucket.put_object_from_file(name, name)
        request = SearchFaceRequest()
        request.set_accept_format('json')
        request.set_DbName("my_face_set")
        request.set_ImageUrl(oss_url)
        request.set_Limit(20)
        response = client.do_action_with_exception(request)
        respone_dict=json.loads(response)
        time.sleep(1)
        if(respone_dict['Data']['MatchList'][0]['FaceItems'][0]["Score"]<=0):
            send_emails(oss_url)
    if(i>=500):
        delect()
        i=1
        #print(str(response, encoding='utf-8')[0])
    time.sleep(0.05)#大概1秒拍一张照片
cap.release()
cv2.destroyAllWindows()
#############################################################
