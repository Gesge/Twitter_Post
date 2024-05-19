import requests
from urllib import parse
import json
import time

url = "https://twitter.com/i/api/2/search/adaptive.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&send_error_codes=true&simple_quoted_tweet=true&q={}&count=20&query_source=typed_query&pc=1&spelling_corrections=1&ext=mediaStats%2ChighlightedLabel%2CvoiceInfo&cursor={}"
url_token = 'https://api.twitter.com/1.1/guest/activate.json'
headers = {
    "authority":"twitter.com",
    "method":"GET",
    "scheme":"https",
    "accept":"*/*",
    "accept-encoding":"gzip, deflate",
    "accept-language":"en,zh;q=0.9",
    "authorization":"",
    "content-type": "application/json",
    "cookie": "",
    "pragma":"no-cache",
    "origin":"https://twitter.com",
    "referer": "https://twitter.com/elonmusk",
    "sec-ch-ua-mobile":"?0",
    "sec-ch-ua-platform":"Windows",
    "sec-fetch-dest":"empty",
    "sec-fetch-mode":"cors",
    "cache-control":"no-cache",
    "sec-fetch-site":"same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "x-client-transaction-id": "BWocxnHFb5XSCcoVONjKdA73RHqaKuBbFaUYg7ZVE8p+Rdld8awMLcL/1L+xG/qxRuCZ9gSTDlPry3p/le+JJiNfmz6VBg",
    "x-client-uuid": "3b7a33fb-bdc6-40e3-8cc7-82179b6a9b68",
    "x-csrf-token": "",
    "x-twitter-active-user":"yes",
    "x-twitter-auth-type": "OAuth2Session",
    "x-twitter-client-language": "en",
    "x-connection-hash": "" 
 }
q = '(from:{}) until:{} since:{}'

def formate_time2time_stamp(time_):
    return int(time.mktime(time.strptime(time_, "%Y-%m-%d")))

def time_stamp2formate_time(time_):
    return time.strftime("%Y-%m-%d", time.localtime(int(time_)))

def q_list_get(from_, since, until):
    since_p = formate_time2time_stamp(since)
    until_p = formate_time2time_stamp(until)
    step = 60 * 60 * 24
    while(since_p < until_p):
        next = since_p + step
        yield q.format(from_, time_stamp2formate_time(next), time_stamp2formate_time(since_p))
        since_p = next

def get_token():
    token = json.loads(requests.post(url_token, headers=headers).text)['guest_token']
    headers['x-guest-token'] = token


if __name__ == "__main__":
    from_ = 'elonmusk' # 用户名
    since = '2024-05-01' # 开始时间
    until = '2024-05-15' #结束时间
    '''
    num = 0
    tweet_list = []
    # get_token()
    for q_ in q_list_get(from_, since, until):
        print(q_)
        try:
            cursor = ''
            while True:
                if num > 500:
                    get_token()
                    num = 0
                num += 1
                res = requests.get(url.format(parse.quote(q_),parse.quote(cursor)), headers=headers)
                root = json.loads(res.text)
                print(root)
                quit()
                tweets = root['globalObjects']['tweets']
                if not tweets:
                    break
                for i in tweets.values():
                    tweet_list.append(i['full_text'])
                    print(i['full_text'])

                next = root.get('timeline',{}).get('instructions', [])
                if len(next) > 1:
                    cursor = next[-1].get('replaceEntry',{}).get('entry',{}).get('content',{}).get('operation',{}).get('cursor',{}).get('value', '')
                else:
                    cursor = next[0].get('addEntries',{}).get('entries',[{}])[-1].get('content',{}).get('operation',{}).get('cursor',{}).get('value', '')
                if not cursor:
                    cursor = ''
        except Exception as e:
            print(e)
    with open('out.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(tweet_list, ensure_ascii=False))
    '''
    # x = "https://twitter.com/i/api/graphql/5yhbMCF0-WQ6M8UOAs1mAg/SearchTimeline?variables=%7B%22rawQuery%22%3A%22(from%3Aelonmusk)%20until%3A2024-04-30%20since%3A2024-04-01%22%2C%22count%22%3A20%2C%22querySource%22%3A%22typed_query%22%2C%22product%22%3A%22Top%22%7D&features=%7B%22rweb_tipjar_consumption_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C%22articles_preview_enabled%22%3Atrue%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22creator_subscriptions_quote_tweet_preview_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_media_interstitial_enabled%22%3Atrue%2C%22rweb_video_timestamps_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D"
    # re = requests.get(x, headers=headers)
    # with open('out1.json', 'w', encoding='utf-8') as file:
    #     json.dump(re.json(), file, ensure_ascii=False)

    

        