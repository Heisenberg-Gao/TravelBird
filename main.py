import asyncio  # 导入异步IO库，用于实现异步编程
import os
import sys

from app import process_user_query
from services.agent_service import(
    process_user_query
)
from web import start_web


async def main():
    """
    主函数入口

    这个函数实现了应用程序的交互命令节目面，负责
    1.显示系统欢迎信息和使用说明
    2.处理用户输入的查询指令
    3.调用process_user_query函数处理用户查询
    4.处理用户退出命令和异常情况
    整个程序以循环方式运行，允许用户连接查询多个技术的关键词
    知道用户明确要求退出，所有异常都会被捕获并记录，确保程序稳定运行
    在本项目中，此函数是用户界面的主入口，提供了一个简单的交互界面
    """
    print("\n==========🌎小鸟地图旅行路线规划系统🌎==========\n")
    print("🌟Web服务已启动: http://localhost:8080")
    print("🌟输入你想去的地方，系统将帮你进行搜索和规划")
    print("🌟输入 'quit' 或 'exit' 退出文档")
    print("🌟提问示例：大理古城附近的景点，并给我提供具体的步行路线规划")
    print("🌟帮我导航从昆明到哈尔滨")
    print("🌟云南大学东陆校区附近的一些酒店推荐")
    print("\n===========================================\n")
    web = start_web()
    try:
        while True:
            user_query = input("\n请输入你想去的地方(输入 'quit' 或 'exit' 退出)：")
            if user_query.lower() in ['quit', 'exit']:
                print("感谢使用，再见！")
                break
            if not user_query.strip():
                print("查询内容不能为空，请重新输入")
                continue
            async with asyncio.TaskGroup() as tg:
               task = tg.create_task(process_user_query(user_query))
            print("\n输入新的查询或输入(' quit ' 或 ' exit ' 退出)")
    except KeyboardInterrupt:
        print("\n用户手动退出...")
    finally:
        # 使用结构化关闭流程
        print("\n🛑 开始关闭流程...")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        if sys.platform == 'win32':
            # Windows 需要额外处理
            os.system('taskkill /f /im node.exe >nul 2>&1')  # 确保终止所有 node 进程

if __name__ == "__main__":
    asyncio.run(main())
