---
name: {skill-name-with-hyphens}
description: Use when {분석이 필요한 상황/증상 - 트리거 조건만}
---

# {Analysis Skill Name}

> **CRITICAL - 파일 위치**: `.claude/skills/{name}/SKILL.md` 경로에 저장 필수.
> 디렉토리명 = `name` 필드 (정확히 일치). 중첩 구조 금지.

> **CRITICAL**: Frontmatter(위 `---` 블록)는 반드시 파일 맨 처음에 raw YAML로 시작해야 합니다.
> 코드 블록(` ```yaml `)으로 감싸면 Claude Code가 인식하지 못합니다.

> **Skill Type**: Analysis (소스코드/데이터에서 정보 추출)

## 1. Overview

### 1.1 Purpose

{소스코드/데이터에서 추출할 정보를 명확하게 기술}

**분석 대상:**
- {분석 대상 1}
- {분석 대상 2}

**추출 정보:**
- {추출할 정보 1}
- {추출할 정보 2}

### 1.2 Analysis Scope

| Aspect | In Scope | Out of Scope |
|--------|----------|--------------|
| Files | {대상 파일 패턴} | {제외 파일} |
| Elements | {분석 요소} | {제외 요소} |
| Depth | {분석 깊이} | {제한 사항} |

---

## 2. Prerequisites

### 2.1 Source Requirements

```yaml
source_requirements:
  - name: "{소스 이름}"
    type: "codebase|database|document"
    location: "${LEGACY_CODEBASE}/{path}"
    format: "java|xml|sql"
```

### 2.2 Analysis Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| Regex | Pattern extraction | {패턴} |
| AST Parser | Code structure | {언어} |
| XML Parser | Configuration | {스키마} |

---

## 3. Methodology

### 3.1 Analysis Pipeline

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Source  │────▶│   Scan   │────▶│  Extract │────▶│Structure │
│  Input   │     │ & Filter │     │   Data   │     │  Output  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

### 3.2 Scan Patterns

```yaml
scan_patterns:
  - pattern_name: "{패턴 이름}"
    regex: "{정규식}"
    applies_to: "{대상 파일}"
    extracts:
      - "{추출 필드 1}"
      - "{추출 필드 2}"
```

### 3.3 Classification Rules

| Category | Criteria | Action |
|----------|----------|--------|
| {분류 1} | {기준} | {처리} |
| {분류 2} | {기준} | {처리} |

---

## 4. Outputs

### 4.1 Output Structure

```yaml
output_structure:
  summary:
    file: "summary.yaml"
    contains:
      - "Total counts"
      - "Classification breakdown"
      - "Coverage metrics"

  details:
    directory: "{detail-dir}/"
    per_item: true
    format: "yaml"
```

### 4.2 Output Schema

```yaml
# {output-file}.yaml
metadata:
  generated_by: "${SKILL_NAME}"
  generated_at: "${TIMESTAMP}"
  source: "{source_path}"

summary:
  total_items: {count}
  by_category:
    {category_1}: {count}
    {category_2}: {count}

items:
  - id: "{item_id}"
    name: "{item_name}"
    category: "{category}"
    details:
      {extracted_field_1}: "{value}"
      {extracted_field_2}: "{value}"
```

---

## 5. Quality Checks

### 5.1 Coverage Validation

| Metric | Target | Formula |
|--------|--------|---------|
| Source Coverage | >= 90% | analyzed_files / total_files |
| Element Coverage | >= 95% | extracted_items / expected_items |

### 5.2 Data Quality

- [ ] No duplicate entries
- [ ] All required fields populated
- [ ] Valid classification for all items
- [ ] Reference integrity maintained

---

## 6. Error Handling

### 6.1 Parse Errors

| Error Type | Handling |
|------------|----------|
| File not found | Log and continue |
| Parse failure | Mark as UNANALYZED |
| Encoding issue | Try UTF-8, then ISO-8859-1 |

### 6.2 Edge Cases

| Case | Handling |
|------|----------|
| Empty file | Skip with warning |
| Binary file | Skip |
| Huge file (>10MB) | Process in chunks |

---

## 7. Examples

### 7.1 Sample Source

```java
// 분석 대상 소스 코드 예시
@Controller
@RequestMapping("/api/sample")
public class SampleController {
    @PostMapping("/list")
    public ResponseEntity<?> getList(@RequestBody RequestDto dto) {
        // ...
    }
}
```

### 7.2 Sample Output

```yaml
# 분석 결과 예시
item:
  id: "SAMPLE-001"
  type: "endpoint"
  class: "SampleController"
  method: "getList"
  path: "/api/sample/list"
  http_method: "POST"
  request_type: "RequestDto"
```
