# OCG Roguelike — 개발 설계 초안

일본 OCG 최초 발매일이 **2012-03-31 이하인 카드**로, 개발 시점의 현행 OCG 규칙·최신 효과를 사용하는 비상업적 싱글플레이 로그라이크 듀얼 게임.

현재는 설계와 카드 지원 상태 검증 도구만 있다. 듀얼 엔진, 게임 화면, 실제 카드 목록, AI는 아직 구현하지 않았다. 실제로 검증된 카드는 0장이다.

- [엔진 검토·아키텍처·최소 개발 범위](docs/design.md)
- [카드 데이터와 지원 판정 계약](docs/card-data.md)
- [조사 출처와 확인 범위](docs/research.md)

개발 보조 도구는 Python 3.12 표준 라이브러리만 사용한다. 게임의 플랫폼·UI 스택을 확정하는 선택은 아니다.

```sh
cd /workspace/yu-gi-oh
python3 -m unittest discover -s tests -v
python3 tools/audit_catalog.py data/catalog.json
```

두 번째 명령은 현재 빈 카탈로그에 대해 종료 코드 2를 반환한다. 이를 게임 준비 완료나 테스트 통과로 해석하지 않는다. 테스트의 가상 카드·URL·해시는 판정 로직을 검증하는 픽스처이며 실제 카드 근거가 아니다.
