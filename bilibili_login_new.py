import time
from io import BytesIO

from selenium import webdriver
from PIL import Image

import requests
from hashlib import md5

class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password =  password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


browser = webdriver.Chrome(executable_path="C:/慕课网课程/chromedriver_win32/78/chromedriver.exe")

url = "https://passport.bilibili.com/login"

def crop_image(image_file_name):
    #截图验证码图片
    #定位某个元素在浏览器中的位置
    time.sleep(2)
    img = browser.find_element_by_xpath("//*[@class='geetest_holder geetest_silver']")
    location = img.location
    print("图片的位置", location)
    size = img.size

    top, buttom, left, right = location["y"], location["y"]+size["height"], location["x"], location['x'] + size["width"]
    print("验证码位置", left,top, right, buttom)
    screenshot = browser.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))
    captcha = screenshot.crop((int(left),int(top), int(right), int(buttom)))
    captcha.save(image_file_name)
    return img


def login():
    import mouse
    username = "xxxx"
    password = "xxx"

    browser.get(url)
    browser.maximize_window() #很重要！！

    username_ele = browser.find_element_by_xpath("//input[@id='login-username']")
    password_ele = browser.find_element_by_xpath("//input[@id='login-passwd']")
    username_ele.send_keys(username)
    password_ele.send_keys(password)

    #点击登录显示出验证码
    login_btn = browser.find_element_by_xpath("//a[@class='btn btn-login']")
    login_btn.click()
    # 1. 鼠标移动到正确的元素上，显示出没有缺口的图片并下载
    time.sleep(2)
    #截取图片,并获验证码图片的坐标
    img_element = crop_image("captcha1.png")
    img_location = img_element.location
    ele_x = img_location["x"]
    ele_y = img_location["y"]+114  #这里114是因为浏览器顶部的区域并没有被selenium识别
    # mouse.click()
    time.sleep(2)
    # action.click()
    # time.sleep(2)

    #通过超级鹰获取各文字的位置
    #超级鹰参考 http://www.chaojiying.com/
    #多次尝试识别，最大尝试3次
    #注意一下，超级鹰接口验证不一定每次都是正确的，多试几次就可以了
    chaojiying = Chaojiying_Client('超级鹰的用户名', '超级鹰的密码', '96001')  # 用户中心>>软件ID 生成一个替换 96001
    for i in range(3):
        print("第{}次尝试识别".format(i))
        im = open('captcha1.png', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        print("验证码坐标：")
        json_data = chaojiying.PostPic(im, 9004)
        location_list = []
        print(json_data)
        if json_data["err_no"] == 0:
            print("识别成功！")
            for location_info in json_data["pic_str"].split("|"):
                location_list.append((location_info.split(",")[0], location_info.split(",")[1]))
            print(location_list)
            for x, y in location_list:
                mouse.move(ele_x+int(x), ele_y+int(y))
                time.sleep(2)
                mouse.click()
            #点击确认按钮
            browser.find_element_by_xpath("//div[@class='geetest_commit_tip']").click()
            time.sleep(5)
            break
        else:
            print("识别失败，继续尝试！")
    # #获取缺口图片
    # ActionChains(browser).click_and_hold(slider).perform()
    # time.sleep(1)
    # image2 = crop_image("captcha2.png")


if __name__ == "__main__":
    login()