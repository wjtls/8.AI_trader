# 8.AI_trader
개인 사용 AI 트레이더
AI를 사용한 알고리즘 트레이딩 (해외선물, 주식, 코인 현물, 마진 모두가능) <br> <br>

설명 <br><br>
 커스텀 지표 또는 사용자가 지정한 데이터를 참고하여 트레이딩 환경에서 다수 에이전트가 비동기적 학습하고 <br>
 학습완료된 글로벌 에이전트가 백테스트, 전진분석, 실전투자를 실행 <br><br>

 각 에이전트는 매수, 매도, 관망, 매매수량 등을 설정하고 트레이딩 환경과 상호작용하여<br>
 보상점수(포트폴리오 가치)를 극대화하는 방향으로 AI 스스로 행동과 전략을 최적화 한다.

 <br>
 <br>
  <br>

주요 구성 <br>
1. 비동기 강화학습 알고리즘 및 학습
2. 커스텀 지표 사용
3. AI 백테스트 환경
4. 실전 트레이딩(Binance API 사용)
5. 마진시 롱숏 분리
6. 매매 slack 메세지 전송
 <br>
특이사항  <br>
- API key 비공개 
- github 등록시 지표 데이터 함수 비공개 

 <br>
 <br>
 <br>
 
기타 기능
1. 'future'로 설정시 마진 트레이딩
2. 'coin'으로 설정시 현물 트레이딩
3. 백테스팅에서 이전과 같은 날짜 호출시 빠른호출
4. 분봉 커스텀 호출, 실전에서 호출시에도 백테스트때와 분봉 일치 기능
5. 지표 리페인트 방지
6. 슬리피지 설정, 수수료 설정
7. 레버리지 설정

<br>
<br>
<br>
기반 알고리즘 <br>
1.(https://github.com/wjtls/5.AI_Trader.....Risk_management_Readme) <br>
2.https://github.com/wjtls/4.AI_Ensemble_trader.....SOTA-RL
<br>
<br>
<br>

참고 이미지  <br>
<p>
  <figure> 
    <img src="https://github.com/wjtls/AI_trader/assets/60399060/80e3b619-78df-4d7a-b865-cc7d210e623f" alt='참고' width="300"/>
    <figcaption>백테스트</figcaption>
  </figure>
 
  <figure> 
    <img src="https://github.com/wjtls/AI_trader/assets/60399060/c4322ad6-4ac5-445b-a7b5-95e6c4955294" width="300"/>
    <figcaption>백테스트 로그</figcaption>
  </figure>
  
</p>
<br>
  <figure> 
    <img src="https://github.com/wjtls/AI_trader/assets/60399060/c08a7041-1f53-413c-9ed0-1d9ede409aaf" width="600"/>
    <figcaption>실전매매 로그</figcaption>
  </figure>
  
<br>
- AI 선물 트레이딩 <br>
- 종목 : 코인 ETH (201분봉) <br>
- 기간 : 2022-01-01 00:00 ~ 2024-03-05 23:41 <br>
- 사용지표 : 커스텀 지표 5개 (추세지표 2개 , 휩소포착 역추세지표 2개, 단기 추세 1개)<br>
- 설정 : 레버리지 1배, 슬리피지 3달러, 수수료 0.2% (본래 수수료 0.04%) <br>
- 시장수익률 : 31.5399169921875 % 
- AI 수익률 : 454.03662109375 % 

<br>
<br>
<br>
실거래 3개월 PV +22.06%
<br>

<figure>
  <img src="https://github.com/wjtls/8.AI_trader/assets/60399060/d54b9054-8ebf-43af-ae02-450228668873" width="300" height='300'/>
  <figcaption>실전매매 로그</figcaption>
</figure>
