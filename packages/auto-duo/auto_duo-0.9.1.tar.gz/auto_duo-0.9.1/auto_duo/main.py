from .data import js_file, js_test
import subprocess
from subprocess import DEVNULL, PIPE
import os
from myBasics import strToBase64  # pip install myBasics
from time import time, sleep

try:
    _ = subprocess.check_output('node -v', shell=True, stderr=DEVNULL)
except:
    print("Please install nodejs and npm first.")
    os._exit(1)

try:
    _ = subprocess.check_output(js_test, shell=True, stderr=DEVNULL)
except:
    print("Please install the required packages first.")
    print("npm install crypto")
    print("npm install @aelfqueen/xmlhttprequest")
    os._exit(1)


def run_js(file_str: str):
    # 这是同步的
    base64_js = strToBase64(file_str)
    base64_js = f'eval(atob("{base64_js}"));'
    result = subprocess.run(f"node -e '{base64_js}'", shell=True, stderr=DEVNULL, stdout=PIPE)
    return result.stdout.decode('utf-8')


def find_output(js_output: str) -> list[str]:
    output_list = js_output.split('$jtc-auto-duo-js-output-hv9g8yvqunqcnuowybgobhuwr$jtc$')
    result = []
    for i in range(0, len(output_list)):
        if (i % 2 == 1):
            result.append(output_list[i])
    return result


def activate(qr_code: str) -> tuple[bool, str]:
    js = js_file.replace('$01$', 'A')
    js = js.replace('$02$', qr_code)
    result = run_js(js)
    result = find_output(result)
    if (len(result) >= 1 and result[0] == 'success'):
        # 这里是为了防止result长度为 0 报错，只要是success就一定长度至少 2
        return (True, result[1])
    result = run_js(js)
    result = find_output(result)
    if (len(result) >= 1 and result[0] == 'success'):
        # 这里是为了防止result长度为 0 报错，只要是success就一定长度至少 2
        return (True, result[1])
    if (len(result) <= 1):
        return (False, '')
    return (False, result[1])


def agree_forever(base64_dict):
    js = js_file.replace('$01$', 'C')
    js = js.replace('$03$', base64_dict)
    while True:
        # 正常应该是不会出错的，但为了防止出现特殊情况，还是加上
        _ = run_js(js)

