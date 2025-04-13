# 项目介绍
演示如何使用 CCxt，完成一个完整的加密货币程序化交易python代码。**不构成投资建议**
本项目是展示程序化交易需要完成的各项决策流程，包括登入交易所、查询持仓、计算指标、下单、查询未成交订单、撤单、查询成交回报。
由于不同交易所对于不同 国家/地区有使用限制，项目使用 okx 交易所作为范例。

*   仅量化交易者供学习之用，不作为任何投资建议
*   范例使用 [okx交易所]([https://](https://www.okx.com/join/EZQUANT888)) 的模拟交易API
*   策略为多支加密货币永续合约的布林通道策略 

# 学习重点
本项目是帮助量化交易的初学者，认识如何建构一套完整的python量化交易策略。学习重点包括：
*   建构完整的量化策略决策流程：删单、止盈止损、新仓进场
*   练习使用 github
*   如何在本地或是云服务器(github codespace)部署运行加密货币量化交易策略
*   如何开通加密货币交易所账号，并申请 API
*   如何开发一套完整的python项目

# 运行步骤
运行本项目代码，请遵循以下步骤
1.   开通加密货币交易所账号以及API(模拟交易/真实交易)
2.   config.ini填写 api_key 以及 Telegram BOT
3.   调整 RunStrategy.py 以下的策略设定

############ strategy config ############   
lvg,shot,haircut,cancel_time = 10, 5,0.01,5
* lvg：永续合约杠杆倍数
* shot：单笔金额
* haircut：买卖加减幅度
* cancel_time:未成交删单时长(分钟)

threshold = shot * 2
* threshold：下单前可以余额为下单margin金额的两倍

target_pool = ['BTC-USDT-SWAP','DOGE-USDT-SWAP','ETH-USDT-SWAP',
               'SOL-USDT-SWAP','EOS-USDT-SWAP','XRP-USDT-SWAP']
* 监控池
  
telegram_on = 0
* 关闭 TG 机器人通知，如果已经设定好 TG机器人，可更改设定为 telegram_on = 1

params= {'hedged': False, 'tdMode': 'isolated', 'leverage': lvg} 
*单向模式、逐仓、杠杆倍数
######### end of strategy config #########   


# [关于ccxt]([https://](https://github.com/ccxt/ccxt))
ccxt全称是 CryptoCurrency eXchange Trading Library。ccxt整合了一百多家加密货币交易所的行情接口与交易接口，使用者可以透过ccxt快速实现加密货币的程序化交易。运行前行先安装 ccxt
pip install ccxt
