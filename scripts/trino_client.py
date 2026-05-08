#!/usr/bin/env python3
"""
Trino 연결을 생성하는 공통 모듈.

연결 정보 우선순위:
  host/port/http_scheme  → catalog/ontology_config.yaml
  user/password          → 환경변수 (TRINO_USER, TRINO_PASSWORD)
                           환경변수 없으면 .env 파일에서 로드

패스워드가 설정된 경우 BasicAuthentication을 사용한다.
패스워드 인증 시 trino_http_scheme을 https로 설정해야 한다.
"""
import os
from pathlib import Path

import trino
import trino.auth
import yaml
from dotenv import load_dotenv

ONTOLOGY_CONFIG_FILE = Path("catalog/ontology_config.yaml")


def _load_config() -> dict:
    if not ONTOLOGY_CONFIG_FILE.exists():
        return {}
    with open(ONTOLOGY_CONFIG_FILE) as f:
        return yaml.safe_load(f) or {}


def get_connection() -> trino.dbapi.Connection:
    load_dotenv()

    config = _load_config()

    host = config.get("trino_host", "localhost")
    port = int(config.get("trino_port", 8080))
    http_scheme = config.get("trino_http_scheme", "http")
    user = os.environ.get("TRINO_USER", "admin")
    password = os.environ.get("TRINO_PASSWORD", "")

    kwargs: dict = {
        "host": host,
        "port": port,
        "user": user,
        "http_scheme": http_scheme,
    }

    if password:
        kwargs["auth"] = trino.auth.BasicAuthentication(user, password)

    return trino.dbapi.connect(**kwargs)
