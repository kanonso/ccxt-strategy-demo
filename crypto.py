import requests,time,json,configparser,requests
from datetime import datetime
import pandas as pd
import time as tme

config = configparser.ConfigParser()

def bb(okx,symbol = 'BTC—USDT-SWAP',factor=3, window = 144):
    ohlcv = okx.fetch_ohlcv(symbol,'5m',limit=300)
    klines =pd.DataFrame(ohlcv,columns = ['Date', 'Open','High','Low','Close','Volume'])
    klines['time'] = pd.to_datetime(klines['Date'],unit='ms')
    klines.set_index('time', inplace=True)
    klines['ma'] = klines['Close'].rolling(window).mean()
    klines['std'] = klines['Close'].rolling(window).std()
    klines['upper'] = klines['ma'] + factor * klines['std']
    klines['lower'] = klines['ma'] - factor * klines['std']
    klines['signal'] = klines.apply(lambda x: 1 if x['Close'] < x['lower']
                    else (-1 if x['Close'] > x['upper'] else 0),
                    axis=1)
    return klines

def tg_html(symbol='ETHFI-USDT-SWAP',action='close',side='long',lvg = 10,
            PnL=0,last=0,PnL_ratio=0,price=3,pos=1):
    sendMsgText = f"""
    <b>{symbol} {action} </b>
    <blockquote>
    Side: {side}
    OrderPrice: {price}
    Pos: {pos}
    last: {last}
    Leverage: {lvg}
    PnL: {PnL:.4f}u  {PnL_ratio:.2f}%    
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </blockquote>
    """
    return sendMsgText     

def send_html(tg_token,tg_chat_id,sendMsgText):
    url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    data = {
        "chat_id": tg_chat_id,
        "text": sendMsgText,
        "parse_mode": "HTML"  # Using HTML formatting
    }    
    response = requests.post(url, data=data)
    return response


class orders_positions(object):    
    def __init__(self,exch,symbol='UXLINK-USDT-SWAP',lvg = 10):   
        self.symbol = symbol
        self.exch = exch
        self.params = {'marginMode': 'isolated'}
        self.message = ''
        self.lvg = lvg
        self.now = datetime.now()
        self.now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def get_open_order(self, open_orders):
        if open_orders:
            for item in open_orders:
                if item['info']['instId'] == self.symbol:
                    self.open_order = item
                    break
            else:
                self.open_order = {}
        else:
            self.open_order = {}

        if self.open_order: 
            self.open_side = self.open_order['side']
            self.ordId = self.open_order['info']['ordId']
            self.order_time = datetime.fromtimestamp(self.open_order['timestamp']/1000 )

    def get_position(self,positions):   
        if positions:
            for item in positions:
                if item['info']['instId'] == self.symbol:
                    self.position = item   
                    break
                else:
                    self.position = {}
        else:
            self.position ={}
        if self.position:
            # instId = position['info']['instId']
            self.uplRatio = self.position['info']['uplRatio']
            self.side = self.position['side'] # 方向
            self.pos = abs(float(self.position['info']['pos'])) # holding position
            self.entryPrice = self.position['entryPrice'] # entry price
            self.realizedPnl = self.position['realizedPnl'] # realized Profit & Loss
            self.unrealizedPnl = self.position['unrealizedPnl']# unrealized Profit & Loss
            self.upnl_ratio = self.position['percentage']# percentage # PnL percentage%
            self.hold_time = datetime.fromtimestamp(self.position['timestamp']/1000 )
            self.hold_seconds = (datetime.now() - self.hold_time).seconds
            try:
                self.last = self.exch.fetch_ticker(self.symbol)['close']        
            except:
                tme.sleep(3)
                self.last = self.exch.fetch_ticker(self.symbol)['close'] 

    def stop_pnl(self,profit = 10,loss = -10,minute=30,sig = 0):
        self.message ,self.response= '',''
        if (not self.open_order) :
            if (self.side == 'long'): # first line
                if (self.upnl_ratio > profit):
                    self.message = f'{self.symbol} {self.pos} Long positon stop profit {self.unrealizedPnl:.2f}u {self.upnl_ratio:.2f}% {round(self.last * 1.001,6)} {self.now_str}'
                    self.response = self.exch.createLimitSellOrder(self.symbol,abs(self.pos),self.last * 1.001, params=self.params)

                elif (self.upnl_ratio < loss):
                    self.message = f'{self.symbol} {self.pos} Long position with market stop-loss {self.unrealizedPnl:.2f}u {self.upnl_ratio:.2f}% {round(self.last * 1.001,6)} {self.now_str}'
                    # response = self.exch.createLimitSellOrder(self.symbol,abs(self.pos),self.last * 1.001,params=self.params)
                    self.response = self.exch.createMarketSellOrder(self.symbol,abs(self.pos),params = self.params)
                
            elif (self.side == 'short') :
                if (self.upnl_ratio > profit) :
                    self.message=f'{self.symbol} {self.pos} short position stop profit {self.unrealizedPnl:.2f}u {self.upnl_ratio:.2f}% {round(self.last*0.999,6)} {self.now_str}'
                    self.response = self.exch.createLimitBuyOrder(self.symbol,abs(self.pos),self.last * 0.999,params=self.params)

                elif (self.upnl_ratio < loss):
                    self.message=f'{self.symbol} {self.pos} Short position with market stop-loss {self.unrealizedPnl:.2f}u {self.upnl_ratio:.2f}% {round(self.last*0.999,6)} {self.now_str}'
                    self.response = self.exch.createMarketBuyOrder(self.symbol,abs(self.pos),params = self.params)       

        if self.message != '':
            print("=================  crypto ================")
            print(self.message)
        return self.message,self.response          
                   
    def send_init_msg(self,target_pool,k):
        try:
            info = self.client.futures_account()
        except Exception as e:
            time.sleep(60)
            print(f'{e} {self.now}')
            info = self.client.futures_account()
        positions = pd.DataFrame(info["positions"])
        for col in positions.columns:
            positions[col] = positions[col].astype(float, errors='ignore')
        unrealizedProfit = positions['unrealizedProfit'].sum()  
        self.mkd_msg=f''' 
            #### ** Strategy Ver **<font color=\"comment\">**{self.ver} **</font>        
            #### ** Setting！**<font color=\"comment\">**{len(target_pool)} targets**</font> \n
                    > testnet：<font color=\"warning\">{self.testnet} </font>     
                    > target_pool：<font color=\"warning\">{target_pool} </font>                           
                    > wallet：<font color=\"warning\">{self.usdt} usdt</font>  
                    > availale：<font color=\"warning\">{self.availableBalance} usdt</font>                      
                    > Total UnrealizedProfit：<font color=\"warning\">{unrealizedProfit} usdt</font>                     
                    > ma interval：<font color=\"warning\">{self.interval}m </font>    
                    > ma_period：<font color=\"warning\">{self.ma_period}</font>   
                    > haircut：<font color=\"warning\">{self.haircut}</font>  
                    > leverage：<font color=\"warning\">{self.lvg}</font>   
                    > single shot：<font color=\"warning\">{self.shot}</font>                       
                    > stop loss chg rate：<font color=\"warning\">{round((float(self.stop_loss_chg_rate))*100,1)} %</font>  
                    > stop proit chge thr：<font color=\"warning\">{(self.stop_profit_chg_rate)*100} %</font>  
                    > ip：<font color=\"comment\">{self.local_ip}</font> 
                    > dt：<font color=\"comment\">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</font>    
                    > k：<font color=\"comment\">{k}</font>                                               
            '''
        self.send_work_markdown()

    def send_work_markdown(self):        
        mkd={
            "msgtype": "markdown",
            "markdown": {
                "content": self.mkd_msg
                }
            }   
        body = json.dumps(mkd)
        res = requests.post(self.bot_url,data=body)
        return res.text, res.status_code

    def position_markdown(self,k):
        info = self.client.futures_account()
        positions = pd.DataFrame(info["positions"])
        for col in positions.columns:
            positions[col] = positions[col].astype(float, errors='ignore')
        positions = positions[positions['positionAmt'] != 0 ]
        for i in range(len(positions)):
            position = positions[i:i+1].reset_index()
            symbol = position['symbol'][0]
            self.mkd_msg=f''' 
            #### ** Holding！**<font color=\"warning\">**{position['symbol'][0]}**</font> \n
                        > wallet：<font color=\"warning\">{self.usdt} usdt</font>  
                        > quantity：<font color=\"warning\">{position['positionAmt'][0]}</font>                     
                        > cost/last：<font color=\"info\">{position['breakEvenPrice'][0]} / {self.get_lastPrice(symbol)}</font> 
                        > PnL：<font color=\"info\">{position['unrealizedProfit'][0]} / {round((position.unrealizedProfit.iat[0]/position.initialMargin.iat[0]) * 100,2)}% </font>                                                   
                        > count：<font color=\"comment\">{k}</font>                                
                        > dt：<font color=\"comment\">{datetime.now()}</font>                            
                '''           
            self.send_work_markdown()
            
    def action_markdown(self,**kwargs):         
        self.mkd_msg=f''' 
        #### ** {kwargs['name']}！**<font color=\"warning\">**{kwargs['target_code']}**</font> \n                              
                    > **signal:{kwargs['signal']}**
                    > **move:{kwargs['move']}**       
                    > **KMA:{kwargs['kma']}**   
                    > **SMA:{kwargs['sma']}** 
                    > **LMA:{kwargs['lma']}**                          
                    > **BS ratio:{kwargs['BS_ratio']}**   
                    > **stragegy:{kwargs['strategy']}**                                                   
                    > side：<font color=\"warning\">{kwargs['side']}</font>                                           
                    > price/quantity：<font color=\"info\">{kwargs['p']} / {kwargs['q']}</font> 
                    > PnL：<font color=\"info\">{kwargs['PnL']} usdt/ {kwargs['PnL_rate']:.2f}%</font>                        
                    > orderno：<font color=\"comment\">{kwargs['orderno']}</font> 
                    > status：<font color=\"comment\">{kwargs['order_status']}</font>                      
                    > updateTime：<font color=\"comment\">{kwargs['t']}</font>       
                    > noticeTime：<font color=\"comment\">{datetime.now()}</font>       
                    > loop count：<font color=\"comment\">{kwargs['k']}</font>                        
                    > ip：<font color=\"comment\">{self.local_ip}</font>                       
            ''' 