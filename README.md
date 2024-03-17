# AI_trader


대상 : 코인 (선물, 현물) 

 <br>
 <br>
  <br>

주요 구성 <br>
1. Asynchronous PPO 알고리즘 및 학습
2. AI 백테스트 환경
3. 실전 트레이딩(Binance API 사용)
4. 매매 slack 메세지 전송


 <br>
 <br>
 <br>
 
기타 기능
1. 'future'로 설정시 선물 트레이딩
2. 'coin'으로 설정시 현물 트레이딩
3. 백테스팅에서 이전과 같은 날짜 호출시 빠른호출
4. 분봉 커스텀 호출,다른날짜 호출시 분봉 일치
5. 지표 리페인트 방지
6. 슬리피지 설정, 수수료 설정
7. 레버리지 설정

<br>
<br>
<br>

참고 이미지  <br>
<p>
  <img src="https://github.com/wjtls/AI_trader/assets/60399060/80e3b619-78df-4d7a-b865-cc7d210e623f" width="300"/>
  <img src="https://github.com/wjtls/AI_trader/assets/60399060/80e3b619-78df-4d7a-b865-cc7d210e623f" width="300"/>
</p>
<br>
- 코인 ETH 선물 백테스팅 (201분봉) <br>
- 2022-01-01 00:00 ~ 2024-03-05 23:41 <br>
- 31.5399169921875 % : 시장 수익률<br>
- 454.03662109375 % : AI 수익률<br>
