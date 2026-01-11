# VeritasGuard AI - Toubina Project

## 🚀 빠른 시작 (HTTPS & 도메인 설정)

이 프로젝트는 현재 `https://www.aisolute.com` 도메인 설정을 지원합니다.

### 1. 도메인 연결 (최초 1회 필수)
로컬 환경에서 도메인을 사용하려면 Hosts 파일 설정이 필요합니다.
1. `setup_hosts.bat` 파일을 마우스 오른쪽 버튼으로 클릭하세요.
2. **"관리자 권한으로 실행"**을 선택하세요.
3. 설정 완료 메시지를 확인합니다.

### 2. 서버 실행
`start.bat` 파일을 더블 클릭하여 서버를 실행합니다.

### 3. 접속하기
브라우저를 열고 다음 주소로 접속하세요:
👉 **[https://www.aisolute.com](https://www.aisolute.com)**
(또는 [https://localhost](https://localhost))

> **주의:** 로컬 인증서를 사용하므로 "안전하지 않음" 경고가 뜰 수 있습니다. **[고급] -> [이동]**을 눌러 진행해주세요.

---

## 🛠 기존 설치 방법


VeritasGuard AI는 딥페이크 및 AI 생성 허위 정보를 탐지하고 콘텐츠의 진위 여부를 확인하는 웹 플랫폼 MVP입니다.

## 🚀 시작하기

### 1. 환경 설정 및 설치

Windows 환경 기준으로 다음 명령어를 터미널에 입력하여 가상 환경을 생성하고 의존성을 설치하세요.

```powershell
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (선택 사항, 스크립트로 실행 시 불필요)
.\venv\Scripts\Activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 서버 실행

설치가 완료되면 다음 명령어로 서버를 시작합니다.

```powershell
python run.py
```

서버가 시작되면 웹 브라우저에서 [http://127.0.0.1:8000](http://127.0.0.1:8000) 으로 접속하여 테스트할 수 있습니다.

## 🛠 기술 스택

- **Backend**: Python, Flask, SQLAlchemy
- **AI/ML**: TensorFlow (Deepfake Detection), Pillow (Image Processing)
- **Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JS

## ⚠️ 참고 사항

- 현재 MVP 버전에는 사전 학습된 모델 파일(`deepfake_model.h5`)이 포함되어 있지 않습니다.
- 모델 파일이 없을 경우 시스템은 자동으로 **Mock Detector** 모드로 전환되어 시뮬레이션된 결과를 반환합니다.
- 실제 모델 적용 시 `app/ai/` 디렉토리에 `.h5` 모델 파일을 배치하세요.
