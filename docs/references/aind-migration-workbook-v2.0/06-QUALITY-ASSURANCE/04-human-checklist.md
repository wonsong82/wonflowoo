# Human Critical Checklist

**Version**: 1.0.0
**Last Updated**: 2026-01-16

---

## Overview

이 문서는 각 Stage Gate에서 Human이 반드시 확인해야 할 핵심 항목을 정의합니다.
AI가 처리한 결과를 맹목적으로 신뢰하지 말고, 아래 체크리스트로 검증하세요.

> **원칙**: 재작업을 방지하는 가장 효과적인 방법은 조기 발견입니다.

---

## Stage 1: Discovery Gate

### Critical Checklist (10개 미만)

```yaml
stage1_gate:
  verification_command: "/s1-04-discovery-spec-generation 실행 후 summary 확인"

  critical_items:
    1_controller_coverage:
      question: "모든 Controller가 식별되었는가?"
      check_method: |
        # Legacy 소스에서 Controller 수 직접 확인
        find hallain/ -name "*Controller.java" | wc -l
        # Feature Inventory의 Controller 수와 비교
        grep -c "controller:" work/specs/stage1-outputs/phase1/feature-inventory.yaml
      failure_impact: "Stage 2에서 누락 발견 → Stage 1 Phase 3-4 재작업"
      acceptable_gap: "0 (100% 일치 필수)"

    2_endpoint_count:
      question: "Endpoint 수가 정확한가?"
      check_method: |
        # 실제 @RequestMapping 수
        grep -r "@RequestMapping\|@GetMapping\|@PostMapping" hallain/ --include="*.java" | wc -l
        # Inventory 기록 수
        grep -c "endpoint:" work/specs/stage1-outputs/phase1/feature-inventory.yaml
      failure_impact: "누락된 Endpoint는 마이그레이션되지 않음"
      acceptable_gap: "< 2%"

    3_sp_identification:
      question: "SP(Stored Procedure) 호출이 모두 식별되었는가?"
      check_method: |
        # Legacy에서 SP 호출 패턴 확인
        grep -r "{call\|CALL " hallain/ --include="*.xml" | wc -l
        # Spec에서 SP 호출 수
        grep -r "stored_procedure:" work/specs/stage1-outputs/phase4/ | wc -l
      failure_impact: "SP 누락 → Stage 4 코드 생성 실패"
      acceptable_gap: "0 (100% 일치 필수)"

    4_dynamic_sql_assessment:
      question: "Dynamic SQL 복잡도가 평가되었는가?"
      check_method: |
        # 동적 SQL 태그 수
        grep -r "<if>\|<choose>\|<foreach>" hallain/ --include="*.xml" | wc -l
        # 복잡도 분류 확인
        grep -c "complexity: HIGH" work/specs/stage1-outputs/phase4/**/*.yaml
      failure_impact: "복잡도 과소평가 → Stage 4 변환 실패율 급증"

    5_domain_boundary:
      question: "도메인 경계가 명확히 식별되었는가?"
      check_method: |
        # 도메인별 Feature 수 균형 확인
        cat work/specs/stage1-outputs/phase1/feature-inventory.yaml | grep "domain:" | sort | uniq -c
      failure_impact: "경계 불명확 → 순환 의존성 문제"
```

### Verification Commands

```bash
# 1. Feature Inventory 요약 확인
cat work/specs/stage1-outputs/phase1/summary.yaml

# 2. 도메인별 분포 확인
grep "domain:" work/specs/stage1-outputs/phase1/feature-inventory.yaml | sort | uniq -c

# 3. SP 호출 Feature 목록
grep -l "stored_procedure:" work/specs/stage1-outputs/phase4/**/*.yaml

# 4. HIGH 복잡도 Feature 수
find work/specs/stage1-outputs/phase4 -name "*.yaml" -exec grep -l "complexity: HIGH" {} \; | wc -l
```

---

## Stage 2: Validation Gate

### Critical Checklist

```yaml
stage2_gate:
  verification_command: "/s2-04-validation-spec-completion 실행 후 coverage 확인"

  critical_items:
    1_coverage_percentage:
      question: "Coverage가 99% 이상인가?"
      check_method: |
        # comparison-report에서 coverage 확인
        grep "coverage:" work/specs/stage2-outputs/phase2/comparison-report.yaml
      failure_impact: "Coverage < 99% → Stage 4에서 누락 Feature 발생"
      acceptable_value: ">= 99%"

    2_gap_remediation:
      question: "모든 Gap이 해결되었는가?"
      check_method: |
        # 미해결 Gap 수
        grep -c "status: unresolved" work/specs/stage2-outputs/phase3/gap-analysis.yaml
      failure_impact: "미해결 Gap → 마이그레이션 누락"
      acceptable_value: "0"

    3_bidirectional_match:
      question: "Forward와 Backward가 일치하는가?"
      check_method: |
        # Stage 1 Feature 수
        S1_COUNT=$(grep -c "feature_id:" work/specs/stage1-outputs/phase1/feature-inventory.yaml)
        # Stage 2 Source Inventory 수
        S2_COUNT=$(grep -c "feature_id:" work/specs/stage2-outputs/phase1/source-inventory.yaml)
        echo "S1: $S1_COUNT, S2: $S2_COUNT"
      failure_impact: "불일치 → 일부 Feature 누락"
```

---

## Stage 3: Preparation Gate

### Critical Checklist

```yaml
stage3_gate:
  verification_command: "Stage 3 Phase 5 완료 확인"

  critical_items:
    1_circular_dependency:
      question: "순환 의존성이 해결되었는가?"
      check_method: |
        # dependency-graph에서 circular 확인
        grep -c "circular: true" work/specs/stage3-outputs/phase1/dependency-graph.yaml
      failure_impact: "순환 의존성 → Stage 4 빌드 실패"
      acceptable_value: "0"

    2_naming_convention:
      question: "Naming Convention이 ADR로 확정되었는가?"
      check_method: |
        # ADR 파일 존재 확인
        ls work/specs/stage3-outputs/phase4/adr/
      failure_impact: "미확정 → Stage 4 코드 생성 후 전체 rename 필요"

    3_interface_definition:
      question: "Cross-domain Interface가 정의되었는가?"
      check_method: |
        # interface 정의 수
        grep -c "interface:" work/specs/stage3-outputs/phase2/interfaces.yaml
      failure_impact: "미정의 → 도메인 간 통합 실패"

    4_architecture_approval:
      question: "아키텍처 설계가 Human 승인되었는가?"
      check_method: |
        # 승인 기록 확인
        grep "approved_by:" work/specs/stage3-outputs/phase4/architecture-design.yaml
      failure_impact: "미승인 → Stage 4 진행 불가"
```

---

## Stage 4: Generation Gate

### Critical Checklist

```yaml
stage4_gate:
  verification_command: "Stage 4 Phase 5 빌드 성공 확인"

  critical_items:
    1_mini_pilot_success:
      question: "Mini-Pilot 6개 Feature가 검증되었는가?"
      check_method: |
        # Mini-Pilot 결과 확인
        cat work/specs/stage4-outputs/phase2/mini-pilot-report.yaml
      failure_impact: "Mini-Pilot 실패 → 대량 생성 후 전체 재작업"

    2_build_success:
      question: "전체 프로젝트 빌드가 성공하는가?"
      check_method: |
        cd next-hallain && ./gradlew build
      failure_impact: "빌드 실패 → Stage 5 진행 불가"

    3_generated_count:
      question: "생성된 Feature 수가 Spec과 일치하는가?"
      check_method: |
        # 생성된 Controller 수
        find next-hallain/src/main/java -name "*Controller.java" | wc -l
        # 목표 Feature 수
        grep -c "feature_id:" work/specs/stage1-outputs/phase1/feature-inventory.yaml
      failure_impact: "불일치 → 누락 Feature 존재"

    4_test_coverage:
      question: "테스트 파일이 생성되었는가?"
      check_method: |
        find next-hallain/src/test/java -name "*Test.java" | wc -l
      failure_impact: "테스트 없음 → Stage 5 검증 불가"
```

---

## Stage 5: Assurance Gate (Final)

### Critical Checklist

```yaml
stage5_gate:
  verification_command: "/s5-05-assurance-quality-gate 실행"

  critical_items:
    1_structural_score:
      question: "Structural Score가 기준 이상인가?"
      check_method: |
        grep "structural_score:" work/specs/stage5-outputs/phase1/structural-report.yaml
      acceptable_value: ">= 85"
      failure_impact: "미달 → 아키텍처 표준 위반"

    2_functional_score:
      question: "Functional Score가 기준 이상인가?"
      check_method: |
        grep "functional_score:" work/specs/stage5-outputs/phase2/functional-report.yaml
      acceptable_value: ">= 85"
      failure_impact: "미달 → 비즈니스 로직 불일치"

    3_sql_equivalence:
      question: "SQL Equivalence가 35점 이상인가?"
      check_method: |
        grep "sql_equivalence:" work/specs/stage5-outputs/phase2/functional-report.yaml
      acceptable_value: ">= 35/40"
      failure_impact: "미달 → 데이터 처리 오류"

    4_overall_quality:
      question: "Overall Quality Score가 90점 이상인가?"
      check_method: |
        grep "overall_score:" work/specs/stage5-outputs/phase5/quality-gate-report.yaml
      acceptable_value: ">= 90"
      failure_impact: "미달 → Quality Gate 실패, 프로덕션 배포 불가"

    5_human_approval:
      question: "Human 최종 승인이 완료되었는가?"
      required: true
      failure_impact: "미승인 → 프로젝트 완료 불가"
```

---

## Quick Reference: Gate 통과 기준 요약

| Stage | 핵심 지표 | 최소 기준 | 검증 방법 |
|-------|----------|----------|----------|
| **1** | Controller Coverage | 100% | Legacy vs Inventory 비교 |
| **1** | SP Identification | 100% | XML grep 비교 |
| **2** | Coverage | ≥ 99% | comparison-report.yaml |
| **2** | Unresolved Gaps | 0 | gap-analysis.yaml |
| **3** | Circular Dependencies | 0 | dependency-graph.yaml |
| **3** | Naming Convention ADR | 존재 | ADR 파일 확인 |
| **4** | Mini-Pilot Success | 6/6 | mini-pilot-report.yaml |
| **4** | Build Success | Pass | gradlew build |
| **5** | Structural Score | ≥ 85 | structural-report.yaml |
| **5** | Functional Score | ≥ 85 | functional-report.yaml |
| **5** | Overall Score | ≥ 90 | quality-gate-report.yaml |

---

## Remediation 절차

Gate 실패 시:

1. **실패 원인 분석**: 어떤 항목이 미달인가?
2. **Root Cause 식별**: 왜 미달인가? (Skill 문제? 데이터 문제?)
3. **수정 범위 결정**: 해당 Phase만? 이전 Stage까지?
4. **Pattern 기반 수정**: 유사 문제 일괄 처리
5. **재검증**: Gate Checklist 재실행

자세한 내용: [03-remediation-procedures.md](03-remediation-procedures.md)

---

**Next:** [APPENDIX/01-glossary.md](../APPENDIX/01-glossary.md)
