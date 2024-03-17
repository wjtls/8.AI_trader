# AI_trader


대상 : 코인 (현물, 마진) 

 <br>
 <br>
  <br>

주요 구성 <br>
1. Asynchronous PPO 알고리즘 및 학습
2. AI 백테스트 환경
3. 실전 트레이딩(Binance API 사용)
4. 마진시 롱숏 분리
5. 매매 slack 메세지 전송


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
 
  <figure> 
    ![image](https://github.com/wjtls/AI_trader/assets/60399060/c08a7041-1f53-413c-9ed0-1d9ede409aaf)
    <figcaption>실전매매 로그</figcaption>
  </figure>

</p>
<br>
- 코인 ETH 선물 백테스팅 (201분봉) <br>
- 2022-01-01 00:00 ~ 2024-03-05 23:41 <br>
- 31.5399169921875 % : 시장 수익률<br>
- 454.03662109375 % : AI 수익률<br>
