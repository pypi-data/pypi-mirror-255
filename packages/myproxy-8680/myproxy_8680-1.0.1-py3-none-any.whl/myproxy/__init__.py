from .myproxy import myproxy_8680

class Config(myproxy_8680):
    '''
    proxies 可以为 None ,也用如下格式可以自定义
    proxies = [
    {'address': 'http://10.10.90.75:1005', 'health': 5},
    {'address': 'http://10.10.90.75:1006', 'health': 7}
    ]

    minvalue 最小健康值  int

    maxvalue 最大健康值  int

    default   sucess +1   faild -3  ,全部最小值后 全体重置成最大值

    '''
    pass


'''
import requests
from requests.exceptions import ProxyError
import myproxy


def download_with_proxy(url, proxy_address):
    max_retries = 0  # 最大重试次数
    retries = 1
    while retries > max_retries:
        try:
            proxy_address = my_proxy.get_healthiest_proxy()
            resp = requests.get(url, proxies={'http': proxy_address, 'https': proxy_address})
            if resp.status_code == 200:
                my_proxy.update_proxy_health(proxy_address, 'success')
                return resp

        except ProxyError:
            my_proxy.update_proxy_health(proxy_address, 'fail')
            retries += 1

        except Exception as e:
            my_proxy.update_proxy_health(proxy_address, 'fail')
            retries += 1
            print(f"Request failed with error: {e}")

    return None


proxies = [
    {'address': 'http://10.10.90.75:1005', 'health': 5},
    {'address': 'http://10.10.90.75:1006', 'health': 7}
]

my_proxy = myproxy.MyProxy(proxies, 2, 7)
image_url = "https://www.baidu.com/img/flexible/logo/pc/result.png"
response = download_with_proxy(image_url, my_proxy)
if response is not None:
    with open('result.png', 'wb') as f:
        f.write(response.content)
    print("Image downloaded successfully.")
else:
    print("Failed to download image.")

'''
