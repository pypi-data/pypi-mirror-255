class myproxy_8680:
    def __init__(self, proxies=None, minvalue=0, maxvalue=10):
        if proxies is None:
            self.proxies = [
                {'address': 'http://10.10.90.75:1004', 'health': 10},
                {'address': 'http://10.10.90.75:1003', 'health': 10},
                {'address': 'http://10.10.90.75:1002', 'health': 10},
                {'address': 'http://10.10.90.75:1006', 'health': 0}
            ]
        else:
            self.proxies = proxies

        if minvalue:
            self.minvalue = minvalue
        else:
            self.minvalue = 0

        if maxvalue:
            self.maxvalue = maxvalue
        else:
            self.maxvalue = 10

        self.current_index = 0  # 当前选择的代理索引

    def get_healthiest_proxy(self):
        sorted_proxies = sorted(self.proxies, key=lambda x: x['health'], reverse=True)
        print(sorted_proxies)
        if sorted_proxies[0]['health'] == 0:
            for proxy in sorted_proxies:
                proxy['health'] = self.maxvalue
        return sorted_proxies[0]['address']

    def update_proxy_health(self, address, success):
        for proxy in self.proxies:
            if proxy['address'] == address:
                if success == "success":
                    proxy['health'] = min(proxy['health'] + 1, self.maxvalue)
                else:
                    proxy['health'] = max(proxy['health'] - 3, self.minvalue)
                break

