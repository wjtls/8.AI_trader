# AI_trader


설명 <br><br>
 AI를 사용한 알고리즘 트레이딩 (해외선물, 주식, 코인 현물, 마진 모두가능) <br>
 커스텀 지표를 참고하여 트레이딩 환경에서 다수 에이전트가 비동기적 학습하고 <br>
 학습완료된 글로벌 에이전트가 백테스트, 전진분석, 실전투자를 실행 <br>

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
  
</p>
<br>
  <figure> 
    <img src="https://github.com/wjtls/AI_trader/assets/60399060/c08a7041-1f53-413c-9ed0-1d9ede409aaf" width="600"/>
    <figcaption>실전매매 로그</figcaption>
  </figure>
  
<br>
- AI 마진 트레이딩 
- 종목 : 코인 ETH (201분봉) <br>
- 기간 : 2022-01-01 00:00 ~ 2024-03-05 23:41 <br>
- 사용지표 : 커스텀 지표 5개 (추세지표 2개 , 휩소포착 역추세지표 2개, 단기 추세 1개)<br>
- 설정 : 레버리지 1배, 슬리피지 3달러, 수수료 0.2% (본래 수수료 0.04%) <br>
- 시장수익률 : 31.5399169921875 % 
- AI 수익률 : 454.03662109375 % 
