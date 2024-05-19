import json
import urllib.parse
from datetime import datetime
import time
import requests
import traceback

import pandas as pd


def get_response_data(url, headers, proxies=None) -> dict:
    """
    获取响应数据
    :url: 请求url
    :headers: 请求头
    :proxies 代理
    """
    if proxies is None:
        response = requests.get(url, headers=headers)
    else:
        response = requests.get(url, headers=headers, proxies=proxies)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("请求失败,状态码: {}".format(response.status_code))


def get_json_data(path) -> dict:
    """
    获取json数据
    :param path: json文件路径
    :return: json数据字典
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def get_url_params(params: dict) -> dict:
    """
    将参数字典转换为url参数字符串
    :param params: 参数字典
    :return: url dict
    """
    str_url_dict = {}
    for key, value in params.items():
        if isinstance(value, dict):
            # print(json.dumps(value).replace(" ", ""))
            str_url = urllib.parse.quote(json.dumps(value).replace(" ", ""))
            str_url_dict[key] = str_url
        else:
            raise ValueError("参数类型错误,必须为字典类型")
    
    return str_url_dict 


def change_time_format(time_str: str, formate: str=None) -> str:
    """
    将时间字符串转换为数字类型
    :param time_str: 时间字符串
    :return: 数字类型时间
    """
    data_time = datetime.strptime(time_str, "%a %b %d %H:%M:%S %z %Y")
    if formate is None:
        data_time = datetime.strftime(data_time, '%Y-%m-%d %H:%M:%S')
    else:
        data_time = datetime.strftime(data_time, formate)
    return data_time


def formate_time2time_stamp(time_):
    return int(time.mktime(time.strptime(time_, "%Y-%m-%d")))


def time_stamp2formate_time(time_):
    return time.strftime("%Y-%m-%d", time.localtime(int(time_)))


def get_twitter_from_homepage(data: json, username) -> list:
    """
    从主页response中获取数据
    :data 获取的json对象
    :return 数据列表, 每条数据为字典类型
    """
    # 第一层数据
    all_twitters = []
    data_instructions = data['data']["user"]["result"]["timeline_v2"]["timeline"]["instructions"]
    for instruction in data_instructions:
        if instruction["type"] != "TimelineAddEntries":
            continue
        for item in instruction["entries"]:
            try:
                if "itemContent" not in item["content"].keys() or "tweet_results" not in item["content"]["itemContent"].keys() or "legacy" not in item["content"]["itemContent"]["tweet_results"]["result"].keys():
                    continue

                twitter_info = item["content"]["itemContent"]["tweet_results"]["result"]["legacy"]
                text, cr_time = twitter_info["full_text"],  twitter_info["created_at"]
                cr_time = change_time_format(cr_time)
                twitter_url = 'https://twitter.com/' + username + str("/status/") + item["entryId"].split("tweet-")[-1].split("-")[0]
                # print(str(twitter_info["is_quote_status"]))
                # 判断是否转发
                if twitter_info["is_quote_status"] is True:
                    is_quote = "re"
                elif twitter_info["is_quote_status"] is False:
                    is_quote = "1"
                one_twitter = {
                    "time": cr_time,
                    "content": text,
                    "url": twitter_url,
                    "is_quote": is_quote
                }
                all_twitters.append(one_twitter)
            except:
                print(traceback.format_exc())
                continue
    
    return all_twitters


def get_twitter_from_search(data: json, username) -> list:
    """
    从search response中获取数据
    :data 获取的json对象
    :return 数据列表, 每条数据为字典类型
    """
    # 第一层数据
    all_twitters = []
    data_instructions = data['data']["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"]
    for instruction in data_instructions:
        if instruction["type"] != "TimelineAddEntries":
            continue
        # 第二层数据
        for item in instruction["entries"]:
            try:
                if "itemContent" not in item["content"].keys() or "tweet_results" not in item["content"]["itemContent"].keys() or "legacy" not in item["content"]["itemContent"]["tweet_results"]["result"].keys():
                    continue

                twitter_info = item["content"]["itemContent"]["tweet_results"]["result"]["legacy"]
                text, cr_time = twitter_info["full_text"],  twitter_info["created_at"]
                cr_time = change_time_format(cr_time)
                twitter_url = 'https://twitter.com/' + username + str("/status/") + item["entryId"].split("tweet-")[-1].split("-")[0]
                # print(str(twitter_info["is_quote_status"]))
                # 判断是否转发, 1转发, 0非转发
                if twitter_info["is_quote_status"] is True:
                    is_quote = "repost"
                elif twitter_info["is_quote_status"] is False:
                    is_quote = ""
                one_twitter = {
                    "time": cr_time,
                    "content": text,
                    "url": twitter_url,
                    "remark": is_quote
                }
                all_twitters.append(one_twitter)
            except:
                print(traceback.format_exc())
                continue
    
    return all_twitters


def sava_data(data: list, file_path: str):
    """
    将数据保存为csv文件, 按照时间进行升序排序
    :param data: 数据列表, 每一个数据为字典类型
    :param file_path: 文件路径
    :return: None
    """
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(by="time", ascending=True)
    df.drop_duplicates(inplace=True)
    if file_path.endswith(".csv"):
        df.to_csv(file_path, index=False)
    elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        df.to_excel(file_path, index=False, engine="xlsxwriter")


def q_list_get(username, since, until):
    """
    按时间段获取推文 以一月为单位
    : since: 开始时间
    : until: 结束时间
    """
    q = '(from:{}) until:{} since:{}'
    since_p = formate_time2time_stamp(since)
    until_p = formate_time2time_stamp(until)
    step = 60 * 60 * 24 * 5
    while(since_p < until_p):
        next = since_p + step
        yield q.format(username, time_stamp2formate_time(next), time_stamp2formate_time(since_p))
        since_p = next



if __name__ == '__main__':
    username = "elonmusk"
    data = get_json_data("./search.json")
    twitters = get_twitter_from_search(data=data, username=username)
    # print(twitters)
    file_path = "./out_data/" + username + "1.csv"
    sava_data(data=twitters, file_path=file_path)