# 项目介绍

本项目演示如何使用 [CCXT](https://github.com/ccxt/ccxt) 完成一个完整的加密货币程序化交易 Python 代码。**<mark>本项目仅供学习参考，不构成任何投资建议</mark>。**

项目展示了程序化交易中常见的各项流程，包括：
- 登录交易所
- 查询持仓
- 计算指标
- 下单
- 查询未成交订单
- 撤单
- 查询成交回报  

> ⚠️ 注意：由于不同交易所对不同国家/地区可能存在使用限制，本项目使用 **OKX 交易所** 的模拟交易 API 作为范例。

### 特点

- 可模拟、实盘的python量化交易代码。示范如何编写一个**完整的python量化交易策略**
- 示例使用 [OKX 交易所](https://www.okx.com/join/EZQUANT888) 模拟交易 API
- 策略为多支加密货币永续合约的 **布林通道策略**

---

# 学习重点

本项目目的在帮助量化交易初学者理解并构建一套完整的 Python 量化交易策略，学习重点包括：

- 构建完整的量化策略决策流程：删单、止盈止损、新仓进场 
- 熟悉 GitHub 的使用
- 学会在本地或云服务器（如 GitHub Codespace）上部署运行量化策略
- 学习开通交易所账号，并申请 API 接口权限
- 掌握完整 Python 项目的开发与结构 

---

# 运行步骤

请依照以下步骤运行本项目代码：
1. 开通加密货币交易所账号，并申请 API（可选择模拟交易或真实交易）
2. 在 `config.ini` 文件中填写 `api_key` 及 Telegram Bot 配置 
3. 根据你的策略需求，编辑 `RunStrategy.py` 中的配置参数
4. 运行安装依赖包 pip install ccxt
5. 修改 okx交易所API的IP白名单

---

## 策略参数说明

请搜寻`RunStrategy.py` 以下的代码块，并根据需求修改。交易参数说明：

############ strategy config ############

1. lvg, shot, haircut, cancel_time = 10, 5, 0.01, 5
   
  - lvg：永续合约杠杆倍数 
  - shot：单笔金额  
  - haircut：买卖加减幅度  
  - cancel_time:未成交删单时长(分钟)
    

2. threshold = shot * 2

    下单最低余额：下单前可以余额为下单margin金额的两倍
   

4. target_pool = ['BTC-USDT-SWAP','DOGE-USDT-SWAP','ETH-USDT-SWAP','SOL-USDT-SWAP','EOS-USDT-SWAP','XRP-USDT-SWAP']

    监控池：初始设定同时监控6支永续合约代码
   

4. telegram_on = 0

    初始关闭 TG 机器人通知避免报错。如果已经设定好 TG机器人，可更改设定为 telegram_on = 1


5. params= {'hedged': False, 'tdMode': 'isolated', 'leverage': lvg}

    交易参数：单向模式、逐仓、杠杆倍数 
    以上参数需要在 okx 交易界面另外同步设定

[![Watch the video](https://img.youtube.com/vi/f4HzLUZ4CZY/maxresdefault.jpg)](https://youtu.be/f4HzLUZ4CZY)
### [Watch this video on YouTube](https://youtu.be/f4HzLUZ4CZY)

