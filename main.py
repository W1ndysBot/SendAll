# script/SendAll/main.py

import logging
import os
import sys
import asyncio

# 添加项目根目录到sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.config import owner_id
from app.api import *
from app.switch import load_switch, save_switch

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "SendAll",
)


# 私聊消息处理函数
async def handle_SendAll_private_message(websocket, msg):
    try:
        user_id = str(msg.get("user_id"))
        raw_message = str(msg.get("raw_message"))

        if raw_message.startwith("send"):
			if user_id not in owner_id:
            	send_private_msg(websocket,user_id,f"你没有权限执行群发命令")
                return
            
    except Exception as e:
        logging.error(f"处理xxx私聊消息失败: {e}")
        return


async def SendAll_main(websocket, msg):

    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)

    await handle_SendAll_private_message(websocket, msg)
