# script/SendAll/main.py

import logging
import os
import sys
import re
import sqlite3


# 添加项目根目录到sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.config import owner_id
from app.api import *

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "SendAll",
)

DB_PATH = os.path.join(DATA_DIR, "group_id.db")


# 初始化数据库
def init_db():
    # 连接数据库，如果不存在会自动创建
    conn = sqlite3.connect(DB_PATH)

    # 创建一个游标对象
    cursor = conn.cursor()

    # 创建表格，如果不存在会自动创建，名为groups，包含id（自动递增）和group_id（群号）
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT NOT NULL UNIQUE
        )
    """
    )

    # 提交创建表格的操作
    conn.commit()

    conn.close()


# 添加群发的群号
def add_group_id(group_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO groups (group_id) VALUES (?)", (group_id,))
    conn.commit()
    conn.close()


# 删除群发的群号
def delete_group_id(group_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM groups WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()


# 获取所有群发的群号
def get_all_group_id():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT group_id FROM groups")
    group_ids = cursor.fetchall()
    conn.close()
    return [group_id[0] for group_id in group_ids]  # 返回一个列表


# 群聊消息处理函数
async def handle_SendAll_group_message(websocket, msg):

    try:
        # 确保数据目录存在
        os.makedirs(DATA_DIR, exist_ok=True)

        user_id = str(msg.get("user_id"))
        raw_message = str(msg.get("raw_message"))
        group_id = str(msg.get("group_id"))

        # 开放功能的群号
        if group_id not in ["910696002"]:
            return

        # 群发消息
        if raw_message.startswith("send"):

            if user_id not in owner_id:
                await send_private_msg(websocket, user_id, f"你没有权限执行群发命令")
                return

            # 初始化数据库
            init_db()

            if raw_message.startswith("sendadd"):
                match = re.search("sendadd(.*)", raw_message)
                if match:
                    added_group_id = match.group(1)
                    add_group_id(added_group_id)
                    await send_group_msg(
                        websocket, group_id, f"已添加群号: {added_group_id}"
                    )

            elif raw_message.startswith("sendrm"):
                match = re.search("sendrm(.*)", raw_message)
                if match:
                    deleted_group_id = match.group(1)
                    delete_group_id(deleted_group_id)
                    await send_group_msg(
                        websocket, group_id, f"已删除群号: {deleted_group_id}"
                    )

            elif raw_message.startswith("sendlist"):
                group_ids = get_all_group_id()
                if group_ids:
                    await send_group_msg(
                        websocket,
                        group_id,
                        f"当前群发群号: \n" + "\n".join(group_ids),
                    )
                else:
                    await send_group_msg(websocket, group_id, "当前没有群发群号")
            elif raw_message.startswith("sendall"):
                match = re.search(r"sendall(.+)", raw_message, re.DOTALL)
                if match:
                    content = match.group(1)
                    group_ids = get_all_group_id()
                    success_count = 0
                    failed_count = []
                    for group_id in group_ids:
                        if (
                            await send_group_msg(
                                websocket, group_id, content
                            )
                            != None
                        ):
                            success_count += 1
                        else:
                            failed_count.append(group_id)
                    failed_groups = "\n".join(failed_count) if failed_count else "无"
                    await send_group_msg(
                        websocket,
                        report_group_id,
                        f"已向 {success_count} 个群发送消息\n失败群号: \n{failed_groups}",
                    )

    except Exception as e:
        logging.error(f"处理群发群消息失败: {e}")
        return
