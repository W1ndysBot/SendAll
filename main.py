# script/SendAll/main.py

import logging
import os
import sys
import re
import sqlite3
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

DB_PATH = os.path.join(DATA_DIR,"group_id.db")


# 初始化数据库
def init_db():

    # 连接数据库，如果不存在会自动创建
    conn = sqlite3.connect(DB_PATH)
	
    # 创建一个游标对象
	cursor = conn.cursor()

	# 创建表格，如果不存在会自动创建，名为groups，包含id（自动递增）和group_id（群号）
	cursor.execute('''
    	CREATE TABLE IF NOT EXISTS groups (
        	id INTEGER PRIMARY KEY AUTOINCREMENT,
        	group_id TEXT NOT NULL
    	)
	''')

	# 提交创建表格的操作
	conn.commit()
	
    conn.close()


# 私聊消息处理函数
async def handle_SendAll_private_message(websocket, msg):
    try:
        user_id = str(msg.get("user_id"))
        raw_message = str(msg.get("raw_message"))

        if raw_message.startswith("send"):
            
			if user_id not in owner_id:
            	await send_private_msg(websocket,user_id,f"你没有权限执行群发命令")
                return

            if raw_message.startswith("sendadd"):
                match = re.search("sendadd(.*)",raw_message)
				if match:
                    added_group_id = match.group[0]
					
            
    except Exception as e:
        logging.error(f"处理xxx私聊消息失败: {e}")
        return


async def SendAll_main(websocket, msg):

    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)

    await handle_SendAll_private_message(websocket, msg)
