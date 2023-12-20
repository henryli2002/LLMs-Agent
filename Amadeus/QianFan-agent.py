import warnings
warnings.filterwarnings("ignore")

import requests
import json
import os
import threading
import sys
import datetime




API_KEY = 'jIHlGsMYHp4j1MrMZGNmYbCL'
SECRET_KEY = 'GzG1o4HC6G0qDVxPKcn9Zl4pv20j7CGA'

headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
          }   

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))



# 创建一个事件对象
timeout_event = threading.Event()

def timeout(timeout_event, input_timeout):
    # 等待超时
    timeout_event.wait(input_timeout)
    if not timeout_event.is_set():  # 如果事件还没有被设置（没有新输入）
        print("\n小助手要休息咯，有什么问题再来问我吧")
        timeout_event.set()  # 设置事件，指示超时






start_prompt = """
你是一个操作系统课程的教学助手，请在使用者需要时提供正确全面的操作系统知识。
"""

def QianFan(timeout_event, url, input_timeout):
    request = {
        "messages": [
            {
                "role": "user",
                "content": start_prompt
            },
            {
                "role": "assistant",
                "content": "当然，作为操作系统课程的教学助手，我可以提供关于操作系统的知识和解答。  \
                    如果你有任何关于操作系统的问题，如操作系统的基本概念,不同类型的操作系统、系统架构、进程管理、内存管理、文件系统和安全性等方面的问题，都可以随时提问。"
            },
        ]
    }
    
    while not timeout_event.is_set():
        try:
            print("请输入您的问题：")
            user_input = input()
            if user_input:
                request["messages"].append({"role": "user", "content": user_input})

                try:
                    # 重置计时器
                    timeout_event.clear()
                    # 重新启动计时器线程
                    timer_thread = threading.Thread(target=timeout, args=(timeout_event, input_timeout))
                    timer_thread.start()
                    response = requests.request("POST", url, headers=headers, data=json.dumps(request))
                    text = response.text
                    # 将 JSON 字符串解析为字典
                    data = json.loads(text)
                    # 提取 result 字段的内容
                    model_response = data['result']
                    print("\n回答：\n",model_response,'\n')
                    request["messages"].append({"role": "assistant", "content": model_response})
                    timeout_event.clear()

                except Exception as e:
                    print(f"QianFan 接口调用出错: {e}")
                    # 可以在此处添加错误处理逻辑，例如重试或记录错误
                
        except EOFError:
            pass


    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"qianfan_history_{current_time}.json"

    # 保存文件到 .history 目录
    filepath = os.path.join('/workspaces/project/Amadeus/history', filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(request["messages"], file, ensure_ascii=False, indent=4)

    print(f"聊天历史已保存到 {filepath}")

def main():
    # 设置输入时间限制
    input_timeout = 60 # 默认值
    if len(sys.argv) > 1:
        try:
            input_timeout = int(sys.argv[1])
        except ValueError:
            print("请输入有效的整数作为等待时间。")
            sys.exit(1)
    # 确保history 目录存在
    if not os.path.exists('/workspaces/project/Amadeus/history'):
        os.makedirs('/workspaces/project/Amadeus/history')

    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token=" + get_access_token()

    # 创建并启动计时器线程
    timer_thread = threading.Thread(target=timeout, args=(timeout_event, input_timeout))
    timer_thread.start()

    # 创建并运行输入线程
    input_thread = threading.Thread(target=QianFan, args=(timeout_event,url, input_timeout))
    input_thread.start()

    input_thread.join()
    timer_thread.join()

if __name__ == "__main__":
    main()
