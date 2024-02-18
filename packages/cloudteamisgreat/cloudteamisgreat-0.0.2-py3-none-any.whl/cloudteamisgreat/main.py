import os

from cloudteamisgreat.version import __version__ 
from cloudteamisgreat import logger
import cloudteamisgreat
import time
import os

# Folder containing command modules 
prompt = [
    "帥氣無法擋。",
    "魅力沒話說。",
    "老鼠愛大米，大家愛吉米。",
    "我只是講話比較浮誇。"
]

def parse(string):
    name = string.split(" ")
    return name[0]


def thinking():
    print("thinking", end="")
    for i in range(5):
        time.sleep(1) 
        print(".", end="") # 輸出一個點，不換行
        print("\r" + " " * (9 + i), end="\r") # 回到行首，用空白字元覆蓋原來的字串
        print("thinking" + "." * (i + 1), end="\r") # 回到行首，輸出新的字串
    print() 
        

def start():
    print('你好，我是 你是在哈囉嗎 語言模型')
    for i in range(4):
        
        print('===============================')
        query = input("你想問我什麼呢？")
        name = parse(query)
        thinking()
        if i < 2:
            print(f"{name} {prompt[i]}")
        else:
            print(f"{prompt[i]}")
        

if __name__ == "__main__":
    start()