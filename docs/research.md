# 조사 기록

조사일: **2026-11-02 (Asia/Seoul)**. 아래는 엔진 자료를 읽은 날짜다. 공식 OCG 규칙·카드 효과를 확인한 날짜로 사용하지 않는다. 브랜치 URL은 변경 가능하므로 실제 도입 시 커밋을 고정해야 한다.

| 자료 | 직접 확인한 내용 |
| --- | --- |
| [ocgcore README](https://github.com/edo9300/ygopro-core/blob/master/README.md) | 독립 빌드, C++17, premake5, Lua, C API, AGPL |
| [ocgcore API 헤더](https://github.com/edo9300/ygopro-core/blob/master/ocgapi.h) | 생성·처리·메시지·응답·조회 API. 일부 인자의 포인터 여부가 README와 다름 |
| [core LICENSE](https://github.com/edo9300/ygopro-core/blob/master/LICENSE) | AGPL-3.0-or-later 표기 |
| [EDOPro README](https://github.com/edo9300/edopro/blob/master/README.md) | core·CardScripts·BabelCdb·WindBot 연결 관계, 타 계열과의 비호환 주의 |
| [CardScripts README](https://github.com/ProjectIgnis/CardScripts/blob/master/README.md) | Lua 카드 구현, 공용 헬퍼, pre-errata 및 비공식 카드 존재, 단순 구문 검사의 한계 |
| [WindBot Ignite README](https://github.com/ProjectIgnis/windbot/blob/master/README.md) | EDOPro 방 프로토콜, 덱별 executor, C#/Mono 계열 구성 |

[공식 카드 DB](https://www.db.yugioh-card.com/yugiohdb/) 접근 시 이 환경의 프록시가 `403 Forbidden`을 반환했다. 따라서 공식 카드 목록, 최초 발매일, 최신 텍스트·재정, 현행 금제는 미검증이다. 필요한 네트워크 허용 대상은 우선 `www.db.yugioh-card.com`이며 공식 규칙 문서의 실제 링크를 따라갈 때 추가 호스트가 필요할 수 있다. 현재 환경 설정을 변경하지는 않았다.

BabelCdb는 엔진용 데이터 후보로만 확인했다. 그 데이터의 정확성·발매 이력·최신성은 검증하지 않았다. 공식 DB의 대체 판정 근거로 사용하지 않는다. 공식 DB에 프로모 등의 최초 배포 근거가 충분하지 않으면 공식 상품·프로모 공지 등의 보조 자료를 기록하고, 결론이 불명확하면 보류한다.
