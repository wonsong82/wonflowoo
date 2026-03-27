작성자 : 송혜선 책임/AX선행개발팀

---

# Windows 사용자를 위한 Claude Code 설정 가이드

> 이 문서는 **비개발자도 따라할 수 있도록** 모든 단계를 상세히 설명합니다.
> 각 단계를 순서대로 진행해 주세요.

---

## 목차

1. [사전 준비물 확인](#1-사전-준비물-확인)
2. [VSCode 설치](#2-vscode-설치)
3. [Node.js 설치 (NVM 활용)](#3-nodejs-설치-nvm-활용)
4. [Git 설치](#4-git-설치)
5. [AWS Bedrock API 키 발급](#5-aws-bedrock-api-키-발급)
6. [시스템 환경변수 설정](#6-시스템-환경변수-설정)
7. [Claude Code 설치](#7-claude-code-설치)
8. [VSCode Extension 설치](#8-vscode-extension-설치)
9. [설치 확인 및 테스트](#9-설치-확인-및-테스트)
10. [자주 발생하는 오류 및 해결방법](#10-자주-발생하는-오류-및-해결방법)

---

## 1. 사전 준비물 확인

시작하기 전에 아래 항목을 준비해 주세요:

| 항목 | 설명 |
|------|------|
| Windows PC | Windows 10 이상 |
| 인터넷 연결 | 소프트웨어 다운로드 및 API 통신에 필요 |
| AWS 계정 | Bedrock API 키 발급을 위해 필요 (각 팀의 AWS 담당자에게 계정 생성 요청) |
| 관리자 권한 | 프로그램 설치 및 환경변수 설정에 필요 |

---

## 2. VSCode 설치

### 2-1. 다운로드

1. 웹 브라우저를 열고 주소창에 아래 주소를 입력합니다:
   ```
   https://code.visualstudio.com/
   ```
2. 화면 중앙의 **"Download for Windows"** 버튼을 클릭합니다.
3. `VSCodeUserSetup-x64-*.exe` 파일이 다운로드됩니다.

### 2-2. 설치

1. 다운로드된 `.exe` 파일을 **더블클릭**합니다.
2. "사용권 계약에 동의합니다"에 체크 → **다음** 클릭
3. 설치 경로는 기본값 그대로 두고 → **다음** 클릭
4. **추가 작업 선택** 화면에서 아래 항목을 **모두 체크**합니다:
   - [x] 바탕 화면에 바로가기 만들기
   - [x] PATH에 추가 (다시 시작한 후 사용 가능)
   - [x] 지원되는 파일 형식에 대한 편집기로 Code 등록
5. **설치** 버튼을 클릭하고 완료될 때까지 기다립니다.
6. **마침** 버튼을 클릭합니다.

---

## 3. Node.js 설치 (NVM 활용)

Claude Code는 Node.js가 필요합니다. NVM(Node Version Manager)을 사용하면 Node.js 버전을 쉽게 관리할 수 있습니다.

### 3-1. NVM for Windows 다운로드

1. 웹 브라우저에서 아래 주소로 이동합니다:
   ```
   https://github.com/coreybutler/nvm-windows/releases
   ```
2. 최신 릴리스에서 **nvm-setup.exe** 파일을 클릭하여 다운로드합니다.

### 3-2. NVM 설치

1. 다운로드된 `nvm-setup.exe`를 **더블클릭**합니다.
2. 설치 경로는 기본값(`C:\Users\<사용자명>\AppData\Local\nvm`)으로 두고 **Next** 클릭
3. Node.js Symlink 경로도 기본값(`C:\nvm4w\nodejs`)으로 두고 **Next** 클릭
4. **Install** → **Finish** 클릭

### 3-3. Node.js 설치

1. **Windows 검색창**(작업 표시줄 왼쪽 하단 돋보기 아이콘)에 `cmd`를 입력합니다.
2. **"명령 프롬프트"**가 나타나면 **마우스 오른쪽 클릭** → **"관리자 권한으로 실행"** 선택
3. 아래 명령어를 **한 줄씩** 입력하고 Enter를 누릅니다:

```cmd
nvm install 22
```
> Node.js 22 버전을 다운로드합니다. 완료까지 1~2분 소요됩니다.

```cmd
nvm use 22
```
> 설치한 22 버전을 사용하도록 설정합니다.

4. 설치가 잘 되었는지 확인합니다:

```cmd
node -v
```
> `v22.x.x` 형태로 버전이 출력되면 성공입니다.

```cmd
npm -v
```
> 숫자(예: `10.x.x`)가 출력되면 성공입니다.

---

## 4. Git 설치

### 4-1. 다운로드

1. 웹 브라우저에서 아래 주소로 이동합니다:
   ```
   https://git-scm.com/download/win
   ```
2. **"64-bit Git for Windows Setup"** 을 클릭하여 다운로드합니다.

### 4-2. 설치

1. 다운로드된 `Git-*.exe` 파일을 **더블클릭**합니다.
2. 대부분의 옵션은 **기본값 그대로** 두고 **Next**를 계속 클릭합니다.
3. 아래 화면에서만 주의해 주세요:
   - **"Adjusting your PATH environment"** 화면:
     → **"Git from the command line and also from 3rd-party software"** 선택 (기본값)
   - **"Choosing the default editor"** 화면:
     → **"Use Visual Studio Code as Git's default editor"** 선택
4. **Install** → **Finish** 클릭

### 4-3. 설치 확인

1. 명령 프롬프트(`cmd`)를 **새로 열고** 아래를 입력합니다:

```cmd
git --version
```
> `git version 2.x.x.windows.x` 형태로 출력되면 성공입니다.

---

## 5. AWS Bedrock API 키 발급

### 5-1. AWS 계정 준비

- 각 팀의 **AWS 담당자**에게 개인 AWS 계정 생성을 요청합니다.
- 계정 생성 후 로그인 정보(ID, 비밀번호)를 받습니다.

### 5-2. AWS 콘솔 접속

1. 웹 브라우저에서 **AWS 콘솔**에 접속하여 로그인합니다.
2. 로그인 후 화면 상단의 **검색창**에 `IAM`을 입력하고 클릭합니다.

### 5-3. API 키 생성

1. IAM 대시보드 왼쪽 메뉴에서 **"사용자"** 클릭
2. 본인의 사용자 이름을 클릭
3. **"보안 자격 증명"** 탭 클릭
4. **"액세스 키"** 섹션에서 **"액세스 키 만들기"** 버튼 클릭
5. 사용 사례 선택:
   - **"Command Line Interface(CLI)"** 선택
   - 하단의 확인 체크박스 체크
   - **다음** 클릭
6. 설명 태그(선택사항): `claude-code-bedrock` 등 알아볼 수 있는 이름 입력
7. **"액세스 키 만들기"** 클릭

### 5-4. API 키 정보 저장

생성이 완료되면 아래 두 가지 정보가 표시됩니다. **반드시 안전한 곳에 복사하여 저장**해 주세요:

| 항목 | 예시 | 설명 |
|------|------|------|
| **액세스 키 ID** | `AKIA1234567890ABCDEF` | AWS_ACCESS_KEY_ID에 사용 |
| **비밀 액세스 키** | `ABSkbHVjeSThd...` | AWS_SECRET_ACCESS_KEY에 사용 |

> **주의:** 비밀 액세스 키는 이 화면에서 **한 번만** 표시됩니다. 페이지를 닫으면 다시 확인할 수 없으므로 반드시 메모장이나 안전한 문서에 복사해 두세요.

---

## 6. 시스템 환경변수 설정

환경변수란 Windows 시스템에 미리 저장해 두는 설정값입니다. Claude Code가 실행될 때 이 값을 읽어서 동작합니다.

### 6-1. 환경변수 설정 화면 열기

1. 키보드에서 **Windows 키 + S** 를 눌러 검색창을 엽니다.
2. **`환경변수`** 를 입력합니다.
3. **"시스템 환경 변수 편집"** 을 클릭합니다.
   (또는: U cloud > desktop 관리 > 환경변수)
4. 열린 창에서 하단의 **"환경 변수(N)..."** 버튼을 클릭합니다.

### 6-2. 사용자 변수 추가하기

상단의 **"사용자 변수"** 영역에서 변수를 하나씩 추가합니다.

**변수 추가 방법:**
1. **"새로 만들기(N)..."** 버튼 클릭
2. **변수 이름**과 **변수 값**을 입력
3. **확인** 클릭

아래 표의 변수를 **하나씩** 추가해 주세요:

| 변수 이름 | 변수 값 | 설명 |
|-----------|---------|------|
| `CLAUDE_CODE_USE_BEDROCK` | `1` | Bedrock 사용 활성화 (Claude Max 사용자는 `0`으로 설정) |
| `ANTHROPIC_MODEL` | `global.anthropic.claude-sonnet-4-5-20250929-v1:0` | 기본 Claude 모델 지정 (Claude Max 사용자는 설정 불필요, `/model` 명령어로 지정 가능) |
| `ANTHROPIC_SMALL_FAST_MODEL` | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | 빠른 응답용 Haiku 모델 |
| `AWS_BEARER_TOKEN_BEDROCK` | `본인이 발급받은 Bedrock token` | Bedrock 인증 토큰 |
| `AWS_REGION` | `us-east-1` | AWS 리전 |
| `CLAUDE_CODE_GIT_BASH_PATH` | `C:\Program Files\Git\bin\bash.exe` | Git Bash 실행 경로 |
| `NODE_TLS_REJECT_UNAUTHORIZED` | `0` | SSL 인증서 검증 비활성화 |
| `NVM_HOME` | `C:\Users\<사용자명>\AppData\Local\nvm` | NVM 설치 경로 (본인 경로에 맞게 수정) |
| `NVM_SYMLINK` | `C:\nvm4w\nodejs` | Node.js 심볼릭 링크 경로 |

> **`<사용자명>` 확인 방법:** 명령 프롬프트(`cmd`)를 열고 `echo %USERNAME%`을 입력하면 본인의 사용자명이 표시됩니다.

### 6-3. 환경변수 확인

1. 모든 변수를 추가했으면 **확인** → **확인** → **확인** 을 눌러 모든 창을 닫습니다.
2. **명령 프롬프트를 새로 열고** 아래 명령어로 제대로 설정되었는지 확인합니다:

```cmd
echo %CLAUDE_CODE_USE_BEDROCK%
```
> `1`이 출력되면 정상입니다.

```cmd
echo %AWS_REGION%
```
> `us-east-1`이 출력되면 정상입니다.

> **중요:** 환경변수 설정 후에는 반드시 **명령 프롬프트(cmd)를 새로 열어야** 변경사항이 반영됩니다. 기존에 열려 있던 cmd 창에서는 이전 설정이 유지됩니다.

---

## 7. Claude Code 설치

### 7-1. 설치

1. 명령 프롬프트(`cmd`)를 **관리자 권한으로** 엽니다.
   (검색창에 `cmd` 입력 → 마우스 오른쪽 클릭 → "관리자 권한으로 실행")
2. 아래 명령어를 입력합니다:

```cmd
npm install -g @anthropic-ai/claude-code
```
> 설치에 1~3분 정도 소요됩니다. 완료될 때까지 기다려 주세요.

### 7-2. 설치 확인

```cmd
claude --version
```
> 버전 번호(예: `1.x.x`)가 표시되면 성공입니다.

### 7-3. 최초 실행

```cmd
claude
```
> 처음 실행하면 초기 설정이 진행됩니다. 화면의 안내에 따라 진행해 주세요.

---

## 8. VSCode Extension 설치

### 8-1. Claude Code Extension 설치

1. **VSCode**를 실행합니다.
2. 왼쪽 사이드바에서 **확장(Extensions)** 아이콘을 클릭합니다.
   (또는 키보드 단축키 `Ctrl + Shift + X`)
3. 검색창에 **`Claude Code`** 를 입력합니다.
4. **"Claude Code"** (Anthropic 제작)를 찾아 **Install** 버튼을 클릭합니다.
5. 설치가 완료되면 왼쪽 사이드바 또는 하단에 Claude Code 아이콘이 나타납니다.

### 8-2. Extension 동작 확인

1. VSCode 하단의 **터미널**을 엽니다. (메뉴: 터미널 → 새 터미널, 또는 `` Ctrl + ` ``)
2. 터미널에 아래를 입력합니다:

```cmd
claude
```
> Claude Code가 시작되면 정상입니다.

---

## 9. 설치 확인 및 테스트

모든 설치가 완료되었는지 최종 확인합니다. 명령 프롬프트를 **새로 열고** 아래 명령어를 하나씩 실행해 보세요:

```cmd
:: 1. Node.js 확인
node -v

:: 2. npm 확인
npm -v

:: 3. Git 확인
git --version

:: 4. Claude Code 확인
claude --version

:: 5. 환경변수 확인
echo %CLAUDE_CODE_USE_BEDROCK%
echo %AWS_REGION%
echo %ANTHROPIC_MODEL%
```

모든 명령어에서 정상적인 결과가 출력되면 설정이 완료된 것입니다.

---

## 10. 자주 발생하는 오류 및 해결방법

### 오류 1: `'node'은(는) 내부 또는 외부 명령이 아닙니다`

**원인:** Node.js가 설치되지 않았거나 PATH에 등록되지 않음

**해결:**
1. NVM으로 Node.js를 설치했는지 확인:
   ```cmd
   nvm list
   ```
2. 설치된 버전이 없으면 다시 설치:
   ```cmd
   nvm install 22
   nvm use 22
   ```
3. 명령 프롬프트를 **새로 열고** 다시 시도

---

### 오류 2: `'claude'은(는) 내부 또는 외부 명령이 아닙니다`

**원인:** Claude Code가 설치되지 않았거나 npm 전역 경로가 PATH에 없음

**해결:**
1. Claude Code를 다시 설치합니다:
   ```cmd
   npm install -g @anthropic-ai/claude-code
   ```
2. npm 전역 경로를 확인합니다:
   ```cmd
   npm config get prefix
   ```
3. 출력된 경로(예: `C:\Users\<사용자명>\AppData\Roaming\npm`)가 **시스템 환경변수의 PATH**에 포함되어 있는지 확인합니다.

---

### 오류 3: SSL/TLS 인증 오류 (UNABLE_TO_VERIFY_LEAF_SIGNATURE 등)

**원인:** 사내 네트워크 환경에서 SSL 인증서 검증 실패

**해결 방법 1 - 간단한 방법 (보안 수준 낮음):**

환경변수에 `NODE_TLS_REJECT_UNAUTHORIZED`가 `0`으로 설정되어 있는지 확인합니다.
(6단계에서 이미 설정한 경우 이 오류는 발생하지 않아야 합니다.)

**해결 방법 2 - 인증서를 직접 등록하는 방법 (권장):**

1. 기본 인증서(.pem) 파일을 확보합니다:
   - 브라우저 주소창의 자물쇠 아이콘 → 인증서 관리 → 내보내기

2. 기본 인증서와 사내(LG CNS) 인증서를 결합합니다:
   ```cmd
   :: Git Bash에서 실행
   cat <기본_인증서_경로> <LG_CNS_인증서_경로> > combined_cert.pem
   ```

3. 결합된 인증서 경로를 환경변수에 등록합니다:
   - 변수 이름: `NODE_EXTRA_CA_CERTS`
   - 변수 값: `C:\Users\<사용자명>\combined_cert.pem` (파일을 저장한 경로)

---

### 오류 4: Bedrock 연결 실패 / 인증 오류

**원인:** AWS 관련 환경변수가 올바르게 설정되지 않음

**해결:**
1. 아래 환경변수가 모두 설정되어 있는지 확인합니다:
   ```cmd
   echo %CLAUDE_CODE_USE_BEDROCK%
   echo %AWS_BEARER_TOKEN_BEDROCK%
   echo %AWS_REGION%
   ```
2. 값이 비어 있거나 `%변수이름%` 그대로 출력되면, 6단계로 돌아가서 환경변수를 다시 설정합니다.
3. 환경변수 설정 후 **명령 프롬프트를 반드시 새로 열어야** 합니다.

---

### 오류 5: `nvm`이 인식되지 않는 경우

**원인:** NVM이 설치되지 않았거나 환경변수가 누락됨

**해결:**
1. NVM을 재설치합니다 (3단계 참조).
2. 환경변수에 아래가 등록되어 있는지 확인합니다:
   - `NVM_HOME`: NVM 설치 경로
   - `NVM_SYMLINK`: Node.js 심볼릭 링크 경로
3. **시스템 환경변수의 PATH**에 `%NVM_HOME%`과 `%NVM_SYMLINK%`가 포함되어 있는지 확인합니다.

---

### 오류 6: Git Bash 경로 오류

**원인:** Git이 기본 경로가 아닌 다른 위치에 설치됨

**해결:**
1. Git이 설치된 경로를 확인합니다:
   ```cmd
   where git
   ```
2. 출력된 경로를 참고하여 `CLAUDE_CODE_GIT_BASH_PATH` 환경변수의 값을 수정합니다.
   예) `C:\Program Files\Git\bin\bash.exe`

---
