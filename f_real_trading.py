import pyupbit as py
import numpy as np
import pandas as pd
import requests
import e_train as params
import a_Env as env_
import ccxt
import torch
import b_network as NET
import c_PPO_Agent as PPO_Agent
import torch.nn.functional as F
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import time
import random
import torch
from binance.client import Client
from datetime import datetime, timedelta
import pandas as pd


seed=1
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)

if params.device=='cuda':
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


env=env_.Env()
params.real_or_train='real'

if params.trading_site =='binance':
    API_key =params.Binance_API_key
    Secret_key =params.Binance_Secret_key

if params.trading_site =='upbit':
    API_key = params.Upbit_API_key
    Secret_key = params.Upbit_Secret_key


def real_save_price_data(data,ind_data,data_name):
    data_name = data_name.replace('/', '_')
    data = [pd.Series(data[step],name='data').reset_index()['data'] for step in range(len(data))]

    data_ = pd.DataFrame(data[:-1])
    date = pd.DataFrame(data[-1])
    data_minute = pd.DataFrame([params.minute])

    date_name_ = str('save_real_date_'+data_name)
    data_name_ = str('save_real_price_'+data_name)
    minute_name = 'minute_data'

    date.to_csv(date_name_,index=False)
    data_.to_csv(data_name_,index=False)
    torch.save(ind_data,'save_real_ind_'+data_name)
    data_minute.to_csv(minute_name,index=False)




def real_load_price_data(data_name,real_data_count):  #불러온 데이터를 csv로 저장하고 동일한 날짜인경우 불러올때 csv를 호출함으로써 시간 절약
    res = 0
    data = 0
    data_name = data_name.replace('/', '_')
    ind_data_ = [0, 0, 0]

    try:
        csv_data=pd.read_csv('save_real_date_'+data_name).values
        ind_data = torch.load('save_real_ind_'+data_name)
        past_minute =pd.read_csv('minute_data').values[0][0] #과거 분봉

        if params.minute == past_minute and real_data_count[1] == csv_data[-1][0][:16]:
            res='csv'
            csv_data_ = pd.read_csv('save_real_price_'+data_name).values

            data = [pd.Series(csv_data_[step]) for step in range(len(csv_data_))]
            data.append(pd.Series(csv_data.reshape(-1))) # 날짜 추가
            ind_data_ = [pd.Series(ind_data[step]) for step in range(len(ind_data))]
        else :
            #API와 저장된 데이터의 불러올 날짜가 다르면 새로 API 호출
            print('불러온 데이터의 마지막 날짜:',csv_data[-1][0][:16],'         불러온 최근 시간:',real_data_count[1])
            res='API'


    except Exception as e:  # 예외 유형을 Exception으로 지정
        print('저장된 데이터 파일이 없습니다. 새로운 API 호출 실시')
        print(f'오류 메시지: {e}')  # 오류 메시지 출력
        res = 'API'

    return res,data,ind_data_






# 레버리지 설정과 바이낸스 설정


class MyBinance(ccxt.binance):
    def nonce(self):
        return self.milliseconds() - self.options['timeDifference']




# api 실시간 데이터 불러와서 거래한다(DB가 하나이므로 학습 데이터는 날짜로 뽑고, 최근 구간은 data_count만큼 뽑는다)





####################코인 트레이딩 일봉단위 의사결정
class Coin_Env():
    def __init__(self):

        self.Global_policy_net={}
        self.Global_value_net={}
        self.agent_data={}
        self.agent=0
        self.decide_action=0

        self.myToken = params.Slack_token
        self.API_key = params.Binance_API_key
        self.Secret_key= params.Binance_Secret_key

        self.client = Client(self.API_key, self.Secret_key)
        self.client.futures_change_leverage(symbol=params.API_data_name.replace('/',''), leverage=params.leverage)

        self.position_info = self.client.futures_position_information(symbol=params.API_data_name.replace('/',''))
        for position in self.position_info:
            if position['symbol'] == params.API_data_name.replace('/',''):
                leverage = position['leverage']
                print(leverage,'설정 레버리지')

        self.binance = ccxt.binance({
            'enableRateLimit': True,  # 데이터 속도제한
            'apiKey': self.API_key,
            'secret': self.Secret_key,
            'timeout': 3000,  # milliseconds
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True,
            },
        }
        )

        self.is_back_testing = True
        self.symbol_name = params.API_data_name
        self.ori_symbol_name = params.API_coin_name


        # long short 2개 생성
        self.PV_data = {'long': [], 'short': []}
        self.action_data = {'long': [], 'short': []}
        self.buy_data = {'long': [], 'short': []}  # 매수한 가격
        self.sell_data = {'long': [], 'short': []}  # 매도한 가격
        self.buy_date = {'long': [], 'short': []}
        self.sell_date = {'long': [], 'short': []}
        self.price_data = {'long': [], 'short': []}  # 가격 데이터
        self.date_data = {'long': [], 'short': []}  # 날짜 데이터
        self.scale_input = {'long': [], 'short': []}

        self.main_ind_state = 'init'
        self.agent_data = {}
        self.past_data_date = 0


    def message(self, token, channel, text):  # slack에 메세지를 보낸다
        response = requests.post("https://slack.com/api/chat.postMessage",
                                 headers={"Authorization": "Bearer " + token},
                                 data={"channel": channel, "text": text}
                                 )

    def time_(self):  # 현시각 출력
        fseconds = time.time()
        second = int(fseconds % 60)
        fseconds //= 60
        minute = fseconds % 60
        fseconds //= 60
        hour = fseconds % 24
        hour = (hour + 9) % 24

        return hour, minute, second











    def act(self, action, unit,real_data_count,short_or_long):  # 매매
        # 매매 포지션을 유지하고 오더된 유닛을 초과하지 않도록 설정
        hour,minute,second= self.time_()
        self.action = action
        self.unit = unit


        if action == 0:  # 매도
            # unit 조절 (풀매수로 설정돼있기 때문에 조정)
            unit_ = round(unit[0], 5)
            if unit_ > self.agent.stock:
                unit_ = self.agent.stock - 0.0001

            if unit_ > 0:
                self.action_data[is_short_or_long].append(0)
                self.order = client.futures_create_order(
                            symbol=self.symbol_name.replace('/',''),
                            side='SELL',
                            type='market',
                            quantity=unit_,
                            newClientOrderId=new_client_order_id
                        )

                self.message(self.myToken, "#future-trading", '시장가 매도 완료')
                self.message(self.myToken, "#future-trading", self.unit[0] * self.price)

            else:
                print('매도 , 유닛수부족으로 패스')

        elif action == 1:  # 관망
            pass
            # self.action_data[is_short_or_long].append(1)

        else:  # 매수
            # unit 조절 (풀매수로 설정돼있기 때문에 조정)
            unit_ = round(unit[2], 3)

            print('매수')
            print(unit[2])

            if unit_ > 0:
                self.action_data[is_short_or_long].append(2)
                self.order = client.futures_create_order(
                            symbol=self.symbol_name.replace('/',''),
                            side='BUY',
                            type='market',
                            quantity=unit_,
                            newClientOrderId=new_client_order_id
                        )

                self.message(self.myToken, "#stock-trading", '시장가 매수 완료')
                self.message(self.myToken, "#stock-trading", self.unit[2] * self.price)

            else:
                print('매수, 유닛수 부족으로 패스')

        # 데이터 저장
        # self.PV_data[is_short_or_long].append(self.agent.PV)

        if real_data_count[1] != self.past_data_date:  # 분봉 시간이 바꼈을때

            print('현시각:', hour, '시', minute, '분', second, '초')

            if action == 0:
                print('진입 분봉 시간:', real_data_count[1], '      행동: 매도', '진입 갯수:', unit[0], '진입 가격:', self.agent.price)

            if action == 2:
                print('진입 분봉 시간:', real_data_count[1], '      행동: 매수', '진입 갯수:', unit[2], '진입 가격:', self.agent.price)

            if short_or_long == 'short':
                print('------------------------------------------------------------------------------------------------------------------------------------------')
                print('종목명:', self.symbol_name, '           현재액션:', action, '       종목매수 가치(달러) : ',float(self.agent.price) * self.agent.short_unit, '       포트폴리오 가치(달러) : ', self.agent.PV, '    현재가(달러):',
                      float(self.agent.price), '   평단가:', 'None', '    보유수량:', self.agent.short_unit)
                print('------------------------------------------------------------------------------------------------------------------------------------------')

            if short_or_long == 'long':
                print('------------------------------------------------------------------------------------------------------------------------------------------')
                print('종목명:', self.symbol_name, '           현재액션:', action, '       종목매수 가치(달러) : ',float(self.agent.price) * self.agent.long_unit, '       포트폴리오 가치(달러) : ', self.agent.PV, '    현재가(달러):',
                      float(self.agent.price), '   평단가:', 'None', '    보유수량:', self.agent.long_unit)
                print('------------------------------------------------------------------------------------------------------------------------------------------')


            self.past_data_date = real_data_count[1]






    def recent_period(self,is_First): #최신데이터를 적절한 구간만큼 minute 고려하여 불러온다
        real_trading_data_num = 1000  # 새로출력시 불러올 데이터 갯수(새로운 분인경우)

        ##############현재 최신 데이터 시간 불러오기
        time.sleep(1) #많은호출 방지

        for i in range(20):  # 최대 20번 재시도
            try:
                self.binance = ccxt.binance({
                    'enableRateLimit': True,  # 데이터 속도제한
                    'apiKey': API_key,
                    'secret': Secret_key,
                    'timeout': 3000,  # milliseconds
                    'options': {
                        'defaultType': 'future',
                        'adjustForTimeDifference': True,
                    },
                }
                )

                ohlcv = self.binance.fetch_ohlcv(self.symbol_name, '1m', limit=10)  # 1분 봉 데이터를 가져옴
                break  # 데이터를 성공적으로 가져오면 for 루프를 빠져나옴

            except ccxt.NetworkError:  # 네트워크 오류가 발생하면
                if i < 19:  # 19번 이하로 시도했다면
                    time.sleep(2)
                    print(i+1,'번 재시도')
                    continue  # 다시

                else:  # 10번이 모두 실패했다면
                    raise  # 오류를 던짐

        latest_ohlcv = ohlcv[-1]  # 가장 최근의 봉 데이터를 선택
        open_time = latest_ohlcv[0] / 1000  # 밀리초를 초로 변환
        open_time = datetime.fromtimestamp(open_time).strftime('%Y-%m-%d %H:%M')  # 해당 종목의 최근 가격 시간

        if is_First==False:
            #########이전에 저장된 최신데이터 불러오기

            try:  #과거 저장됐던 데이터 호출
                csv_data = pd.read_csv('save_real_date_' + self.symbol_name.replace('/','_')).values
                ori_last_minute = csv_data[-1][0][:16] #저장된 데이터의 마지막 시각
            except:
                pass

            ########### minute 만큼 시간이 지났는지 확인
            time1 = datetime.strptime(open_time, '%Y-%m-%d %H:%M')
            time2 = datetime.strptime(ori_last_minute, '%Y-%m-%d %H:%M')
            time_diff = time1-time2
            time_minute = int(time_diff.total_seconds()/60)

            if round(time_minute / params.minute) < real_trading_data_num : # 뽑게될 데이터 갯수가 적으면 데이터를 더뽑음
                last_minute = datetime.strptime(ori_last_minute, '%Y-%m-%d %H:%M') - timedelta(minutes=params.minute * real_trading_data_num)  # 데이터 1000개만큼 출력되도록 시작점 설정
                last_minute = str(last_minute)[:16]
                time2 = datetime.strptime(last_minute, '%Y-%m-%d %H:%M')
                time_diff = time1 - time2
                time_minute = int(time_diff.total_seconds() / 60)


            ########## 백테스트 마지막 ~ 최신 데이터 호출 구간
            if time_minute%params.minute==0: # minute 만큼 시간이 지났을경우 새로운 데이터 호출
                is_API = 'API'
                real_data_count = [last_minute, open_time]
            else:
                is_API = 'csv'
                real_data_count = [last_minute, ori_last_minute]

            '''''
            print(round(time_minute / params.minute))
            print(time2, 'csv 의 마지막 시간')
            print(time_diff, '시간차이')
            print(open_time, '실시간')
            print(last_minute, '불러올 초기시간')
            print(time_minute, '지나온시간')
            print(is_API, 'API냐 csv냐')
            print(real_data_count,'불러오는 시간')
            '''''

        if is_First==True: #csv도 없는 첫상태, 초기 트레이딩 시작일때
            is_API='API'
            real_data_count = [params.data_count[0],open_time]  #종목의 최근까지 호출

        return real_data_count, is_API





    def start_trading(self):
        # 학습했던 구간의 데이터를 불러온다
        env = env_.Env()
        is_First=True #처음인경우
        real_data_count, is_API_ = self.recent_period(is_First)  #처음 뽑으면 API 최신까지 호출
        print(real_data_count,'원시 데이터 호출 날짜 기간')

        data_ = env.coin_data_create(params.minute, real_data_count, params.real_or_train, params.coin_or_stock,
                                     params.point_value,self.symbol_name)  # 학습시 뽑은 history 데이터

        long_input_, short_input_, ori_ind_data= env.input_create(params.minute, params.ratio,real_data_count,
                                                               params.coin_or_stock, params.point_value,
                                                               params.short_ind_name, params.long_ind_name,
                                                               data_)  # ind에서 높은 값을 뽑음
        ind_data = [long_input_,short_input_,ori_ind_data]
        real_save_price_data(data_,ind_data, self.symbol_name)

        long_maxmin = [[np.max(long_data), np.min(long_data)] for long_data in ori_ind_data[0]]  # 학습구간 데이터의 지표 max 와 min 값
        short_maxmin = [[np.max(short_data), np.min(short_data)] for short_data in ori_ind_data[1]]


        #############################실시간 데이터 호출
        while True:  # 실시간 호출 및 액션
            # 재 접속 시도
            for step in range(100):
                try:
                    self.binance = MyBinance({
                        'enableRateLimit': True,  # 데이터 속도제한
                        'apiKey': API_key,
                        'secret': Secret_key,
                        'timeout': 300000,  # milliseconds
                        'options': {
                            'defaultType': 'future',
                            'adjustForTimeDifference': True,
                        },
                    })

                    self.ohlcv = self.binance.fetch_ohlcv(self.symbol_name, '1m', limit=5)  # 1분 봉 데이터를 가져옴
                    self.client = Client(API_key, Secret_key)
                    break

                except Exception as e:
                    print(e)
                    print('재접속 시도', step, '번째')

            is_First = False
            real_data_count, is_API_ = self.recent_period(is_First)  # 처음 뽑으면(= is First : True) API 최신까지 호출

            is_API, data_, ind_data = real_load_price_data(self.symbol_name, real_data_count)  # csv를 불러올지, api를 불러올지 선택
            long_input_ = ind_data[0]
            short_input_ = ind_data[1]
            ori_ind_data = ind_data[2]

            # 데이터 불러옴
            if is_API == 'API':
                data_ = env.coin_data_create(params.minute, real_data_count, params.real_or_train, params.coin_or_stock,
                                             params.point_value, self.symbol_name)  # 학습시 뽑은 history 데이터

                long_input_, short_input_, ori_ind_data = env.input_create(params.minute, params.ratio, real_data_count,
                                                                           params.coin_or_stock, params.point_value,
                                                                           params.short_ind_name, params.long_ind_name,
                                                                           data_)  # ind에서 높은 값을 뽑음
            ind_data = [long_input_, short_input_, ori_ind_data]
            real_save_price_data(data_, ind_data, self.symbol_name)

            long_train_data, long_val_data, long_test_data, long_ori_close, long_total_input, long_date_data, long_total_date = long_input_
            short_train_data, short_val_data, short_test_data, short_ori_close, short_total_input, short_date_data, short_total_date = short_input_

            self.long_price_data = torch.cat([long_ori_close[0], long_ori_close[1], long_ori_close[2]])  # 실시간 가격., 지표 데이터들
            self.long_scale_input = long_total_input
            self.long_date_data = long_total_date

            self.short_price_data = torch.cat([short_ori_close[0], short_ori_close[1], short_ori_close[2]])
            self.short_scale_input = short_total_input
            self.short_date_data = short_total_date

            long_real_ori = ori_ind_data[0]
            short_real_ori = ori_ind_data[1]

            long_res_data = [] #결과 최신 지표 데이터 저장할곳
            short_res_data = []

            for index, max_min in enumerate(long_maxmin):  # 과거의 최대, 최소값 real에 추가
                res_data = []
                for step in range(len(long_real_ori[index])):
                    try:
                        res = np.array(long_real_ori[index].iloc[step])
                    except:
                        res = np.array(long_real_ori[index][step])

                    res = np.insert(res, 0, np.array(max_min))
                    scaler = MinMaxScaler([0.1, 1])
                    res = scaler.fit_transform(res.reshape(-1, 1))
                    res_data.append(res[-1])
                long_res_data.append(torch.Tensor([res_data]).view(-1))

            for index, max_min in enumerate(short_maxmin):  # 과거의 최대, 최소값 real에 추가
                res_data = []
                for step in range(len(short_real_ori[index])):
                    try:
                        res = np.array(short_real_ori[index].iloc[step])
                    except:
                        res = np.array(short_real_ori[index][step])

                    res = np.insert(res, 0, np.array(max_min))
                    scaler = MinMaxScaler([0.1, 1])
                    res = scaler.fit_transform(res.reshape(-1, 1))
                    res_data.append(res[-1])
                short_res_data.append(torch.Tensor([res_data]).view(-1))


            ##########################에이전트 호출
            for short_or_long in params.short_or_long_data:  # 롱숏 에이전트 호출
                # global net
                Global_actor = NET.Global_actor
                Global_critic = NET.Global_critic


                window= params.window[short_or_long]
                input_dim = len(params.short_ind_name)

                self.Global_policy_net[short_or_long] = Global_actor('cpu', window, input_dim, short_or_long,params.Neural_net, params.bidirectional_)
                self.Global_value_net[short_or_long] = Global_critic('cpu', window, input_dim, short_or_long,params.Neural_net, params.bidirectional_)


                # 숏 or 롱 포지션 따라 인풋 정의
                if short_or_long == 'short':
                    input_ = short_res_data
                    self.input_dim = params.input_dim['short']
                    ori_close = self.short_price_data
                    date_data = self.short_date_data

                else:
                    input_ = long_res_data
                    self.input_dim = params.input_dim['long']
                    ori_close = self.long_price_data
                    date_data = self.long_date_data

                agent_num = 0  # 글로벌 에이전트 넘버=0

                self.agent_data[short_or_long] = PPO_Agent.PPO(window,  # LSTM 윈도우 사이즈
                                                               params.cash,  # 초기 보유현금
                                                               params.cost,  # 수수료 %
                                                               params.device,  # 디바이스 cpu or gpu
                                                               params.k_epoch,  # K번 반복
                                                               input_,  # 인풋 데이터
                                                               ori_close,  # 주가 데이터
                                                               date_data,  # 날짜 데이터
                                                               self.input_dim,  # feature 수
                                                               agent_num,
                                                               params.coin_or_stock,
                                                               params.deposit,
                                                               params.backtest_slippage,
                                                               short_or_long,  # 숏인지 롱인지
                                                               self.Global_policy_net[short_or_long],  # 글로벌넷
                                                               self.Global_value_net[short_or_long],  # 글로벌넷
                                                               self.is_back_testing
                                                               )

                self.agent = self.agent_data[short_or_long]  # 에이전트 정의
                self.policy_net = self.Global_policy_net[short_or_long] #폴리시 정의
                balance = self.binance.fetch_balance(params={'type' : 'future'})

                if short_or_long =='short':
                    self.decide_action = self.agent.short_decide_action
                    self.discrete_step = env.short_discrete_step
                    self.agent.short_ori_input = ori_ind_data[1]
                    self.agent.price_data = self.short_price_data  # 가격 데이터

                    pos = balance['info']['positions']  #숏 매수 물량
                    for position in pos:
                        if position['symbol'] == self.symbol_name.replace('/', ''):
                            short_unit = float(position['positionAmt']) #숏매수는 음수로 표시됨
                            if short_unit < 0 :
                                self.agent.short_unit = np.abs(short_unit) #숏매수는 음수로 표시됨
                            else:
                                self.agent.short_unit = 0
                            break

                if short_or_long =='long':
                    self.decide_action = self.agent.long_decide_action
                    self.discrete_step = env.long_discrete_step
                    self.agent.long_ori_input = ori_ind_data[0]
                    self.agent.price_data = self.long_price_data  # 가격 데이터

                    pos = balance['info']['positions']  # 롱 매수 물량
                    for position in pos:
                        if position['symbol'] == self.symbol_name.replace('/', ''):
                            long_unit = float(position['positionAmt'])
                            if long_unit < 0 :
                                self.agent.long_unit = 0  # 숏매수는 음수로 표시됨
                            else:
                                self.agent.long_unit = np.abs(long_unit)
                            break

                #상태 API 업데이트
                latest_ohlcv = self.ohlcv[-1]  # 가장 최근의 봉 데이터를 선택
                self.data_price = latest_ohlcv[1]   #시장의 x분봉 open 가격
                self.agent.price = self.agent.price_data[-1] #분봉 계산된 가격
                self.agent.cash= balance['USDT']['free']



                ##저장된 가중치 load
                self.policy_net.load()

                #policy 계산
                with torch.no_grad():
                    prob = self.policy_net(self.agent.LSTM_input).to(self.agent.device)
                    policy = F.softmax(prob, dim=1)  # policy

                self.agent.price = self.agent.price_data[-1]  # 현재(최근) 주가업데이트
                self.agent.back_testing = True

                #액션 설정
                action, unit= self.decide_action(policy[-1],deposit=1)
                step = len(self.agent.PV_list)-1
                action, reward, step_ = self.discrete_step(action, unit, step, self.agent)  # PV및 cash, stock 업데이트

                # 매매
                unit[0]=0
                self.act(action, unit,real_data_count,short_or_long) #real_data_count = 최근 기간 문자열

                if real_data_count[1] != self.past_data_date:
                    print(short_res_data[0][-40:],'fkasgggggggggggggggggggggggnfks')

            time.sleep(1)




if __name__ == '__main__':
    coin_env = Coin_Env()
    coin_env.start_trading()
