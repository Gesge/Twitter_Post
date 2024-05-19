import requests
import datetime
import itertools
import os
import time

# import httpx as htt
from tools import *
import socks
import socket

'''
代理IP测试：#亿牛云 爬虫代理加强版 代理服务器
proxyHost = "www.16yun.cn"
proxyPort = "31111"

# 代理验证信息
proxyUser = "16YUN"
proxyPass = "16IP"

# 构造代理服务器字典
proxies = {
    "http": f"http://{proxyUser}:{proxyPass}@{proxyHost}:{proxyPort}",
    "https": f"https://{proxyUser}:{proxyPass}@{proxyHost}:{proxyPort}"
}
'''


def main():
    # 基础请求url, 此处若网站规则变化则需要更改, 否则不变
    user_info_url_ = "https://twitter.com/i/api/graphql/qW5u-DAuXpMEG0zA1F7UGQ/UserByScreenName"
    user_twitter_url_ = "https://twitter.com/i/api/graphql/9zyyd1hebl7oNWIPdA8HRw/UserTweets"
    user_search_url_ = "https://twitter.com/i/api/graphql/5yhbMCF0-WQ6M8UOAs1mAg/SearchTimeline"

    # 获取代理信息
    proxies = get_json_data("./configs_user/proxy.json")
    if "https" in proxies.keys() and "http" in proxies.keys() and len(proxies["https"]) > 0 and len(proxies["http"]) > 0:
        # https 代理
        pass
    else:
        proxies = None
        # 设置socks代理
        # socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 10809)  # 替换为实际的代理地址和端口
        # 将socket的默认代理设置为socks代理
        # socket.socket = socks.socksocket

    # 构造请求头字典
    headers = get_json_data('./configs_user/request_headers.json')

    # 获取用户设定的信息
    print(">>>>>>开始获取用户设置的爬取信息")
    try:
        user_set_data = get_json_data("./configs_user/user_set.json")
        home_page = user_set_data["home_page"]
        start_date = user_set_data["start_date"]
        end_date = user_set_data["end_date"]
        if home_page == "":
            raise ValueError("请在configs_user/user_set.json中设置用户主页地址")
        username = home_page.split("/")[-1]
        print(f"用户名:{username}")
    except Exception as e:
        print(e)
        print("------获取用户设置的爬取信息失败")

    # 获取用户信息
    print(">>>>>>开始获取目标的用户信息")
    try:
        user_info_data = get_json_data("./configs/user_info_data.json")
        user_info_data["variables"]["screen_name"] = username # 要查询的用户名
        info_url_dict = get_url_params(user_info_data)
        user_info_url = user_info_url_ + str("?variables=") + str(info_url_dict["variables"]) + str("&features=") + str(info_url_dict["features"]) + str("&fieldToggles=") + str(info_url_dict["fieldToggles"])
        # 获取用户id和创建时间
        response_user_info = get_response_data(url=user_info_url, headers=headers, proxies=proxies)
        user_id = response_user_info["data"]["user"]["result"]["rest_id"]
        user_created_at = change_time_format(response_user_info["data"]["user"]["result"]["legacy"]["created_at"], '%Y-%m-%d')

        # 设定查询时间范围
        if start_date == "":
            start_date = user_created_at
            print(f"未设置起始日期，默认使用用户创建日期:{user_created_at}")
        if end_date == "":
            end_date = datetime.now().strftime('%Y-%m-%d')
            print(f"未设置截止日期，默认使用当前日期:{end_date}")
    except Exception as e:
        print(e)
        print("------获取目标用户信息失败")
        quit()

    # 获取用户twitter
    # user_twitter_data = get_json_data("./configs/user_twitter_data.json")
    #user_twitter_data["variables"]["userId"] = user_id # 替换用户id
    # 获取请求地址
    # twitter_url_dict = get_url_params(user_twitter_data)
    #user_twitter_url = user_twitter_url_ + str("?variables=") + str(twitter_url_dict["variables"]) + str("&features=") + str(twitter_url_dict["features"]) + str("&fieldToggles=") + str(twitter_url_dict["fieldToggles"])
    #response_user_twitters = get_response_data(url=user_twitter_url, headers=headers)#, proxies=proxies)
    
    
    # 获取推特
    print(">>>>>>开始获取目标用户的推文")
    try:
        all_twitters = []
        user_search_data = get_json_data("./configs/user_search_data.json")
        for q in q_list_get(username=username, since=start_date, until=end_date):
            try:
                user_search_data["variables"]["rawQuery"] = q
                search_url_dict = get_url_params(user_search_data)
                user_search_url = user_search_url_ + str("?variables=") + str(search_url_dict["variables"]) + str("&features=") + str(search_url_dict["features"])
                response_user_search = get_response_data(url=user_search_url, headers=headers, proxies=proxies)

                # 保存响应结果
                # with open("./out_data/twitters.json", 'w', encoding='utf-8') as f:
                #     json.dump(response_user_search, f, ensure_ascii=False, indent=4)

                one_batch_twitters = get_twitter_from_search(data=response_user_search, username=username)
                all_twitters.append(one_batch_twitters)
            except Exception as e:
                print(e)
                break
            
            time.sleep(2)

        all_twitters_list = list(itertools.chain(*all_twitters))
    except Exception as e:
        print(e)
        print("------获取推文失败")

    # 保存数据到文件
    try:
        if len(all_twitters_list) == 0:
            print("此时间段内用户没有推文，请换时间")
            quit()
        print(all_twitters_list[:5])
        file_path = f"./out_data/{username}_{start_date}_{end_date}_twitters.xlsx"
        if not os.path.exists("./out_data/"):
            os.makedirs("./out_data/")
        sava_data(data=all_twitters_list, file_path=file_path)
        print(f"保存数据到文件:{file_path}成功")
    except Exception as e:
        print(e)
        print("------保存数据到文件失败")

if __name__ == "__main__":
    main()

