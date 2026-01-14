# 전 세계 배포 가이드 (Deployment Guide)

이 프로젝트는 **Render.com**과 같은 최신 클라우드 플랫폼에 즉시 배포할 수 있도록 설정되어 있습니다.
아래 단계만 따라하면 5분 안에 전 세계 어디서나 접속 가능한 URL을 얻을 수 있습니다.

---

## 1. 깃허브(GitHub)에 코드 업로드
현재 로컬에 있는 코드를 GitHub 저장소(Repository)에 올려야 합니다.

1. GitHub에서 새로운 저장소(New Repository)를 생성합니다.
2. 로컬 터미널에서 아래 명령어로 코드를 업로드합니다:
   ```bash
   git init
   git add .
   git commit -m "Initial deploy to global"
   git branch -M main
   git remote add origin https://github.com/사용자아이디/저장소이름.git
   git push -u origin main
   ```

---

## 2. Render.com에서 웹 서비스 생성 (무료)
가장 쉽고 빠른 방법입니다.

1. [Render.com](https://render.com)에 접속하여 회원가입/로그인합니다.
2. 대시보드에서 **New +** 버튼을 누르고 **Web Service**를 선택합니다.
3. **Build and deploy from a Git repository**를 선택하고, 방금 업로드한 GitHub 저장소를 연결합니다.

---

## 3. 배포 설정 (자동 감지됨)
Render가 자동으로 설정을 감지하지만, 아래 내용과 일치하는지 확인하세요.

- **Name**: `veritas-guard` (원하는 이름)
- **Region**: `Singapore` (한국과 가까움) 또는 `Oregon`
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn run:app`

---

## 4. 환경 변수 설정 (Environment Variables)
프로덕션 환경을 위해 아래 변수들을 설정하는 것이 좋습니다 (선택 사항). Render 설정 메뉴 중 'Environment' 탭에서 추가합니다.

- `PYTHON_VERSION`: `3.9.18` (권장)
- `SECRET_KEY`: (복잡한 무작위 문자열 입력)
- `WEB_CONCURRENCY`: `2` (무료 티어에서는 2가 적당함)

---

## 5. 배포 완료
**Create Web Service** 버튼을 누르면 배포가 시작됩니다.
약 3~5분 후 배포가 완료되면 `https://veritas-guard.onrender.com` 과 같은 전 세계 접속 가능한 URL이 생성됩니다.

> **주의사항**: 무료 티어는 15분 동안 접속이 없으면 절전 모드(Spin Down)로 들어가며, 다음 접속 시 30초 정도 딜레이가 발생할 수 있습니다 (Cold Start).
