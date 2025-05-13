# web.py
import aiohttp_jinja2
import jinja2
import asyncio
from app import process_user_query
import traceback
from aiohttp import web
from datetime import datetime

async def setup_web_app():
    """初始化并配置Web应用程序

    返回值：
        web.Application: 配置完成的web应用实例，包含：
        - Jinja2模板引擎配置
        - 静态文件路由（/static）
        - 根路径路由（'/'）
        - 查询处理路由（'/process_query'）
    """
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

    # 配置静态文件路由
    app.router.add_static('/static', path='static', name='static')

    # 配置路由
    app.router.add_get('/', index)
    app.router.add_post('/process_query', handle_query)

    return app


@aiohttp_jinja2.template('index.html')
async def index(request):
    """处理根路径的GET请求

    参数：
        request: aiohttp请求对象

    返回：
        dict: 空字典用于模板渲染
    """
    return {}


async def handle_query(request):
    """处理用户查询的POST请求

    参数：
        request: 包含查询参数的请求对象

    返回：
        web.json_response: JSON格式响应，包含：
        - 成功时：格式化后的HTML内容
        - 错误时：错误信息和堆栈跟踪
        可能的状态码：
        - 200: 成功处理
        - 400: 空查询参数
        - 500: 服务器内部错误
    """
    data = await request.post()
    query = data.get('query', '').strip()

    if not query:
        return web.json_response({'error': '查询内容不能为空'})
    try:
        # 获取结构化结果
        result = await process_user_query(query)

        if not result.get('success'):
            return web.json_response({
                'error': result.get('error', '未知错误'),
                'detail': result.get('trace')
            }, status=500)

        # 增强格式化逻辑
        formatted_html = format_result(result['data'], result['type'])

        return web.json_response({'html_content': formatted_html})

    except Exception as e:
        return web.json_response({
            'error': '服务器内部错误',
            'detail': traceback.format_exc()
        }, status=500)


def format_result(raw_data, result_type):
    sections = []
    current_section = []

    # 正则表达式模式：匹配以数字+点+空格开头的行（如 "1. "、"2. " 等）
    number_pattern = re.compile(r'^\d+\.\s')

    for line in raw_data.split('\n'):
        line = line.strip()  # 去除行首行尾的空白字符

        if line.startswith('##'):
            # 处理标题行
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []
            current_section.append(f'<h3>{line.strip("# ")}</h3>')

        elif number_pattern.match(line):
            # 处理数字开头的行（如酒店名称行）
            # 提取酒店名称部分（去除数字和点）
            content = line.split('. ', 1)[1]
            current_section.append(f'<h4>{content}</h4>')

        elif line.startswith('- '):
            # 处理列表项行（如评分、类型等）
            current_section.append(f'<li>{line[2:]}</li>')

        else:
            # 处理普通段落行
            current_section.append(f'<p>{line}</p>')

    if current_section:
        sections.append('\n'.join(current_section))

    return f'''
    <div class="result {result_type}">
        {"".join(sections)}
        <div class="timestamp">{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
    </div>
    '''


async def start_web():
    """启动Web服务

    包含：
    - 应用初始化
    - TCP站点配置
    - 服务状态提示信息输出
    - 保持服务持续运行
    """
    app = await setup_web_app()
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, 'localhost', 8080)
    print("\n==========🌎小鸟地图旅行路线规划系统🌎==========\n")
    print("🌟Web服务已启动: http://localhost:8080")
    print("🌟输入你想去的地方，系统将帮你进行搜索和规划")
    #print("🌟输入 'quit' 或 'exit' 退出文档")
    print("🌟提问示例：大理古城附近的景点，并给我提供具体的步行路线规划")
    print("🌟帮我导航从昆明到哈尔滨")
    print("🌟云南大学东陆校区附近的一些酒店推荐")
    print("\n===========================================\n")
    await site.start()

    # 保持服务运行
    while True:
        await asyncio.sleep(3600)


if __name__ == '__main__':
    asyncio.run(start_web())
