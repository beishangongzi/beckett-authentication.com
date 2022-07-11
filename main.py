# create by andy at 2022/4/1
# reference: 

import csv
import json
import os
import multiprocessing

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import ddddocr
from selenium.webdriver.common.by import By

import config
import get_driver
import ocr
import utils


def save_time_tower():
    pass


def begin(driver, number):
    print(number)
    serial_number = driver.find_element(by=By.CSS_SELECTOR, value="#serial_num")
    serial_number.send_keys(number)
    img = driver.find_element(by=By.CSS_SELECTOR, value="#register_capt")
    captcha = driver.find_element(by=By.XPATH, value='//*[@id="captchaword"]')
    i = 0
    while i <= 1000:
        i += 1
        if i == 100:
            res = input("重新识别了多次，但是还是错误，请输入正确的验证码\n")
        else:
            driver.find_element(by=By.CSS_SELECTOR, value='#refreshcap').click()
            if i == 1:
                time.sleep(0.1)  # 提高第一次运行的正确率，只能增加，不要降低
            time.sleep(0.2)  # 重新识别二维码的时间， 点击刷新
            try:
                img.screenshot(os.path.join("captcha", f"{multiprocessing.current_process().pid}.png"))
            except:
                try:
                    if driver.find_element(by=By.XPATH, value=config.NO_RECORD).text == config.NO_RECORD_TEXT:
                        print("No Record Found")
                        return 1
                    time.sleep(1)  # 这个时间很玄学，但是并不是每次都会使用他，只有有时候会用到，不用动。
                    print("验证是否跳转")
                    driver.find_element(by=By.XPATH, value=config.TRUE_NUMBER)
                    break
                except:
                    try:
                        if driver.find_element(by=By.XPATH, value=config.NO_RECORD).text == config.NO_RECORD_TEXT:
                            print("No Record Found")
                            return 1
                        time.sleep(0.5)  # 这个时间很玄学，但是并不是每次都会使用他，只有有时候会用到，不用动。
                        print("验证是否跳转第二次")
                        driver.find_element(by=By.XPATH, value=config.TRUE_NUMBER)
                        break
                    except:
                        pass
                    pass
                exit("不能找到验证码的错误，程序停止")

            res = ocr.ocr_local(os.path.join("captcha", f"{multiprocessing.current_process().pid}.png"))
        captcha.clear()
        captcha.send_keys(res)
        verify = driver.find_element(by=By.CSS_SELECTOR, value="#search")
        verify.click()
        time.sleep(2)  # 识别成功后，进行跳转，可能需要两秒，自己调整， 这里是最影响时间的:

        try:
            try:
                driver.find_element(by=By.XPATH, value=config.TRUE_NUMBER)
                break
            except:
                time.sleep(0.5)
                try:
                    driver.find_element(by=By.XPATH, value=config.TRUE_NUMBER)
                    break
                except:
                    time.sleep(0.5)
                    driver.find_element(by=By.XPATH, value=config.TRUE_NUMBER)
            break
        except:
            if driver.find_element(by=By.XPATH, value=config.NO_RECORD).text == config.NO_RECORD_TEXT:
                print("No Record Found")
                return 1
            print("验证码错误，重新填写")


@utils.logit()
def get_another(driver: webdriver.Firefox):
    another = driver.find_element(by=By.XPATH, value=config.ANOTHER)
    another.click()


@utils.logit()
def get_information(driver: webdriver.Firefox, query_number):
    true_number = driver.find_element(by=By.XPATH, value=config.TRUE_NUMBER).text.split(":")[-1].strip()
    # item_name = driver.find_element(by=By.XPATH, value=config.ITEM_NAME).text
    # signer_name = driver.find_element(by=By.XPATH, value=config.SIGNER_NAME).text
    print(driver.find_element(by=By.XPATH, value=config.NO_RECORD).text)
    if driver.find_element(by=By.XPATH, value=config.NO_RECORD).text == config.NO_RECORD_TEXT:
        print("No Record Found")
        return
    image = "有照片"
    try:
        driver.find_element(by=By.XPATH, value='//*[@id="image_data"]/div')
    except:
        image = "没照片"
    fields = driver.find_elements(by=By.XPATH, value=config.ALL_FIELDS)
    names = driver.find_elements(by=By.XPATH, value=config.ALL_FIELDS_NAME)
    res = {}
    for i in range(len(names)):
        name_text = names[i].text
        field_text = fields[i].text
        res.update({name_text: field_text})
    res.update({"image": image, "true_number": true_number, "query_number": query_number})
    with open("data/" + query_number + ".json", "w", encoding="utf-8") as f:
        json.dump(res, f)
    # return query_number, true_number, item_name, signer_name
    print(res)
    return res

def get_numbers():
    with open("numbers.csv") as f:
        return f.readlines()


def for_main(q: multiprocessing.Queue):
    print("{%s} 进程启动。。。" % multiprocessing.current_process().pid)
    driver = get_driver.get_driver()
    driver.get("https://www.beckett-authentication.com/verify-certificate")
    while True:
        if q.empty():
            print("{%s} 进程结束了。。。" % multiprocessing.current_process().pid)
            break
        number = q.get()
        if os.path.exists(f"data/{number}.json"):
            print(f"{multiprocessing.current_process().pid} 进程发现 {number}.json存在了")
        else:
            try:
                res = begin(driver, number)
                if res == 1:
                    driver.quit()
                    for_main(q)
                    return
                get_information(driver, number)
                get_another(driver)
            except Exception as e:
                print(e)
                q.put(number)
                driver.quit()
                for_main(q)
                return
    driver.quit()

def main():
    driver = get_driver.get_driver()
    driver.get("https://www.beckett-authentication.com/verify-certificate")
    numbers = get_numbers()
    save_file = "res.csv"
    with open(save_file, "w") as f:
        for number in numbers:
            number = number.strip()
            if os.path.exists(f"data/{number}.json"):
                print(f"{number} 已经下载了 ")
                continue
            try:
                begin(driver, number)
            except:
                driver.quit()
                main()
            information = get_information(driver, number)
            # f.write(",".join(information))
            # f.write("\n")
            get_another(driver)


def multi_process_main():
    if not os.path.exists("captcha"):
        os.mkdir("captcha")
    if not os.path.exists("data"):
        os.mkdir("data")
    q = multiprocessing.Queue()
    numbers = get_numbers()
    for number in numbers:
        q.put(number.strip())
    multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()
    # multiprocessing.Process(target=for_main, args=(q,)).start()

    
    

if __name__ == '__main__':
    # main()
    start = time.time()
    p = multiprocessing.Process(target=multi_process_main)
    p.start()
    p.join()
    end = time.time()
    print(end-start)
    print("每一秒有{}".format(150/(end-start)))
    print("一个需要{}".format((end-start)/150))
