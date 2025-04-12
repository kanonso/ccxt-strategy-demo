import ccxt,crypto,requests
from datetime import datetime
import time as tme
import pandas as pd
import ccxt,configparser
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['testnet']['api_key']
api_secret = config['testnet']['api_secret']
password = config['testnet']['password']
tg_token = config['telegram']['tg_token']
tg_chat_id = config['telegram']['chat_id']
okx = ccxt.okx({
    'apiKey': api_key ,
    'secret': api_secret,
    'password': password,
    'options': {
        'adjustForTimeDifference': True,
        'defaultType': 'future',
    },
})
okx.set_sandbox_mode(True)

lvg,shot,haircut,cancel_time,k = 10, 5,0.01,5,0
threshold = shot * 2
sendMsgText = ''

params= {'hedged': False, 'tdMode': 'isolated', 'leverage': lvg} 

# balance  = pd.DataFrame(okx.fetch_balance()['info']['data'][0]['details'])
# availBal = float(balance[balance['ccy'] == 'USDT']['availBal'].iloc[0])
target_pool = ['BTC-USDT-SWAP','DOGE-USDT-SWAP','ETH-USDT-SWAP',
               'SOL-USDT-SWAP','EOS-USDT-SWAP','XRP-USDT-SWAP']

contracts = {}
for symbol in target_pool:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    okx.load_markets()
    market = okx.market(symbol)
    contract = {'contractSize' : round(market['contractSize'],8),
                'minSz' : float(okx.market(symbol)['info']['minSz'])}
    contracts.update({symbol:contract})

while True:
    open_orders = okx.fetch_open_orders()
    positions = okx.fetch_positions()
    for symbol in target_pool:
        holding = crypto.orders_positions(okx,symbol,lvg = lvg)
        holding.get_open_order(open_orders)
        holding.get_position(positions)
        kbars = crypto.bb(okx,symbol)
        signal = kbars.signal.iloc[-1]
        contractSize = contracts[symbol]['contractSize']
        minSz = contracts[symbol]['minSz']
        ticker = okx.fetch_ticker(symbol)
        last = ticker['close']
        pos = round(round((lvg * shot) /( last * contractSize * minSz )) * minSz,8)
        # order_price = round(last * (1 - haircut),6)
        if holding.open_order:
            if (
                (((datetime.now() - holding.order_time).seconds)> cancel_time * 60 ) or
                ((holding.open_order['side']=='sell') & (signal >0) ) or 
                ((holding.open_order['side']=='buy') & (signal <0))                     
            ):
                try:
                    response = okx.cancel_order(holding.ordId,symbol)
                    if (((datetime.now() - holding.order_time).seconds)> cancel_time * 60 ):
                        sendMsgText = f"{k} time out cancel order {symbol} {now_str}"
                    else:
                        sendMsgText = f"{k} reverse signal cancel order {symbol} signal：{signal} {now_str}"
                    url = f'https://api.telegram.org/bot{tg_token}/sendMessage?chat_id={tg_chat_id}&text={sendMsgText}'
                    response = requests.post(url)      
                    print(sendMsgText)
                    tme.sleep(1)
                    continue
                except Exception as e:
                    print(f"{k} {symbol} {holding.ordId,symbol} {datetime.now()}")
                    print(e)
        if holding.position:
            if k%501 == 1:
                print(f"{k} {holding.symbol} {holding.side} {holding.pos} unrealized PnL:{holding.unrealizedPnl:.2f}u {holding.upnl_ratio:.2f}% signal:{signal} {now_str}")

            if k % 2001 ==1:
                ticker = okx.fetch_ticker(symbol)
                last = ticker['close']
                sendMsgText = crypto.tg_html(symbol=symbol,action='holding',side=holding.position['side'],
                                                lvg=holding.position['leverage'],price=holding.position['entryPrice'],
                                                pos=holding.pos,last=last,PnL=holding.unrealizedPnl,PnL_ratio=holding.upnl_ratio )
                response = crypto.send_html(tg_token,tg_chat_id,sendMsgText)      
                if not response:  
                    tme.sleep(2)
                    response = crypto.send_html(tg_token,tg_chat_id,sendMsgText) 

            if not holding.open_order:
                message = ''
                try:
                    holding.stop_pnl(profit = lvg*1 ,loss = -(lvg*0.7), minute = 5 ,sig=signal)
                    message ,order_response = holding.message,holding.response
                except Exception as e:
                    print(f" {k} {symbol} line111 {e} {datetime.now()}")
                if message != '':
                    tme.sleep(1)
                    try:
                        order = okx.fetch_open_orders(symbol)[0]       
                        if not order:
                            amount = holding.pos *  okx.market(symbol)['contractSize']
                            side = order_response['side']
                            price = holding.last
                        else:    
                            amount = order['amount'] *  okx.market(symbol)['contractSize']   
                            side = order['side']
                            price = order['price']    
                        if holding.unrealizedPnl <0:
                            act = "close loss"
                        else:
                            act = "close profit"
                        sendMsgText = crypto.tg_html(symbol=symbol,action= act,side=side,lvg=lvg,price=price,pos=amount,
                                                        last=last,PnL=holding.unrealizedPnl,PnL_ratio=holding.upnl_ratio )
                        response = crypto.send_html(tg_token,tg_chat_id,sendMsgText) 
                    except Exception as e:
                        print(f"{k} {symbol} line132 error {e} {datetime.now()}")
                        continue         

            if (not holding.position ) & ( not holding.open_order) & (signal != 0) :
                response_flag = 0
                while response_flag == 0:
                    try:
                        balance = okx.fetch_balance()['free']['USDT']
                        response_flag = 1
                    except:
                        tme.sleep(2)
                        balance = okx.fetch_balance()['free']['USDT']
                print(f"signal:{symbol} signal:{signal} bal:{balance:.4f} {now_str}")                    
                if balance >threshold:
                    ticker = okx.fetch_ticker(symbol)
                    last = ticker['close']
                    pos = round(round((lvg * shot) /( last * contractSize * minSz )) * minSz,8)

                    order_response = None                              
                    if (signal >0):
                        order_price = round(last * (1 - haircut),6)
                        order_response = okx.createLimitSellOrder(symbol,abs(pos),order_price, params= params) 
                        print(f"{k} {symbol} signal:{signal} last:{last} ma1:{round(kbars['ma'].iat[-1],4)} ma7:{round(kbars['ma'].iat[-7],4)} {last<kbars['ma'].iat[-1]} {datetime.now()}")

                    elif (signal <0) :
                        order_response = okx.createLimitSellOrder(symbol,abs(pos),order_price, params= params)   
                        print(f"{k} {symbol} signal:{signal} last:{last} ma1:{round(kbars['ma'].iat[-1],4)} ma7:{round(kbars['ma'].iat[-7],4)} {last>kbars['ma'].iat[-1]} {datetime.now()}")

                    if order_response:
                        sendMsgText = crypto.tg_html(symbol=symbol,action='new',side=order_response['side'],lvg=lvg,
                                                        price=order_price,last=last,pos=pos)

                        response = crypto.send_html(tg_token,tg_chat_id,sendMsgText) 
                        print(sendMsgText)   
    k += 1     