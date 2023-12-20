import warnings
warnings.filterwarnings("ignore")

import json
import openai
import os
import threading
import datetime
import sys
import warnings
warnings.filterwarnings("ignore")


# 创建一个事件对象
timeout_event = threading.Event()

def timeout(timeout_event, input_timeout):
    # 等待超时
    timeout_event.wait(input_timeout)
    if not timeout_event.is_set():  # 如果事件还没有被设置（没有新输入）
        print("\n小助手要休息咯，有什么问题再来问我吧")
        timeout_event.set()  # 设置事件，指示超时



openai.api_key = '_____________________'

MODEL_TYPE = "gpt-3.5-turbo-0613" # gpt-4

start_prompt = """
你是一个操作系统课程的教学助手，请在使用者需要时提供正确全面的操作系统知识。
"""

def ChatGPT(timeout_event, model="gpt-3.5-turbo-0613"):
    request = {
        "model": model,
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
                if timeout_event.is_set():
                    break
                request["messages"].append({"role": "user", "content": user_input})
                timeout_event.clear()

                try:
                    response = openai.ChatCompletion.create(
                        model=request["model"],
                        messages=request["messages"]
                    )
                    model_response = response.choices[0].message["content"]
                    print(model_response)
                    request["messages"].append({"role": "assistant", "content": model_response})
                except Exception as e:
                    print(f"OpenAI 接口调用出错: {e}")
                    # 可以在此处添加错误处理逻辑，例如重试或记录错误

        except EOFError:
            pass
        except KeyboardInterrupt:
            break

    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"chatgpt_history_{current_time}.json"

    # 保存文件到history 目录
    filepath = os.path.join('/workspaces/project/Amadeus/history', filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(request["messages"], file, ensure_ascii=False, indent=4)

    print(f"聊天历史已保存到 {filepath}")

def main():
    # 设置输入时间限制
    input_timeout = 60 # 默认值
    if len(sys.argv) > 1:
        try:
            input_timeout= int(sys.argv[1])
        except ValueError:
            print("请输入有效的整数作为等待时间。")
            sys.exit(1)
    # 确保history 目录存在
    if not os.path.exists('/workspaces/project/Amadeus/history'):
        os.makedirs('/workspaces/project/Amadeus/history')
    # 创建并启动计时器线程
    timer_thread = threading.Thread(target=timeout, args=(timeout_event, input_timeout))
    timer_thread.start()

    # 创建并运行输入线程
    input_thread = threading.Thread(target=ChatGPT, args=(timeout_event,))
    input_thread.start()

    input_thread.join()
    timer_thread.join()

if __name__ == "__main__":
    main()
