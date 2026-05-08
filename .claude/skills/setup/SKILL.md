# /setup — 분석 환경 초기화

분석 세션을 시작하기 전에 venv 확인, Trino 기동, 샘플 데이터 로드를 한 번에 처리한다.
**처음 실행 시에만** venv를 생성하고 패키지를 설치한다.

## 실행 절차

### Step 1. Python venv 확인 및 설정

```bash
ls venv/bin/python3
```

**venv가 없는 경우 (최초 1회):**

```bash
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
```

**venv가 이미 있는 경우:**

패키지가 최신인지 확인한다:
```bash
venv/bin/pip install -r requirements.txt --quiet
```

---

### Step 2. Trino 기동

```bash
docker-compose up -d
```

Trino가 준비될 때까지 기다린다 (최대 60초):
```bash
until curl -sf http://localhost:8080/v1/info | venv/bin/python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('starting')==False else 1)" 2>/dev/null; do
  echo "Trino 기동 중..."; sleep 5
done
echo "Trino 준비 완료"
```

---

### Step 3. 샘플 데이터 로드

memory connector는 재시작 시 초기화되므로 매번 로드한다:
```bash
venv/bin/python3 scripts/setup_data.py
```

---

## 완료 메시지

설정 완료 후 사용 가능한 스킬을 안내한다:

```
분석 환경 준비 완료!

사용 가능한 스킬:
  /schema             — 테이블·컬럼 탐색
  /sync               — 카탈로그를 Trino 스키마와 동기화
  /analyze <질문>     — 자연어로 데이터 분석
  /chart <타입>       — 마지막 결과를 차트로 시각화
  /save <name>        — 결과를 DuckDB에 저장
  /dashboard          — 저장된 결과로 HTML 대시보드 생성
```
