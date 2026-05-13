import urllib.request
import json

try:
    response = urllib.request.urlopen('http://localhost:8004/api/pets')
    data = response.read().decode('utf-8')
    pets = json.loads(data)
    print('状态码:', response.status)
    print('宠物数量:', len(pets))
    # 写入文件避免控制台编码问题
    with open('api_test_result.txt', 'w', encoding='utf-8') as f:
        f.write('状态码: ' + str(response.status) + '\n')
        f.write('宠物数量: ' + str(len(pets)) + '\n')
        f.write('宠物列表:\n')
        for pet in pets:
            f.write(f"  - {pet['name']} (¥{pet['price']}, 属性: {', '.join(pet['attributes'])})\n")
    print('测试结果已保存到 api_test_result.txt')
except Exception as e:
    print('错误:', e)