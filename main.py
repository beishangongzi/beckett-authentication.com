import io
import os.path
import threading
from queue import Queue

import requests
import re
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd

from ocr import Ocr


def make_request(url, method, headers=None, timeout=None, data=None, cookies=None, ):
    global response
    i = 0
    while i < 10:
        try:
            response = getattr(requests, method)(url=url, data=data, cookies=cookies, headers=headers, timeout=timeout)
            break
        except requests.exceptions.ConnectionError as e:
            print(e)
            i += 1
            print(f"正在重试{i}次。。。。。。。。")
            pass
    if i == 10:
        print("网络异常")
        exit(1)
    return response

def init_cookie(cookies):
    cookie_olds = "__gads=ID=2c0c910414bcee33:T=1657506109:S=ALNI_MbBt8zizXkDzZPwxG1a6202dk0pLg; _hjSessionUser_396266=eyJpZCI6ImYxNmNlOTgyLWE2NmQtNWI3Yi1hMTI0LWMyN2MyYmI0MGU5OSIsImNyZWF0ZWQiOjE2NTc1MDYxMDk3MjUsImV4aXN0aW5nIjp0cnVlfQ==; _gid=GA1.2.967853733.1658320693; __gpi=UID=000007933f7833f3:T=1657506109:RT=1658320686:S=ALNI_MZFF-qVE-uJhcT6Q3EHud-RloQNoQ; _hjShownFeedbackMessage=true; ___rl__test__cookies=1658370502676; OUTFOX_SEARCH_USER_ID_NCOO=2093932773.2851992; _hjIncludedInSessionSample=0; _hjSession_396266=eyJpZCI6ImU3NDA5NWI1LTI1MjQtNGUxNS04ODUyLTY2NmIyYzhiNzkyYSIsImNyZWF0ZWQiOjE2NTgzODM3OTUxODAsImluU2FtcGxlIjpmYWxzZX0=; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; ci_session=qk3l39839c8eudpdmbvi4u4bq06godjf; _gat=1; _ga_K5EV5SPMCL=GS1.1.1658383793.5.1.1658384229.53; _ga=GA1.1.109171264.1657506109; AWSALBTG=xn/2l+yGSKgrHx8ILxQf/UhRJKePsl7SCCBy8kh4Pb2xDAkVcQtqCc7yl7SjId+fsxXcoLaWaOqwqzQomLAr1N+oAmS15po8FZ1FiMbQft1ze9Vov4wHkYKy9ASuygZVUuk3KlV0djuSZ2NfD1H6YmjnfTqVYr9v2T/ptfyEyAUXQ4TU42g=; AWSALBTGCORS=xn/2l+yGSKgrHx8ILxQf/UhRJKePsl7SCCBy8kh4Pb2xDAkVcQtqCc7yl7SjId+fsxXcoLaWaOqwqzQomLAr1N+oAmS15po8FZ1FiMbQft1ze9Vov4wHkYKy9ASuygZVUuk3KlV0djuSZ2NfD1H6YmjnfTqVYr9v2T/ptfyEyAUXQ4TU42g=; AWSALB=kMY1kjVmIPlPjlEbgkRrIIFQU+unkeHZUNw+znDEzlgHhEB2DwhcpNQ+I8LUjwm5uIdN5QlJDHejmmqdD+fUx9CGj/dp4ahnIBX6mVaewLMaiT1Hm+kpn4QmA4M2; AWSALBCORS=kMY1kjVmIPlPjlEbgkRrIIFQU+unkeHZUNw+znDEzlgHhEB2DwhcpNQ+I8LUjwm5uIdN5QlJDHejmmqdD+fUx9CGj/dp4ahnIBX6mVaewLMaiT1Hm+kpn4QmA4M2"
    cookie_olds = cookie_olds.split(";")
    for c in cookie_olds:
        c_s = c.split(",")
        for cookie_old in c_s:
            name, value = re.match("(\S*?)=(.*)", cookie_old.strip()).groups()
            cookies.update({name.strip(): value.strip()})


def process_cookie(cookies_str, cookies):
    element = cookies_str.split(";")
    for c in element:
        c_s = c.split(",")
        for cookie in c_s:
            if len(cookie) > 30:
                cookie = cookie.strip()

                name, value = re.match("(\S*?)=(.*)", cookie.strip()).groups()
                if name == "Path":
                    continue
                cookies.update({name.strip(): value.strip()})


def set_cookie(cookies):
    verify_certificate = "https://www.beckett-authentication.com/verify-certificate"
    response = make_request(verify_certificate, method="get", headers=headers, timeout=(5, 10))
    cookies_str = response.headers['Set-Cookie']

    process_cookie(cookies_str, cookies)


def captcha_image(cookies):
    captchaImage = "https://www.beckett-authentication.com/bgsauthentication/captchaImage/?=0.2676218989787853"
    response = make_request(captchaImage, method="get", cookies=cookies, timeout=(5, 10))
    contetnt = response.content
    ocr = Ocr()
    res = ocr.my_predict(image=contetnt)
    cookies_str = response.headers['Set-Cookie']
    process_cookie(cookies_str, cookies)
    return res


def validateCaptcha(cookies, code, number):
    validateCaptcha = "https://www.beckett-authentication.com/bgsauthentication/validateCaptcha"
    data = {
        "captchaword": code.__str__(),
        "serial_num": number
    }
    response = make_request(url=validateCaptcha, data=data, cookies=cookies, headers=headers, timeout=(5, 10), method="post")
    if response.json()["success"] == 0:
        print("验证码错误")
        return 0
    cookies_str = response.headers['Set-Cookie']
    process_cookie(cookies_str, cookies)
    return 1



def listCertification(cookies, number):
    listCertification = "https://www.beckett-authentication.com/bgsauthentication/listCertification"
    data = {
        "serial_num": number
    }
    response = make_request(method="post", url=listCertification, data=data, cookies=cookies, headers=headers, timeout=(5, 10))
    search_result = response.json()["search_result"]
    cert_image = response.json()["cert_image"]
    soup = BeautifulSoup(search_result, "html.parser")
    table = soup.table
    if len(cert_image) == 0:
        name = "data/" + number + ".lxml"
    else:
        name = "data/" + number + "-image-" + ".lxml"
    with open(name, "w") as fp:
        fp.write(table.__str__())


def get_name_without_ext(path):
    basename = os.path.basename(path).split(".")[0].split("-")[0]
    return basename


def main(queue: Queue):
    cookies = {}
    print(threading.current_thread(), "start.................")
    while not queue.empty():
        number = queue.get()
        init_cookie(cookies)
        set_cookie(cookies)
        code = captcha_image(cookies)
        flag = validateCaptcha(cookies, code, number)
        if flag == 0:
            queue.put(number)
            continue
        listCertification(cookies, number)
        print(number)


def get_numbers(file):
    df = pd.read_excel(file, names=["data"], header=None)["data"]
    return df.tolist()


if __name__ == '__main__':
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
    numbers = get_numbers("numbers.xlsx")
    numbers_exists = []
    for file in os.listdir("data"):
        name = get_name_without_ext(file)
        numbers_exists.append(name)
    numbers = list(set(numbers).difference(set(numbers_exists)))
    queue_numbers = Queue()
    for number in numbers:
        queue_numbers.put(number)
    for i in range(10):
        threading.Thread(target=main, args=(queue_numbers,)).start()
