# 即使慢，驰而不息，纵令落后，纵令失败，但一定可以达到他所向往的目标。               —— 鲁迅


# 🤝建议🤝
我们渴望得到您的建议，如果您有任何想法，请发送邮件到 pengyugaoynu@stu.ynu.edu.cn,我们随时等待您的建议！
# 如何使用
下载 Node.js，URL：https://nodejs.org/en

火山模型 deepseek-v3 配置 URL: https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement?LLM=%7B%7D&OpenTokenDrawer=false

高德地图：https://console.amap.com/dev/key/app.      创建一个应用，绑定服务为web端的，此时会有Key 和 安全密钥，这两个根据注释填入index前端页面，仔细找一下

AP_APP_ID 是支付宝的应用 ID，AP_APP_KEY 是支付宝的私钥， AP_PUB_KEY 是支付宝的公钥，这三个参数不配置也不影响使用。

API_KEY 是大模型的 API_KEY , BASE_URL 是大模型的固定 URL，MPDEL_NAME 是选用的模型名称， Gao_De_API 和高德 MCP 中的 AMAP_MAPS_API_KEY 是高德地图创建应用时提供的 Key

运行在web.py生成的前端网页，本地电脑接口 8080 中使用

~~~
pip install playwright
~~~

配置API，

### MCP sever configuration
##Playwright-MCP
~~~json
{
    "mcpServers": {
        "playwright": {
            "command": "npx",
            "args": [
                "-y",
                "@playwright/mcp@latest"
            ]
        }
    }
}
~~~
##Gaode-MCP
~~~json
{
    "mcpServers": {
        "amap-maps": {
            "command": "npx",
            "args": [
                "-y",
                "@amap/amap-maps-mcp-server"
            ]
            "env": {
                "AMAP_MAPS_API_KEY": "你的高德Key"
            }
        }
    }
}
~~~
##Alipay-MCP
~~~json
{
    "mcpServers": {
        "mcp-server-alipay": {
            "command": "npx",
            "args": [
                "-y",
                "@alipay/mcp-server-alipay"
            ]
            "env": {
                "AP_APP_ID": "你的支付宝应用ID",
                "AP_APP_KEY": "你的私有钥匙",
                "AP_PUB_KEY": "你的公有钥匙"
            },
        }
    }
}
~~~

注意：npx是运行环境，必须下载node.js，不然会报错！配置的时候，如果MCP是需要密钥的，就要注意配置"env",没有密钥的，"env"就是空，配置MCP的关键参数："args":的第二个参数"@alipay/mcp-server-alipay",这是MCP的地址。
# 🌎小鸟地图🌎
这是一个**旅行助手**，它能帮助您规划旅行路线、酒店推荐等与旅行相关的操作，类似的，你可以询问它**从昆明到北京的路线**，或者**云南大学东陆校区
附近的景点推荐，并给我一些步行的路线规划**，不用担心**天气**问题，它会一并输出。
# 主体框架图
![项目流程图](https://github.com/user-attachments/assets/5a17c42e-6328-411a-a5e6-924eb152e3d4)
# 旅游询问框架图
![具体流程图](https://github.com/user-attachments/assets/68f0d5fd-98ea-4252-b699-b5e1c9374f00)

# 使用说明 #
需要创建一个.env文件来保存自己的接口信息，里面的参数包括:
- API_KEY = "Your_API_KEY"
- BASE_URL = "Your_Model_BASE_URL"
- MODEL_NAME = “deep_seek-v3"
- Gao_De_API = "Gaode_MCP_API"
- AMAP_MAPS_API_KEY = "Gaode_MCP_API"
- AP_APP_ID = "alipay_APP"
- AP_APP_KEY = "alipay_KEY"
- AP_PUB_KEY= "alipay_Public_KEY"

配置好参数后就可以使用了
一些运行截图：
![image](https://github.com/user-attachments/assets/e836c875-9734-4003-af52-14ae421a61ad)
![image](https://github.com/user-attachments/assets/cb7a8066-a9e9-404f-87f9-f7953dcf9902)
![image](https://github.com/user-attachments/assets/6e126d23-70c8-4335-a277-f8d35c7a5eb5)
![image](https://github.com/user-attachments/assets/9c332b86-b01d-4ef5-80fc-ee19bfa21247)
<img width="1182" alt="54dd09c257aa21ac0bd61329ba0f6a4" src="https://github.com/user-attachments/assets/0759c18d-3114-46ce-ad97-1bafd73df4d6" />





优化：前端的美观程度，以及上下文的记忆能力，而不是单纯的只是输出结果
## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Heisenberg-Gao/TravelBird&type=Date)](https://www.star-history.com/#Heisenberg-Gao/TravelBird&Date)
