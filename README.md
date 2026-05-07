# trino-studio

데이터 분석가가 자연어로 질문하면 SQL 생성 → 실행 → 차트까지 대화형으로 처리하는 로컬 분석 환경.

**Claude Code + Trino + DuckDB** 기반. API 서버 불필요.

## 빠른 시작

```bash
pip install -r requirements.txt
docker-compose up -d
python scripts/setup_data.py
# Claude Code에서:
/analyze 장르별 평균 평점 보여줘
```

## 스킬

| 스킬 | 설명 |
|------|------|
| `/analyze <질문>` | 자연어 → SQL → 결과 |
| `/chart <타입>` | 마지막 결과 시각화 |
| `/save <name>` | 결과를 DuckDB scratch에 저장 |
| `/schema` | 테이블·컬럼 탐색 |
| `/sync` | Trino 스키마 → catalog/schema.yaml 동기화 |

자세한 내용은 [CLAUDE.md](./CLAUDE.md) 참고.
