import json
import os
import random
import time
from datetime import datetime, timedelta
from typing import Any

import requests
from playwright.sync_api import sync_playwright


def get_config():
    """获取环境变量配置"""
    config = {
        # 需要添加Action Secrets，在action的yaml中将secrets转换为环境变量（env: SCKEY: ${{ secrets.SCKEY }}）
        # 添加Action Secrets的路径如下：
        # Settings -> Security -> Secrets and variables -> Actions -> New repository secrets
        'SCKEY': os.environ.get('SCKEY'),  # serv酱key
        'PUSHPLUS_TOKEN': os.environ.get('TOKEN'),  # pushplus token
        'TG_BOT_TOKEN': os.environ.get('TG_BOT_TOKEN'),  # telegram bot token
        'TG_CHAT_ID': os.environ.get('TG_CHAT_ID'),  # telegram chat id
        'SERV_LIST': os.environ.get('SERV_LIST')
    }

    if config['SERV_LIST'] is None:
        print('SERV_LIST为空，直接退出')
        exit(0)

    return config


def date_format(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')


def push(config, title, content):
    """根据配置推送信息"""
    sckey = config.get('SCKEY')
    pushplus_token = config.get('PUSHPLUS_TOKEN')
    tg_bot_token = config.get('TG_BOT_TOKEN')
    tg_chat_id = config.get('TG_CHAT_ID')

    # 检查是否所有的token都未配置
    if not any([sckey, pushplus_token, tg_bot_token and tg_chat_id]):
        print('未配置相关token，跳过推送')
        return

    if sckey:
        if push_sct(sckey, title, content):
            print('server酱推送成功')
        else:
            print('server酱推送失败')

    if pushplus_token:
        if push_plus(pushplus_token, title, content):
            print('push_plus推送成功')
        else:
            print('push_plus推送失败')

    if tg_bot_token and tg_chat_id:
        if push_tg(tg_bot_token, tg_chat_id, f"{title} - {content}"):
            print('Telegram推送成功')
        else:
            print('Telegram推送失败')


def push_sct(sckey, title, content):
    """server酱推送"""
    now_utc = date_format(datetime.utcnow())
    now_bj = date_format(datetime.utcnow() + timedelta(hours=8))
    content_with_timestamp = f"{now_bj}(UTC {now_utc}): {content}"
    url = "https://sctapi.ftqq.com/{}.send?title={}&desp={}".format(sckey, title, content_with_timestamp)
    response = requests.post(url)
    if response.status_code == 200:
        return True
    else:
        return False


def push_plus(plus_token, title, content):
    """pushplus推送"""
    now_utc = date_format(datetime.utcnow())
    now_bj = date_format(datetime.utcnow() + timedelta(hours=8))
    content_with_timestamp = f"{now_bj}(UTC {now_utc}): {content}"
    headers = {'Content-Type': 'application/json'}
    json_data = {"token": plus_token, 'title': title, 'content': content_with_timestamp, "template": "json"}
    resp = requests.post(f'http://www.pushplus.plus/send', json=json_data, headers=headers).json()
    if resp['code'] == 200:
        return True
    else:
        return False


def push_tg(tg_bot_token, tg_chat_id, message):
    """Telegram推送"""
    url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"
    payload = {
        'chat_id': tg_chat_id,
        'text': message,
        # 可以让接收消息的用户在收到消息时看到一个可点击的按钮，点击按钮后会打开指定的链接。
        # 'reply_markup': {
        #     'inline_keyboard': [
        #         [
        #             {
        #                 'text': '问题反馈❓',
        #                 'url': 'https://t.me/yxjsjl'
        #             }
        #         ]
        #     ]
        # }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return True
        else:
            print(f"发送消息到Telegram失败: {response.text}")
            return False
    except Exception as e:
        print(f"发送消息到Telegram时出错: {e}")
        return False


def serv_login(serv_list):
    print(f'SERV_LIST个数:{len(serv_list)}')
    login_records = []

    with sync_playwright() as p:
        # for循环中公用一个浏览器，减少重复创建开销
        browser = p.chromium.launch(headless=True)
        try:
            for i, serv in enumerate(serv_list):
                username = serv['username']
                password = serv['password']
                panel = serv['panel']
                print(f'[{i}]: {panel} | {username}')
                service_name = 'ct8' if 'ct8' in panel else 'serv00'

                is_logged = login(browser, username, password, panel)

                now_utc = date_format(datetime.utcnow())
                now_beijing = date_format(datetime.utcnow() + timedelta(hours=8))

                # 将panel、username和is_logged信息以字典形式添加到列表中
                login_records.append({'panel': panel, 'username': username, 'is_logged': is_logged})

                if is_logged:
                    print(f'{service_name}账号 {username} 于北京时间 {now_beijing}（UTC时间 {now_utc}）登录 [成功]')
                else:
                    print(f'{service_name}账号 {username} 于北京时间 {now_beijing}（UTC时间 {now_utc}）登录 [失败]')

                # 随机延时1-8秒
                time.sleep(random.randint(1, 8))

        finally:
            if browser:
                browser.close()
            return login_records


def login(browser: Any, username, password, panel):
    page = None
    try:
        print('1-1 打开登录页面')
        page = browser.new_page()
        url = f'https://{panel}/login/?next=/'
        page.goto(url, timeout=60000)

        print('1-2 输入账号密码')
        page.fill('#id_username', username)
        page.fill('#id_password', password)

        print('1-3 点击登录按钮')
        page.click('#submit')

        print('1-4 检查是否登录成功')
        return page.wait_for_selector('a[href="/logout/"]', timeout=60000) is not None

    except Exception as e:
        print(f'登录时出现错误: {e}')
        return False

    finally:
        if page:
            page.close()


def main():
    print('0.获取配置')
    # get_config()找不到配置会直接退出
    config = get_config()

    # 解析SERV_LIST配置，格式如下：
    # [
    #   {"username": "serv00的账号", "password": "serv00的密码", "panel": "panel6.serv00.com"},
    #   {"username": "ct8的账号", "password": "ct8的密码", "panel": "panel.ct8.pl"}
    # ]
    serv_list = json.loads(config['SERV_LIST'])
    print('1.登录')
    login_records = serv_login(serv_list)

    print('2.推送')
    # 将login_records转换为最精简的content传入push函数
    content = '\n'.join(
        [f"{record['panel']} | {record['username']} | {'Y' if record['is_logged'] else 'N'}" for record in
         login_records])
    print(content)
    push(config, 'serv00/ct8登录', content)


if __name__ == '__main__':
    main()
