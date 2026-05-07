# /setup — 분석 환경 초기화

분석 세션을 시작하기 전에 Trino 기동, 샘플 데이터 로드, cmux 레이아웃 설정을 한 번에 처리한다.

## 실행 절차

### Step 1. Trino 기동

```bash
docker-compose up -d
```

Trino가 준비될 때까지 기다린다 (최대 60초):
```bash
until curl -sf http://localhost:8080/v1/info | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('starting')==False else 1)" 2>/dev/null; do
  echo "Trino 기동 중..."; sleep 5
done
echo "Trino 준비 완료"
```

### Step 2. 샘플 데이터 로드

memory connector는 재시작 시 초기화되므로 매번 로드한다:
```bash
python scripts/setup_data.py
```

### Step 3. cmux 레이아웃 설정

```bash
# 오른쪽 패널: 쿼리 결과
cmux new-split right

# 오른쪽 하단 패널: 차트 브라우저 (필요 시)
cmux new-split down
```

## 완료 메시지

설정 완료 후 사용 가능한 스킬을 안내한다:

```
분석 환경 준비 완료!

사용 가능한 스킬:
  /schema          — 테이블·컬럼 탐색
  /sync            — 카탈로그를 Trino 스키마와 동기화
  /analyze <질문>  — 자연어로 데이터 분석
  /chart <타입>    — 마지막 결과를 차트로 시각화
```
