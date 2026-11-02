# 카드 판정 데이터 계약 v1

`data/catalog.json`은 실제 카드가 들어갈 빈 카탈로그다. `tools/audit_catalog.py`는 입력 형식과 **기록된 검증 상태**를 검사한다. URL을 방문하거나 증거의 진위·테스트 실행 여부를 검증하지 않는다. 검토자가 공식 근거와 실행 결과를 확인한 뒤 상태를 올려야 한다. 플레이 가능 여부의 최종 판정에는 별도의 덱/금제 검증이 추가로 필요하다.

## 서로 독립적인 상태

| 축 | 상태 | 의미 |
| --- | --- | --- |
| `eligibility.status` | `pending`, `verified`, `excluded` | 일본 최초 발매 근거 미확인 / 검증 완료 / 제외 |
| `implementation.status` | `unimplemented`, `candidate`, `verified`, `blocked` | 없음 / 스크립트 후보 확보 / 현재 묶음에서 효과 검증 / 오류·재정 충돌 |
| 금제 | 별도 프로필 | 해당 덱에 투입 가능한 장수. 위 두 축을 바꾸지 않음 |

자격이 있어도 구현이 없으면 보상에 나오지 않는다. 스크립트가 있어도 최초 발매일이 늦으면 제외한다. 일반 몬스터처럼 개별 Lua 파일이 필요 없는 카드도 엔진 데이터와 동작 검증을 거쳐야 한다. 스크립트 파일의 유무만으로 상태를 계산하지 않는다.

## 레코드 형태

아래 필드는 `verified`를 주장할 때 필요하다. 미확인 값은 `null` 또는 필드 생략으로 남길 수 있으나 사용 승인은 나지 않는다. 날짜는 ISO `YYYY-MM-DD`, 해시는 SHA-256 소문자 64자리다.

```text
catalog
  schema_version: 1
  cutoff: "2012-03-31"  # 고정
  snapshot:
    id: 비어 있지 않은 실행 묶음 식별자
    rules_verified_at: 실제 공식 규칙 확인일
    rules_source_url: 확인한 공식 문서 URL
    engine_sha256: core 아티팩트 해시
    scripts_sha256: 카드 스크립트 + 공용 헬퍼 묶음 해시
    card_data_sha256: 엔진 DB 해시
  cards: [
    card_id: 공식 DB cid 등으로 만든 고유 식별자
    name_ja: 일본어 카드명
    eligibility:
      status: pending | verified | excluded
      territory: "JP-OCG"
      first_release_date: 최초 발매일
      evidence_url: 공식 DB 또는 공식 상품/프로모 근거
      verified_at: 최초 발매 검증일
    text:
      status: pending | verified
      source_url: 일본어 공식 DB 개별 카드 URL
      verified_at: 최신 텍스트/에라타 확인일
      sha256: 정규화한 일본어 텍스트 해시
    implementation:
      status: unimplemented | candidate | verified | blocked
      snapshot_id: 검증한 실행 묶음
      text_sha256: 구현과 대조한 공식 텍스트 해시
      tests: [{id: 고유 시나리오 ID, result: passed}]
  ]
```

증거 URL과 날짜만으로 '최초' 발매를 증명할 수는 없다. 본 데이터 수집 단계에서는 상품 ID·종류(부스터/스트럭처/프로모/서적/게임 등)·발매 지역·발매일·출처·접근일을 별도 `release_evidence` 이력으로 보존한다. 검토자가 일본 OCG 수록 이력의 최솟값과 프로모 배포 기록을 대조해 위 요약 값을 승인한다. TCG 선행 발매를 일본 발매로 취급하지 않는다. 토큰·별칭·동일 카드의 다른 패스코드·구버전 효과 ID는 실제 카드 정체성과 엔진 코드의 매핑 테이블로 구분한다.

실제 도입 시 추가할 자료: 룰 옵션 값과 근거, 재정 URL별 확인일/관련 테스트 ID, 원본 커밋, 카드별 스크립트 의존성, 테스트 산출물 해시, 금제 정책, 표시 언어. 현재 도구는 이 전체 자료를 검증하는 완성된 콘텐츠 파이프라인이 아니다.

선택 가능한 집합은 `자격 검증 ∩ 최신 텍스트 검증 ∩ 현재 실행 묶음에서 효과 검증`으로 만든다. 이후 각 기능이 금제·덱 구성 조건을 적용한다. 테스트 한 개가 통과했다는 사실만으로 모든 효과가 검증되지는 않는다. `implementation.status=verified`는 모든 적용 효과와 필요한 상호작용을 검토했다는 담당자의 승인 상태다.

실행 묶음이나 텍스트 해시가 바뀌면 기존 승인을 재사용하지 않는다. 현재 도구는 ID/해시 불일치를 보류한다. 런 시작 후에는 전체 묶음을 고정한다.

CLI 종료 코드: 0 = 한 장 이상 지원 조건 충족 및 전체 레코드 충족, 1 = 보류/제외 레코드 또는 미검증 스냅샷, 2 = 형식 오류/빈 목록. 제외·미지원 카드를 포함하는 전체 연구용 카탈로그에서 코드 1은 정상적인 감사 결과일 수 있다. 출력의 카드별 사유로 구분한다.
