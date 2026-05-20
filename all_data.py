#!/home/xu/Documents/python-env/code/bin/python
import requests
import json
import csv

url = "https://szjk.cnki.net/numerical-db-building/select/searchDatas"

# 定义 Cookie 变量
cookie_value = 'Ecp_ClientId=64780cb00bc7bb15b472c5870c5f10610UxLvaAIc5; _c_WBKFRo=cwqbXvV7D0mpDVQExhCD132SHtIVyx5ULzF5CFaN; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2219a14e667e32180-056d6c5eaca2194-43330223-2073600-19a14e667e41b6f%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%7D%2C%22%24device_id%22%3A%2219a14e667e32180-056d6c5eaca2194-43330223-2073600-19a14e667e41b6f%22%7D; tfstk=gw_KurjezmAI7uME9TqgqCuC8NFcylfF_95jrLvnVOBON6fk-_wF28BHI3jHEeORN9vZ-MqeqLhJITSHqLVeVOpWQaVeEk7tyTfrt2VUY39RLgjHETqee4LFSM0kKJ8RNtYYn-40o65eYUw0nqTJy-YewQiWOY0_5QLJOX7Uxb1ezUwMQtTRq6WHuJypAUN95QAkFU9BOAN9iBLSR3gIfA9wNUTWdDT6fIdjFQ9WP5C6QQTWFTT76F9wNU95FU9DL8psOL0RYehlq-uTE43RWBKpewvtkG_no3JX6dgW_GAL3K1BB4gkhC-8ps68pqRCyBI1PHrap6KCVwY1RRaXb3sRFCSae0pAV6jVcaVoyKsfNwtdbyH29G1A43_ck6xqnKdov5QS40-B_q1jFZ52EXyp6KVLy0oyb5R9n5Ft40-B_Cp098nr4hPN.; Ecp_loginuserbk=sh0350; Ecp_session=1; SID=090003; dimensionName=%E4%B8%AD%E5%9B%BD%E5%9F%8E%E5%B8%82%E7%BB%9F%E8%AE%A1%E6%95%B0%E6%8D%AE%E5%BA%93%EF%BC%88%E5%B9%B4%E5%BA%A6%E6%95%B0%E6%8D%AE%E7%89%88%EF%BC%89; dimensionId=595b3bf46c0b44469ae0d38f531cd789; Ecp_LoginStuts={"IsAutoLogin":false,"UserName":"sh0350","ShowName":"%E5%8D%8E%E4%B8%9C%E5%B8%88%E8%8C%83%E5%A4%A7%E5%AD%A6","UserType":"bk","BUserName":"","BShowName":"","BUserType":"","r":"SqAo9y","Members":[]}; c_m_LinID=LinID=WEEvREcwSlJHSldSdmVpdTVyUlJvV1Vtc2g1RWxQd2RSMVBubXZDMllxYz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot=11%2F02%2F2025%2021%3A59%3A51; LID=WEEvREcwSlJHSldSdmVpdTVyUlJvV1Vtc2g1RWxQd2RSMVBubXZDMllxYz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!; c_m_expire=2025-11-02%2021%3A59%3A51; Admin-Token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NjIwOTI1OTcsInVzZXJuYW1lIjoic2gwMzUwIn0.mpGnuCUAaa5b3TKJJ79X0fYkRPQyQ1ZgxRKO2hiE8Fs'

# 从 Cookie 中提取 Lid 的值
def extract_lid_from_cookie(cookie):
    """从 Cookie 字符串中提取 Lid 参数的值"""
    parts = cookie.split('; ')
    for part in parts:
        if part.startswith('LID='):
            return part[4:]  # 去掉 'LID=' 前缀
    return None

# 读取地区代码文件
def read_area_codes_from_csv(filename):
    """从CSV文件中读取所有地区代码，只保留最后两位为'00'的地区"""
    area_codes = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            adcode = row['adcode']
            # 跳过"中国"的代码（100000），通常不需要全国汇总数据
            if adcode != '100000' and adcode.endswith('00'):
            # if adcode != '100000':
                area_codes.append(adcode)
    return area_codes

def extract_leaf_indicators(zhibiao_file='indicator_example.json'):
    """
    从指标文件中提取所有叶子节点指标（没有子指标的指标）的code
    
    Args:
        zhibiao_file: 指标文件路径
        
    Returns:
        list: 叶子节点指标的code列表
    """
    try:
        with open(zhibiao_file, 'r', encoding='utf-8') as f:
            zhibiao_data = json.load(f)
        
        leaf_indicator_codes = []
        
        def traverse_nodes(nodes):
            """递归遍历节点，收集叶子节点的code"""
            for node in nodes:
                if not node.get('children'):  # 没有子节点，是叶子节点
                    if node.get('code'):
                        leaf_indicator_codes.append(node['code'])
                else:
                    traverse_nodes(node['children'])  # 递归遍历子节点
        
        if zhibiao_data.get('success') and zhibiao_data.get('result'):
            traverse_nodes(zhibiao_data['result'])
        
        print(f"从 {zhibiao_file} 中提取到 {len(leaf_indicator_codes)} 个叶子节点指标code")
        #print("提取的指标code列表:", leaf_indicator_codes)
        
        return leaf_indicator_codes
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {zhibiao_file}")
        return []
    except json.JSONDecodeError:
        print(f"错误: {zhibiao_file} 文件格式错误")
        return []
    except Exception as e:
        print(f"读取指标文件时发生错误: {e}")
        return []

# 提取 Lid
lid_value = extract_lid_from_cookie(cookie_value)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json;charset=UTF-8",
    "dimensionId": "595b3bf46c0b44469ae0d38f531cd789",
    "LID": lid_value,  # 使用提取的 Lid 值
    "Cookie": cookie_value  # 使用单独的 Cookie 变量
}

# 读取所有地区代码
area_codes_list = read_area_codes_from_csv('china.csv')
# 将地区代码列表转换为逗号分隔的字符串
area_codes_string = ','.join(area_codes_list)

leaf_indicator_list = extract_leaf_indicators("indicator.json")
#leaf_indicator_string = ','.join(leaf_indicator_list)

# 创建数据结构
data_dict = {}

def get_data(leaf, l_index):
    data = {
        "timeType": "1",
        "dates": "2000,2024",
        "dimensionId": "595b3bf46c0b44469ae0d38f531cd789",
        "areaCodes": area_codes_string,  # 使用从CSV读取的地区代码
        "indexIds": leaf,
        "json": "",
        "timeFrequency": "年度",
        "type": "xz",
        "xHeaders": "tb_indexes_name,area",
        "yHeaders": "date"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()

        if result.get("success"):
            # 提取地区信息
            if not result["result"]:
                return
            left_body = result["result"]["left"]["body"]
            right_body = result["result"]["right"]["body"]


            # 构建指标-城市与right_body的对应关系
            right_index = 0  # right_body的当前索引

            # 遍历左侧指标
            for indicator in left_body:
                indicator_name = indicator["label"]

                # 遍历该指标下的所有城市
                for city_info in indicator["children"]:
                    city_name = city_info["label"]

                    # 检查right_body中是否有对应数据
                    if right_index < len(right_body):
                        city_data = right_body[right_index]

                        # 初始化数据结构
                        if indicator_name not in data_dict:
                            data_dict[indicator_name] = {}

                        data_dict[indicator_name][city_name] = {}

                        # 提取各年份数据 - 使用body中实际存在的年份
                        for year_key, year_value in city_data.items():
                            # 过滤掉非年份的字段（如data_source等）
                            if year_key.endswith('年'):
                                data_dict[indicator_name][city_name][year_key] = year_value

                        # 移动到下一个right_body数据
                        right_index += 1
                    else:
                        print(f"警告: 没有找到 {indicator_name} - {city_name} 的对应数据")
            print(f"{l_index + 1} indicator")


        else:
            print(f"请求失败: {result.get('message', '未知错误')}")
    else:
        print(f"HTTP请求失败，状态码: {response.status_code}")

for l_index, leaf in enumerate(leaf_indicator_list):
    #import pdb; pdb.set_trace()
    get_data(leaf, l_index)


with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data_dict, f, ensure_ascii=False)

print(f"数据已成功保存到 data.json 文件，共处理了 {len(data_dict)} 条数据记录")
