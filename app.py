import asyncio
import traceback
from agents import Runner, RunConfig
from services.agent_service import (
    create_browser_agent,
    create_Gaode_agent,
    create_alipay_agent,
    create_controller_agent
)
"""
这个函数的作用相当于对用户提问的设置，对用户的问题进行设置的函数
"""
async def process_user_query(query: str) -> dict:
    """
    处理用户查询

    这个函数是整个应用的核心处理流程，负责：
    1.初始化所有的agent组件
    2.建立和协调agent之间的关系
    3.处理执行过程中的异常和资源清理

    工作流程依次为：创建浏览器agent->创建高德agent->创建alipay_agent -> 创建控制器 agent->
    执行 控制器agent 协调整个流程 ->处理和展示结果 -> 清理资源
    在项目中此函数是用户交互的入口函数，将用户的简单查询转化为完整的代理工作流

    Args:
        query(str):用户输入的查询 如：成都武侯祠附近的景点，并给我一些步行的路线规划；云南大学东陆校区附近的一些酒店推荐

    Returns:
        bool:处理才成功返回True，否则返回FALSE,用于向用户返回操作结果
    """
    cleanup_tasks = []
    playwright_server = None
    Gaode_server = None
    alipay_server = None
    try:
        print("========== 开始处理用户查询 ===========")

        #创建browser
        browser_agent, playwright_server = await create_browser_agent()
        print("playwright MCP 创建成功")
        # 创建高德agent
        # 负责使用Gaode
        Gaode_agent, Gaode_server = await create_Gaode_agent()
        print("高德 agent 创建成功")
        #创建alipay agent
        #负责支付环节
        alipay_agent, alipay_server = await create_alipay_agent()
        print("alipay agent 创建成功")

        # 创建控制器agent
        # 负责协调整个工作流程，管理浏览器agent和文档处理agent作为项目中的系统调度中心
        controller_agent = await create_controller_agent(Gaode_agent, browser_agent, alipay_agent)
        print("控制器 agent 创建成功")

        for tool in controller_agent.tools:
            print(f"控制器 agent 的可用工具是{tool.name}:{tool.description}")

        for handoff in controller_agent.handoffs:
            tool_name = f"transfer_to_{handoff.name.lower()}"
            print(f"控制器 agent 交接代理：{tool_name} > {handoff.name}")

        cleanup_tasks.extend([
            (playwright_server, "playwright"),
            (Gaode_server, "Gaode"),
            (alipay_server, "alipay")
        ])
        # 简化查询指令，专注于查询内容
        # formatted_query = f"""
        # 请在高德上查找关于“{query}”的技术文档并翻译成中文
        # """
        formatted_query = f"""
        请用高德MCP查找关于'{query}的一些回答'"""

        print(f"\n正在处理查询:'{query}'")
        print(f"这个操作可能需要几分钟时间...\n")

        result = await Runner.run(
            controller_agent,
            input=formatted_query,
            max_turns=50,  # 设置最大回合数，防止无限循环
            run_config=RunConfig(
                trace_include_sensitive_data=False  # 不在追踪中包含敏感数据，保护隐私和敏感信息
            )
        )
        print("\n========== 任务完成 ===========")
        if hasattr(result, "final_output"):
            print("\n工作流最终结果")
            print(result.final_output)
        return {
            "success": True,
            "type": "scenic" if "景点" in query else "hotel",
            "data": result.final_output if hasattr(result, "final_output") else str(result),
            "log": "查询成功"  # 添加调试信息
        }
    except asyncio.CancelledError as e:
        return {
            "success": False,
            "error": "请求被取消",
            "code": "ERR_CANCELLED"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "code": "ERR_UNKNOWN",
            "trace": traceback.format_exc()
        }
    # 在app.py的process_user_query函数中：
    finally:
        # 结构化清理流程
        async def safe_cleanup(server, name):
            try:
                if server:
                    print(f"🔄 正在清理 {name} 服务...")
                    await server.cleanup()
                    print(f"✅ {name} 服务已清理")
            except Exception as e:
                print(f"❌ 清理 {name} 时发生错误: {str(e)}")

        # 使用同一事件循环执行清理
        await asyncio.gather(
            safe_cleanup(playwright_server, "Playwright"),
            safe_cleanup(Gaode_server, "高德地图"),
            safe_cleanup(alipay_server, "支付宝"),
            return_exceptions=True  # 避免单个失败影响整体
        )

