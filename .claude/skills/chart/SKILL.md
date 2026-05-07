# /chart — 마지막 결과 시각화

`/analyze`가 저장한 `/tmp/last_result.json`을 읽어 차트를 생성하고 브라우저에서 연다.

## 사용법

```
/chart              # 기본 bar 차트
/chart <type>       # 타입 지정
/chart <type> <x> <y> "<title>"  # 컬럼과 제목 직접 지정
```

지원 타입: `bar` | `line` | `pie` | `scatter`

예시:
- `/chart`
- `/chart pie`
- `/chart bar genres avg_rating "장르별 평균 평점"`

## 실행 절차

### Step 1. 마지막 결과 확인

```bash
cat /tmp/last_result.json
```

파일이 없으면: "먼저 `/analyze`를 실행해 주세요." 안내 후 종료.

### Step 2. 컬럼 파악

결과 JSON의 첫 번째 레코드에서 컬럼명을 파악한다.
분석가가 x/y를 지정하지 않았으면 적절한 컬럼을 자동 선택:
- x: 문자열 또는 날짜 컬럼 우선
- y: 숫자형 컬럼 우선

### Step 3. 차트 생성

```bash
python scripts/chart.py "$(cat /tmp/last_result.json)" <type> <x> <y> "<title>"
```

### Step 4. cmux 브라우저 패널에 표시 (선택)

cmux가 사용 가능하면 브라우저 패널에 스냅샷:
```bash
cmux browser snapshot -i
```
