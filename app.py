!!!!前端未使用!!!!
# from flask import Flask, render_template, request
# import asyncio
# from main import process_user_query  # 假设你的核心函数在名为main的模块中，根据实际情况修改

# app = Flask(__name__)


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/process_query', methods=['POST'])
# async def process():
#     user_query = request.form.get('query')
#     if user_query:
#         try:
#             result = await process_user_query(user_query)
#             if result:
#                 return render_template('result.html', result=result)
#             else:
#                 return render_template('result.html', error="处理查询时出现错误，请重试。")
#         except Exception as e:
#             # 更详细地捕获异常，方便调试
#             print(f"执行process_user_query时出错: {e}")
#             return render_template('result.html', error="处理查询时出现错误，请重试。")
#     else:
#         return render_template('result.html', error="请输入查询内容。")


# if __name__ == '__main__':
#     # 使用uvicorn运行应用以更好支持异步
#     import uvicorn
#     uvicorn.run("app:app", host='127.0.0.1', port=5000, reload=True)
