"""
这是创建智能体的服务
"""
import asyncio  # 导入异步IO库，用于实现异步编程
import os  # 导入操作系统模块，在本项目中用于读取环境变量文件
import sys
import traceback  # 用于捕获和打印详细的异常信息
from typing import Any  # 导入类型提示工具，增强代码的提示安全，在本项目中用于标记函数的参数和返回值类型


"""
OpenAI agents SKD 相关导入
"""
from agents import (
    Agent,  # agent类，用于定义和执Agent任务，本项目中我们需要构建浏览器，文档处理和控制器代理、
    Model,  # Model类， 用于定义我们自定义的模型提供商函数返回的类型
    ModelSettings,  # ModelSetting类， 用于配置模型参数， 如温度等， 在本项目中用于调整各代理的行为特征
    Runner,  # 在本项目中用于启动和协调 agent
    RunConfig,  # 在本项目中用于配置和运行环境和追踪选项
    set_tracing_disabled,  # 在本项目中用于禁用追踪功能的函数，避免发送数据到OpenAI
    # function_tool,  # 在本项目中用于创建一个markdown浏览器工具让agent使用
    ModelProvider,  # 在本项目中用于实现 DeepSeek API 兼容的实例
    OpenAIChatCompletionsModel,  # 在本项目中用于连接DeepSeek API
    RunContextWrapper,  # 在本项目中用于钩子函数参数的类型进行定义
    AgentHooks,  # agent 生命周期钩子接口， 用于监控和干预 agent 执行过程，在本项目中用于追踪执行进度和提取执行结果
)
from agents.mcp import MCPServerStdio  # 使用本地通信，标准化输入输出与本地 MCP 通信，在本项目中创建Playwright MCP 服务的连接
from openai import AsyncOpenAI  # 导入OpenAI异步客户端，在本项目中用于创建DeepSeek API 的异步通信客户端
from dotenv import load_dotenv  # 导入dotenv, 在本项目中用于加载环境变量

load_dotenv()  # 加载环境变量

# 从环境变量中读取这些值
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
Gao_De_API = os.getenv("Gao_De_API")  # 高德地图的API
AMAP_MAPS_API_KEY = os.getenv("AMAP_MAPS_API_KEY")
AP_APP_ID = os.getenv("AP_APP_ID")  # 支付宝
AP_APP_KEY = os.getenv("AP_APP_KEY")  # 支付宝
AP_PUB_KEY = os.getenv("AP_PUB_KEY")  # 支付宝

# 验证参数是否存在
if not API_KEY:
    raise ValueError("API_KEY is not set")
if not BASE_URL:
    raise ValueError("BASE_URL is not set")
if not MODEL_NAME:
    MODEL_NAME = "deepseek-chat"

# 用OpenAI的函数指向deepseek
client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


# 创建模型提供商的类
class DeepSeekModelProvider(ModelProvider):
    """
    自定义模型提供商

    实现ModerProvider接口，提供自定义的模型实例
    这使应用程序可以使用DeepSeek等于OpenAI兼容的API替代原生openai接口
    在本项目中，他作为所有agents与模型交互的统一入口，确保一致性的模型行为
    """

    # 实现ModelProvider接口的get_model方法
    def get_model(self, model_name: str) -> Model:
        """
        获取模型实例
        根据提供的模型名称，船舰并返回一个模型实例
        返回的是与OpenAI兼容的实例
        """
        return OpenAIChatCompletionsModel(
            model=model_name,
            openai_client=client
        )


# 创建模型提供商实例
# 这个实例将作用于所有Agent
model_provider = DeepSeekModelProvider()

# 这是为了防止 SDK默认向OPENAI发送追踪数据进行agent调试，我们使用的是deepseek API，是没有open API密钥的，防止他自动发送给openAI
set_tracing_disabled(True)
async def cleanup(self):
    try:
        await self.connection.close()
    except RuntimeError as e:
        if "Event loop isa closed" not in str(e):
            raise

class GaodeHooks(AgentHooks):
    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        """
        在 agent 开始执行的时候调用
        """
        print(f"[你的旅行助手] agent {agent.name} 开始执行...")

    async def on_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        """
        当 agent 结束运行时触发
        """
        print(f"[你的旅行助手] agent {agent.name} 完成执行，执行结果： \n {output[:300]}")


class BrowserAgentHooks(AgentHooks):
    """
    用于监控浏览器agent执行的钩子

    这个类实现了 AgentHooks 接口，用于监控和处理浏览器agent的生命周期时间
    只要功能是：
    1.跟踪agent执行开始结果
    2.解析agent返回的markdown格式数据
    3.保存这些数据以便后续处理和分析

    在本项目中，他是连接浏览器agent和文档处理agent的关键环节，负责从浏览器代理返回结果中提取结构化数据
    """

    def __init__(self):
        super().__init__()

    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        """
        在 agent 开始执行的时候调用
        """
        print(f"[浏览器代理] agent {agent.name} 开始执行...")

    async def on_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        """
        当 agent 结束运行时触发
        """
        print(f"[浏览器代理] agent {agent.name} 完成执行。执行结果：\n{output[:300]}")


# async def create_browser_agent():
#     """
#     创建浏览器交互Agent
#     这个函数负责初始化和配置浏览器交互agent 包括：
#     1.创建 playwright MCP 服务器连接实例
#     2.配置浏览器agent,包括指令指令和模型设置
#     3.设置监控钩子显示执行结果

#     浏览器agent负责使用playwright打开浏览器访问高德地图,访问用户询问的有关读点路线问题
#     在本程序中，此函数创建了负责网络交互的agent, 是整个工作流的第一个关键组件
#     returns:
#        tuple:包含两个元素的元组
#        1.Agent:配置好的浏览器交互为agent实例
#        2.MCP :playwright MCP 服务器连接实例
#     """
#     # 创建playwright MCP服务连接实例，使用 MCPServerStdio 标准输入输出
#     playwright_server = MCPServerStdio(
#         name="playwright",
#         params={
#             "command": "npx",  # 运行npx命令，用于执行playwright MCP 服务
#             "args": ["-y", "@playwright/mcp@latest"],  # 启用最新版的playwright MCP服务
#             "env": {}  # 环境变量，在本项目中不需要额外配置
#         },
#         cache_tools_list=True  # 启用工具缓存，减少重复运行 MCP服务运行工具列表查询的开销
#     )

#     try:
#         # 连接playwright MCP 服务
#         print("正在连接 playwright MCP 服务...")
#         await playwright_server.connect()
#         print("playwright MCP 服务连接成功")

#         # 获取 MCP服务可用工具列表
#         tools = await playwright_server.list_tools()
#         print(f"playwright MCP 服务可用工具列表{len(tools)}")

#         # 创建浏览器 agent 钩子
#         # 用于监控和处理六拉起的执行过程和结果，在项目中作为agent生命周期的监控组件
#         browser_hooks = BrowserAgentHooks()

#         # 创建浏览器agent
#         # 配置一个专门用于打开百度地图网页的智能体，帮助我们打开百度地图
#         browser_agent = Agent(
#             name="GaoDeDocumentBrowser",  # 代理名称，作为代理的唯一标识符
#             # 详细的agent指导，指导这个agent在百度地图上进行路线检索，在项目中作为一个agent的执行策略和行为规划
#             instructions="""
#             你是一个专业的高德地图规划专家，你的任务是使用浏览器工具访问高德地图,搜索用户指定的技术关键词，并提取最权威，最直接相关的官方仓库文档内容
#             按照以下步骤工作：
#             ##最重要的事情##：不要点击网页内的图片，不要点击相册内的文件，也就是img文件。
#             1.导航到百度地图(https://map.baidu.com)网页
#             2.使用平台内的搜索功能，注意用户是询问一个景点的问题，还是询问这个景点附近的景点的问题，理解后再把问题输入到平台内的搜索栏中
#             3.根据用户信息，在网页内得到排序后的各个景点后，依次点击这几个景点展现给用户
#             4.禁止点击网页内的图片
#             注意：你的唯一任务是获取文档并按格式返回结果， 不要尝试执行额外的任务或动用其他代理，
#             **返回格式（必须严格按照以下结构）：**

#             **如果用户询问的是酒店的信息，那么按照下列格式
#                 --------返回内容从这里开始--------
#                 ## 酒店的信息：
#                 **酒店的名字**
#                  - 地址:[]
#                  - 评分:[“没有就填写无”]
#                  - 介绍:["没有就写无"]
#                 --------返回内容到这里结束--------
#             **如果用户询问的是关于景点路线规划的问题
#                 --------返回内容从这里开始--------
#                 ## 景点的信息：
#                   **景点名称**  
#                   - 地址：[] 
#                   - 特色：[]
#                   - 评分：[“没有就填写无”]  
#                   - 门票：[“没有就填写免费”]  
#                 ##路线规划
#                 总体的路线规划：第一个景点的名称 -> 第二个景点的名称 ->...->最后一个景点的名称
#                 ##详细路线
#                   **景点名称** -> **景点名称**:
#                   - 步行距离：[]米，约[]分钟
#                   - 路线规划：具体要怎么走的导航内容
#                  ##天气
#                   **天气情况：（输出用户询问消息当天的天气信息）
#                 --------返回内容到这里结束--------
#                 **重要限制和说明:**
#                 1.严格按照上面的格式返回信息。不要添加额外的说明的解释
#                 2.得到了多个地点，那么按先近后远的顺序，以->来连接不同的地点位置，然后给出从第一个地点依次到最后一个地点的路线规划，一定要用->来连接不同的地点
#                 3.注意要返回一个总体的路线规划，从近到远，依次连接每一个景点
#                 4.与Gaode_agent一起完成这个任务
#             **重要限制和说明:**
#             1.严格按照上面的格式返回信息。不要添加额外的说明的解释
#             2.不要点击网页内的图片，不能点击网页内的图片
#            """,
#             mcp_servers=[playwright_server],  # 关联MCP服务器，提供浏览器自动化能力
#             hooks=browser_hooks,  # 添加浏览器 agent 钩子，用于监控和处理浏览器 agent 的执行过程和结果
#             model=model_provider.get_model(MODEL_NAME),  # 使用我们自定义的模型提供商，确保agent使用正确的模型
#             model_settings=ModelSettings(
#                 temperature=0.3,  # 设置温度值
#                 top_p=0.9,  # 设置词汇多样性
#                 tool_choice="auto"  # 设置工具选择策略
#             )
#         )
#         return browser_agent, playwright_server
#     except Exception as e:
#         print(f"创建浏览器 agent 时发生异常: {e}")
#         await playwright_server.cleanup()  # 确保清理MCP服务器资源，防止资源泄露和进程残留
#     await playwright_server.cleanup()


async def create_Gaode_agent():
    """
    创建旅行路线等规划agent,调用高德地图的MCP，来回答用户的关于旅行的一些问题
    这个函数负责回答用户的旅行问题用法；
    1.从用户的问题中分析是不是要进行旅行规划
    2.调用高德的MCP工具
    3.从而输出，以规范的语言输出
    """
    Gaode_server = MCPServerStdio(
        name="amap-maps",
        params={
            # "description": "高德mcp",
            # "isActive": True,
            "command": "npx",
            "args": [
                "-y",
                "@amap/amap-maps-mcp-server"
            ],
            "env": {
                "AMAP_MAPS_API_KEY": f"{AMAP_MAPS_API_KEY}"
            }
        },
        cache_tools_list=True
    )
    try:
        # 连接Gaode MCP 服务
        print("正在连接 Gaode MCP 服务...")
        await Gaode_server.connect()
        print("Gaode MCP 服务连接成功")

        # 获取 MCP服务可用工具列表
        tools = await Gaode_server.list_tools()
        print(f"Gaode MCP 服务可用工具列表{len(tools)}")

        # 创建高德地图 agent 钩子
        # 用于监控和处理六拉起的执行过程和结果，在项目中作为agent生命周期的监控组件
        Gaode_hooks = GaodeHooks()
        # 创建高德地图agent
        # 配置一个专门用于高德地图检索路线规划的智能体，在项目中负责输出关于旅行的一些建议
        Gaode_agent = Agent(
            name="Gaode_map",  # 代理名称，作为代理的唯一标识符
            # 详细的agent指导，指导这个agent在高德地图进行检索，在项目中负责输出路线信息
            instructions="""
            你是高德地图领域专家 Agent，能够精准且全面地解答与高德地图相关的各类问题，包括但不限于地图功能使用、导航设置、POI（兴趣点）搜索、开发者 API 调用、与高德地图 MCP（Model Context Protocol）服务器交互等方面内容。
            具体任务:
            **重点：在规定的格式中根据用户所提的问题选取对应的格式来输出**
            1.旅行路线解答：当用户询问某一个地方的一些景点的相关问题的时候，搜索关于景点的内容，并且按照规定的返回格式输出给用户
            2.酒店问题的解答：当用户询问关于某一个地方附近的酒店的相关问题的时候，搜搜关于附近酒店的内容，并且按照规定的格式输出给用户
            3.你的工作流程：
            a.如果用户询问的是关于酒店的内容，那么就按规定格式输出关于酒店的信息
            b.如果用户询问的是关于景点的内容，那么按规定的格式输出关于景点的信息，提醒：输出规定好的单个景点的信息，也就是 ## 景点的信息 -> 接着第一个景点去第二个景点的路线规划，
            第二个景点去第三个景点的路线规划，以此类推也就是##路线规划 -> 最后输出天气


            如果得到了多个地点，那么按先近后远的顺序，以 -> 来连接不同的地点位置，然后给出从第一个地点依次到最后一个地点的路线规划

            **返回格式（必须严格按照以下结构）：**

            **如果用户询问的是酒店的信息，那么按照下列格式
                --------返回内容从这里开始--------
                ## 酒店的信息：
                **酒店的名字**
                 - 地址:[]
                 - 评分:[“没有就填写无”]
                 - 介绍:["没有就写无"]
                --------返回内容到这里结束--------
            **如果用户询问的是关于景点路线规划的问题
                --------返回内容从这里开始--------
                ## 景点的信息：
                  **景点名称**  
                  - 地址：[] 
                  - 特色：[]
                  - 评分：[“没有就填写无”]  
                  - 门票：[“没有就填写免费”]  
                ##路线规划
                总体的路线规划：第一个景点的名称 -> 第二个景点的名称 ->...->最后一个景点的名称
                --------具体路线规划--------
                ##详细路线
                  **景点名称** -> **景点名称**:
                  - 步行距离：[]米，约[]分钟
                  - 路线规划：具体要怎么走的导航内容
                 ##天气
                  **天气情况：（输出用户询问消息当天的天气信息）
                --------返回内容到这里结束--------
                **重要限制和说明:**
                1.严格按照上面的格式返回信息。不要添加额外的说明的解释
                2.得到了多个地点，那么按先近后远的顺序，以->来连接不同的地点位置，然后给出从第一个地点依次到最后一个地点的路线规划，一定要用->来连接不同的地点
                3.注意要返回一个总体的路线规划，从近到远，依次连接每一个景点
                """,
            mcp_servers=[Gaode_server],  # 关联MCP服务器，提供浏览器自动化能力
            hooks=Gaode_hooks,  # 添加浏览器 agent 钩子，用于监控和处理浏览器 agent 的执行过程和结果
            model=model_provider.get_model(MODEL_NAME),  # 使用我们自定义的模型提供商，确保agent使用正确的模型
            model_settings=ModelSettings(
                temperature=0.3,  # 设置温度值
                top_p=0.9,  # 设置词汇多样性
                tool_choice="auto"  # 设置工具选择策略
            )
        )
        return Gaode_agent, Gaode_server
    except Exception as e:
        print(f"创建高德 agent 时发生异常: {e}")
        await Gaode_server.cleanup()  # 确保清理MCP服务器资源，防止资源泄露和进程残留
    await Gaode_server.cleanup()


async def create_alipay_agent():
    """
    创建智能支付助手，帮助用户实现支付功能
    """
    alipay_server = MCPServerStdio(
        name="mcp-server-alipay",
        params={
            "command": "npx",
            "args": [
                "-y",
                "@alipay/mcp-server-alipay"
            ],
            "env": {
                "AP_APP_ID": f"{AP_APP_ID}",
                "AP_APP_KEY": f"{AP_APP_KEY}",
                "AP_PUB_KEY": f"{AP_PUB_KEY}"
            },
            # "disabled": False,
            # "autoApprove": []
        }
    )
    try:
        # 连接alipay MCP 服务
        print("正在连接 alipay MCP 服务...")
        await alipay_server.connect()
        print("alipay MCP 服务连接成功")

        # 获取 MCP服务可用工具列表
        tools = await alipay_server.list_tools()
        print(f"alipay MCP 服务可用工具列表{len(tools)}")
        # print(f"alipay MCP 服务的可用工具是:{tools}")
        # 创建浏览器agent
        # 配置一个专门用于打开百度地图网页的智能体，帮助我们打开百度地图
        alipay_agent = Agent(
            name="alipay",  # 代理名称，作为代理的唯一标识符
            # 详细的agent指导，指导这个agent在百度地图上进行路线检索，在项目中作为一个agent的执行策略和行为规划
            instructions="""
                  你现在是一个收费管家，但是目前你不需要收取任何费用
               """,
            mcp_servers=[alipay_server],  # 关联MCP服务器，提供浏览器自动化能力
            model=model_provider.get_model(MODEL_NAME),  # 使用我们自定义的模型提供商，确保agent使用正确的模型
            model_settings=ModelSettings(
                temperature=0.5,  # 设置温度值
                top_p=0.9,  # 设置词汇多样性
                tool_choice="auto"  # 设置工具选择策略
            )
        )
        return alipay_agent, alipay_server
    except Exception as e:
        print(f"创建alipay agent 时发生异常: {e}")
        await alipay_server.cleanup()  # 确保清理MCP服务器资源，防止资源泄露和进程残留
    await alipay_server.cleanup()


async def create_controller_agent(Gaode_agent: Agent, alipay_agent: Agent):
    """
    创建主要控制器 agent

    这个函数负责初始化配置控制器agent 包括：
    1.创建整个工作流程
    2.管理打开百度地图和在高德MCP上查询的功能
    3.确保整个系统有序的完成所有任务

    控制器代理是整个系统的核心组件，他通过工具调用和交接功能，
    将用户查询转换为一系列协调的任务，最终生成翻译好的文档，

    Arg:
        browser_agent:浏览器交互agent实例，用于打开百度地图
        Gaode_agent:旅行信息处理agent实例，用于查询关于旅行路线酒店规划的一些信息
        alipay_agent:用于支付的agent实例

    Returns:
        agent:配置好的控制器 agent实例
    """
    # 使用as_tool方法将agent转换为工具，确保直接调用
    # 当agent被转换为工具时，告诉模型这个工具的功能和用途，模型根据这个描述决定合适调用该工具
    Gaode_tool = Gaode_agent.as_tool(
        tool_name="Gaode_map",
        tool_description="根据用户想要去的地点，在高德MCP服务器上找寻答案，并且生成回答给用户"
    )
    # browser_tool = browser_agent.as_tool(
    #     tool_name="browser",
    #     tool_description="打开地图网页，提供可视化服务"
    # )
    alipay_tool = alipay_agent.as_tool(
        tool_name="alipay",
        tool_description="用于收取费用的一个智能体"
    )

    # 创建控制器 agent
    # 这是整个工作流的核心，负责协调检索和翻译过程
    controller_agent = Agent(
        name="workflow_controller",  # 代理名称
        # agent指令
        instructions="""
        你是高德地图路线检索和打开网页等的主控制器，你负责协调多个工作流程，确保从高德地图检索路线

        工作流程：
        如果是充值的问题，就把任务交给alipay_agent
        1.首先，理解用户的问题,是查询路线，还是询问酒店
        2.然后用browser_agent来进行查询
        3.将browser_agent查询到的景点交给Gaode_agent来输出
        4.如果是问关于旅行路线规划的问题，则输出关于酒店内容的规定格式；如果是问关于酒店的问题，则输出关于酒店内容的规定格式
        5.使用browser工具在高德地图上搜索并提取相关路线信息
        6.向用户报告最终结果

        重要提示：
        - 你必须完成整个流程的所有步骤
        - 不要自行处理成修改文档内容，你的工作时协调而非处理

        你的成功标准时完成整个流程，确保路线正确输出
        """,
        tools=[Gaode_tool,  alipay_tool],  # 浏览器agent作为工具提供给控制器 agent使用
        handoffs=[Gaode_agent,  alipay_agent],  # 作为交接选项提供给控制器agent
        model=model_provider.get_model(MODEL_NAME),  # 使用我们自己定义的模型提供商
        model_settings=ModelSettings(
            temperature=0.1,  # 定义非常低的温度值，使控制更加确定，减少随机性
            top_p=0.9,
            tool_choice="auto"
        )
    )
    return controller_agent


async def process_user_query(query: str):
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
    # playwright_server = None
    Gaode_server = None
    alipay_server = None
    try:
        print("========== 开始处理用户查询 ===========")

        # 创建browser
        # browser_agent, playwright_server = await create_browser_agent()
        # print("playwright MCP 创建成功")
        # 创建高德agent
        # 负责使用Gaode
        Gaode_agent, Gaode_server = await create_Gaode_agent()
        print("高德 agent 创建成功")
        # 创建alipay agent
        # 负责支付环节
        alipay_agent, alipay_server = await create_alipay_agent()
        print("alipay agent 创建成功")

        # 创建控制器agent
        # 负责协调整个工作流程，管理浏览器agent和文档处理agent作为项目中的系统调度中心
        controller_agent = await create_controller_agent(Gaode_agent, alipay_agent)
        print("控制器 agent 创建成功")

        for tool in controller_agent.tools:
            print(f"控制器 agent 的可用工具是{tool.name}:{tool.description}")

        for handoff in controller_agent.handoffs:
            tool_name = f"transfer_to_{handoff.name.lower()}"
            print(f"控制器 agent 交接代理：{tool_name} > {handoff.name}")

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
    except asyncio.CancelledError as e:
        print(f"任务被取消: {e}")
        return False
    except Exception as e:
        print(f"执行过程中出错{e}")
        traceback.print_exc()
        return False
    finally:
        # 确保所有资源都被释放
        async def cleanup_server(server, name):
            if server:
                try:
                    print(f"正在释放 {name} 资源...")
                    await asyncio.wait_for(server.cleanup(), timeout=5)
                    print(f"{name} 资源释放成功")
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    print(f"清理 {name} 时被取消或超时")
                except Exception as e:
                    print(f"清理 {name} 时出错: {e}")

        # 按顺序清理
        # await cleanup_server(playwright_server, "playwright")
        await cleanup_server(Gaode_server, "Gaode")
        await cleanup_server(alipay_server, "alipay")
