# NAT Traversal & UDP Hole Punching 심화 가이드

> 게임 개발자 출신이라면 "왜 P2P 매치메이킹이 안 되지?"라는 좌절을 겪어봤을 것이다.
> 이 문서는 그 근본 원인인 NAT와, 이를 극복하는 기술들을 깊이 파고든다.

---

## 목차

1. [NAT Traversal 개요 - 왜 필요한가](#1-nat-traversal-개요---왜-필요한가)
2. [NAT 타입별 상세 동작](#2-nat-타입별-상세-동작)
3. [STUN 프로토콜 상세](#3-stun-프로토콜-상세)
4. [TURN 프로토콜 상세](#4-turn-프로토콜-상세)
5. [UDP Hole Punching 상세 메커니즘](#5-udp-hole-punching-상세-메커니즘)
6. [TCP Hole Punching](#6-tcp-hole-punching)
7. [ICE (Interactive Connectivity Establishment)](#7-ice-interactive-connectivity-establishment)
8. [실제 활용 사례](#8-실제-활용-사례)
9. [Carrier-Grade NAT (CGNAT) 문제](#9-carrier-grade-nat-cgnat-문제)
10. [IPv6와 NAT Traversal의 미래](#10-ipv6와-nat-traversal의-미래)
11. [비교 대상 기술/프로토콜](#11-비교-대상-기술프로토콜)
12. [참고 자료](#12-참고-자료)

---

## 1. NAT Traversal 개요 - 왜 필요한가

### 핵심 문제: NAT는 일방통행이다

```
게임 클라이언트 A                                    게임 클라이언트 B
(192.168.1.10)                                      (10.0.0.5)
     │                                                   │
     ▼                                                   ▼
┌─────────┐         인터넷          ┌─────────┐
│ NAT A   │ ◄───── ? ──────────── │ NAT B   │
│ 1.1.1.1 │                       │ 2.2.2.2 │
└─────────┘                       └─────────┘

문제: B가 A에게 직접 패킷을 보내려 해도,
      NAT A는 "너 누군데?" 하고 패킷을 DROP 한다.
```

### 왜 이게 문제인가? - 게임 개발자의 관점

| 시나리오 | NAT가 없을 때 | NAT 뒤에서 |
|---------|-------------|-----------|
| 1:1 대전 게임 | IP 직접 연결 | 연결 불가 (양쪽 모두 NAT 뒤) |
| 보이스 채팅 | 직접 UDP 스트림 | 릴레이 서버 필요 → 지연 증가 |
| 파일 공유 (P2P) | 직접 전송 | 중계 서버 비용 발생 |
| IoT 원격 접속 | 포트 열어서 접근 | 포트포워딩 수동 설정 필요 |

### NAT Traversal이란?

**한 줄 요약**: NAT 뒤에 있는 두 디바이스가 직접 통신할 수 있도록 "구멍을 뚫는" 기술의 총칭

NAT는 원래 IPv4 주소 부족 해결용이었지만, 사실상 방화벽 역할도 한다. 외부에서 내부로의 unsolicited(요청하지 않은) 패킷을 차단하기 때문이다. P2P 통신에서는 양쪽 모두가 "내부"이므로, 누군가 먼저 구멍을 뚫어야 한다.

---

## 2. NAT 타입별 상세 동작

> RFC 3489에서 정의한 4가지 NAT 분류. 현실에서는 이 분류에 깔끔하게 안 맞는 NAT도 많지만,
> 여전히 가장 널리 쓰이는 분류 체계다.

### 2.1 Full Cone NAT (완전 원뿔형)

```
내부 호스트 A (192.168.1.10:5000)
     │
     ▼  NAT 매핑: 192.168.1.10:5000 → 1.1.1.1:8000
┌────────────┐
│ Full Cone  │
│    NAT     │  1.1.1.1:8000
└────────────┘
     │
     ▼  ← 누구든지 1.1.1.1:8000으로 보내면 A에게 전달됨

외부 호스트 X (3.3.3.3:9000) → 1.1.1.1:8000 → A ✅ 전달됨
외부 호스트 Y (4.4.4.4:7000) → 1.1.1.1:8000 → A ✅ 전달됨
```

**동작 원리**:
- 내부에서 한 번이라도 외부로 패킷을 보내면, 해당 매핑(내부IP:포트 → 외부IP:포트)이 생성됨
- 이후 **어떤 외부 호스트든** 해당 외부IP:포트로 패킷을 보내면 내부로 전달
- 게임 개발자 비유: "서버 소켓 바인딩"과 유사 - 포트만 알면 누구나 접속 가능

**홀펀칭 난이도**: 매우 쉬움 (STUN으로 외부 주소만 알면 끝)

---

### 2.2 Restricted Cone NAT (제한 원뿔형 / Address Restricted)

```
내부 호스트 A (192.168.1.10:5000)
     │
     ▼  NAT 매핑: 192.168.1.10:5000 → 1.1.1.1:8000
┌─────────────────┐
│ Restricted Cone │
│      NAT        │  1.1.1.1:8000
└─────────────────┘
     │
     ▼  ← A가 먼저 보낸 IP에서만 응답 허용

시나리오: A가 3.3.3.3으로 패킷을 보낸 적이 있을 때:
  외부 호스트 X (3.3.3.3:9000) → 1.1.1.1:8000 → A ✅ (IP 일치)
  외부 호스트 X (3.3.3.3:7777) → 1.1.1.1:8000 → A ✅ (IP 일치, 포트 무관)
  외부 호스트 Y (4.4.4.4:9000) → 1.1.1.1:8000 → A ❌ (IP 불일치)
```

**동작 원리**:
- 내부 → 외부로 패킷을 보내면, **해당 외부 IP 주소** 전체에 대해 매핑 허용
- 외부 IP는 일치해야 하지만, 포트는 아무거나 가능
- 게임 개발자 비유: "화이트리스트 서버" - 내가 먼저 접속한 서버 IP에서만 패킷 수신

**홀펀칭 난이도**: 쉬움 (양쪽이 서로에게 패킷을 한 번씩 보내면 됨)

---

### 2.3 Port Restricted Cone NAT (포트 제한 원뿔형)

```
내부 호스트 A (192.168.1.10:5000)
     │
     ▼  NAT 매핑: 192.168.1.10:5000 → 1.1.1.1:8000
┌──────────────────────┐
│ Port Restricted Cone │
│         NAT          │  1.1.1.1:8000
└──────────────────────┘
     │
     ▼  ← A가 먼저 보낸 정확한 IP:포트에서만 응답 허용

시나리오: A가 3.3.3.3:9000으로 패킷을 보낸 적이 있을 때:
  외부 호스트 X (3.3.3.3:9000) → 1.1.1.1:8000 → A ✅ (IP+포트 일치)
  외부 호스트 X (3.3.3.3:7777) → 1.1.1.1:8000 → A ❌ (포트 불일치!)
  외부 호스트 Y (4.4.4.4:9000) → 1.1.1.1:8000 → A ❌ (IP 불일치)
```

**동작 원리**:
- Restricted Cone과 비슷하지만, **외부 IP + 포트** 모두 일치해야 통과
- 게임 개발자 비유: "정확한 IP:Port 화이트리스트" - connect()한 정확한 endpoint만 허용

**홀펀칭 난이도**: 보통 (양쪽이 정확한 IP:Port로 서로 패킷을 보내야 함)

---

### 2.4 Symmetric NAT (대칭형)

```
내부 호스트 A (192.168.1.10:5000)
     │
     ├─→ 3.3.3.3:9000 전송 시 → NAT 매핑: 1.1.1.1:8000
     │
     └─→ 4.4.4.4:7000 전송 시 → NAT 매핑: 1.1.1.1:8001  ← 다른 포트!
          (목적지가 다르면 매핑도 달라짐)

┌───────────────┐
│  Symmetric    │
│     NAT       │
└───────────────┘

STUN 서버(5.5.5.5)에게 물어본 결과: "너는 1.1.1.1:8002야"
실제 피어와 통신할 때의 매핑:          1.1.1.1:8003  ← 또 다름!

→ STUN으로 알아낸 포트가 실제 P2P 통신 시에는 쓸모없음!
```

**동작 원리**:
- **목적지(IP:Port)마다 다른 외부 포트를 할당**
- STUN 서버를 통해 알아낸 매핑이 실제 피어와 통신할 때는 달라짐
- 게임 개발자 비유: "매 connect()마다 소스 포트가 랜덤으로 바뀌는 소켓" - 예측 불가

**홀펀칭 난이도**: 매우 어려움 (사실상 불가능, TURN 릴레이 필요)

---

### 2.5 NAT 타입별 패킷 흐름 비교

```
                        외부 매핑 규칙          외부 필터 규칙
                    ┌────────────────────┬────────────────────────┐
Full Cone           │ 동일 내부 소스 →     │ 모든 외부 호스트       │
                    │ 항상 같은 외부 포트   │ 허용                  │
                    ├────────────────────┼────────────────────────┤
Restricted Cone     │ 동일 내부 소스 →     │ 내부에서 보낸 적 있는   │
                    │ 항상 같은 외부 포트   │ IP만 허용             │
                    ├────────────────────┼────────────────────────┤
Port Restricted     │ 동일 내부 소스 →     │ 내부에서 보낸 적 있는   │
Cone                │ 항상 같은 외부 포트   │ IP:Port만 허용        │
                    ├────────────────────┼────────────────────────┤
Symmetric           │ 목적지마다           │ 해당 목적지에서만       │
                    │ 다른 외부 포트       │ 응답 허용              │
                    └────────────────────┴────────────────────────┘
```

### 2.6 NAT 타입별 홀펀칭 성공률 조합표

> 핵심 매트릭스: P2P 게임 서버를 만들 때 반드시 참고해야 할 표

| Peer A \ Peer B | Full Cone | Restricted Cone | Port Restricted | Symmetric |
|:---------------:|:---------:|:---------------:|:---------------:|:---------:|
| **Full Cone**       | ✅ 성공    | ✅ 성공          | ✅ 성공          | ✅ 성공    |
| **Restricted Cone** | ✅ 성공    | ✅ 성공          | ✅ 성공          | ✅ 성공    |
| **Port Restricted** | ✅ 성공    | ✅ 성공          | ✅ 성공          | ❌ 실패    |
| **Symmetric**       | ✅ 성공    | ✅ 성공          | ❌ 실패          | ❌ 실패    |

**성공률 요약**:

| 조합 | 예상 성공률 | 비고 |
|------|-----------|------|
| Cone ↔ Cone | ~95% | 타이밍만 맞으면 거의 성공 |
| Cone ↔ Symmetric | ~80% | Full/Restricted Cone 쪽에서는 성공 |
| Port Restricted ↔ Symmetric | ~5% | 포트 예측이 맞을 때만 (거의 불가) |
| Symmetric ↔ Symmetric | ~0% | TURN 릴레이 필수 |

**왜 Symmetric NAT끼리는 안 되는가?**:

```
Peer A (Symmetric NAT)              Peer B (Symmetric NAT)
      │                                    │
      │  STUN으로 알아낸 포트: 8000          │  STUN으로 알아낸 포트: 9000
      │                                    │
      ├─→ B의 9000으로 전송 시              ├─→ A의 8000으로 전송 시
      │   NAT A가 새 포트 8005 할당         │   NAT B가 새 포트 9007 할당
      │                                    │
      │  B는 8000으로 보냈지만              │  A는 9000으로 보냈지만
      │  실제 A의 포트는 8005              │  실제 B의 포트는 9007
      │                                    │
      └─→ 서로 엉뚱한 포트로 보내고 있음 → 모두 DROP
```

---

## 3. STUN 프로토콜 상세

### 3.1 개요 (RFC 5389 / RFC 8489)

**STUN** = **S**ession **T**raversal **U**tilities for **N**AT

> 주의: 원래 RFC 3489에서는 "Simple Traversal of UDP through NATs"였다.
> RFC 5389에서 이름과 역할이 바뀌었다. STUN은 더 이상 단독 NAT traversal 솔루션이 아니라,
> **다른 프로토콜(ICE 등)의 도구**로 재정의되었다.

```
┌────────────────┐                    ┌────────────────┐
│  STUN Client   │                    │  STUN Server   │
│ (NAT 뒤 피어)   │                    │ (공인 IP)      │
│ 192.168.1.10   │                    │ 5.5.5.5:3478   │
└───────┬────────┘                    └───────┬────────┘
        │                                     │
        │  1. Binding Request                 │
        │  (src: 192.168.1.10:5000)          │
        │────────────────────────────────────→│
        │         NAT가 변환:                  │
        │    192.168.1.10:5000 → 1.1.1.1:8000│
        │                                     │
        │  2. Binding Response               │
        │  XOR-MAPPED-ADDRESS: 1.1.1.1:8000  │
        │←────────────────────────────────────│
        │                                     │
        │  "아, 내 공인 주소가 1.1.1.1:8000   │
        │   이구나! 이걸 상대 피어에게 알려주자" │
```

### 3.2 Binding Request/Response 상세

**STUN 메시지 구조** (20바이트 헤더):

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|0 0|     STUN Message Type     |         Message Length        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                         Magic Cookie (0x2112A442)             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                     Transaction ID (96 bits)                  |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

**주요 Attribute**:

| Attribute | 코드 | 설명 |
|-----------|------|------|
| MAPPED-ADDRESS | 0x0001 | 클라이언트의 공인 IP:Port (구 버전) |
| XOR-MAPPED-ADDRESS | 0x0020 | Magic Cookie로 XOR한 공인 IP:Port |
| USERNAME | 0x0006 | 인증용 사용자명 |
| MESSAGE-INTEGRITY | 0x0008 | HMAC-SHA1 무결성 검증 |
| FINGERPRINT | 0x8028 | CRC-32 기반 STUN 패킷 식별 |
| SOFTWARE | 0x8022 | 소프트웨어 이름/버전 |

> **왜 XOR을 하는가?** 일부 NAT 장비가 패킷 페이로드 안의 IP 주소까지 변환하는
> ALG(Application Layer Gateway) 동작 때문이다. XOR을 하면 NAT가 페이로드 내의
> IP를 인식하지 못해 이중 변환을 방지할 수 있다.

### 3.3 NAT 타입 판별 알고리즘

> RFC 3489에서 정의한 알고리즘이다. RFC 5389에서는 이 알고리즘이 제거되었지만,
> 여전히 많은 구현체에서 참조한다. RFC 5780이 이를 대체한다.

```
시작
  │
  ▼
Test I: STUN 서버 IP1:Port1로 Binding Request 전송
  │
  ├─ 응답 없음 → UDP 차단됨 (방화벽) → 종료
  │
  ▼
응답의 MAPPED-ADDRESS == 로컬 주소?
  │
  ├─ 예 → NAT 없음 (Public IP)
  │        │
  │        ▼
  │     Test II: CHANGE-REQUEST (IP+Port 변경 요청)
  │        │
  │        ├─ 응답 있음 → Open Internet
  │        └─ 응답 없음 → Symmetric Firewall
  │
  ├─ 아니오 → NAT 존재 확인
  │
  ▼
Test II: CHANGE-REQUEST (IP+Port 변경 요청) → 다른 IP:Port에서 응답?
  │
  ├─ 응답 있음 → Full Cone NAT ✅
  │
  ├─ 응답 없음
  │     │
  │     ▼
  │  Test I-2: STUN 서버 IP2:Port2로 Binding Request 전송
  │     │
  │     ▼
  │  MAPPED-ADDRESS가 Test I과 같은가?
  │     │
  │     ├─ 다름 → Symmetric NAT ❌
  │     │
  │     ├─ 같음
  │     │     │
  │     │     ▼
  │     │  Test III: 같은 IP, 다른 Port로 CHANGE-REQUEST
  │     │     │
  │     │     ├─ 응답 있음 → Restricted Cone NAT ✅
  │     │     └─ 응답 없음 → Port Restricted Cone NAT ✅
```

### 3.4 주요 공개 STUN 서버 목록

| 제공자 | 서버 주소 | 포트 | 비고 |
|--------|----------|------|------|
| Google | stun.l.google.com | 19302 | 가장 널리 사용 |
| Google | stun1.l.google.com | 19302 | 백업 |
| Google | stun2.l.google.com | 19302 | 백업 |
| Google | stun3.l.google.com | 19302 | 백업 |
| Google | stun4.l.google.com | 19302 | 백업 |
| Mozilla | stun.services.mozilla.com | 3478 | Firefox 내장 |
| Twilio | global.stun.twilio.com | 3478 | 상용 서비스 |
| Cloudflare | stun.cloudflare.com | 3478 | 2023년부터 제공 |

> **주의**: 공개 STUN 서버는 SLA가 없다. 상용 서비스에서는 자체 STUN 서버를 운영해야 한다.
> coturn(오픈소스)으로 STUN+TURN 서버를 함께 구축할 수 있다.

---

## 4. TURN 프로토콜 상세

### 4.1 개요 (RFC 5766 → RFC 8656)

**TURN** = **T**raversal **U**sing **R**elays around **N**AT

STUN이 "거울"이라면, TURN은 "우체국"이다. 직접 전달이 안 될 때, 중간에서 패킷을 릴레이해준다.

```
┌──────────┐         ┌──────────────┐         ┌──────────┐
│ Peer A   │         │  TURN Server │         │ Peer B   │
│ (NAT A)  │         │  (공인 IP)    │         │ (NAT B)  │
└────┬─────┘         └──────┬───────┘         └────┬─────┘
     │                      │                      │
     │  1. Allocate Req     │                      │
     │─────────────────────→│                      │
     │                      │                      │
     │  2. Allocate Resp    │                      │
     │  (Relayed Addr:      │                      │
     │   6.6.6.6:12345)     │                      │
     │←─────────────────────│                      │
     │                      │                      │
     │  3. "내 릴레이 주소는  │                      │
     │   6.6.6.6:12345야"   │  (시그널링 채널)      │
     │─────────────────────────────────────────────→│
     │                      │                      │
     │                      │  4. B → 6.6.6.6:12345│
     │                      │←─────────────────────│
     │                      │                      │
     │  5. TURN이 릴레이     │                      │
     │←─────────────────────│                      │
     │                      │                      │
     ▼  A ↔ B 간접 통신 성립  ▼                      ▼
```

### 4.2 주요 동작: Allocation, Permission, Channel Binding

#### Allocation (할당)

```
Client                           TURN Server
  │                                   │
  │  Allocate Request                 │
  │  (Lifetime: 600s)                │
  │──────────────────────────────────→│
  │                                   │
  │  401 Unauthorized                 │
  │  (nonce, realm)                   │
  │←──────────────────────────────────│
  │                                   │
  │  Allocate Request + Credentials   │
  │  (USERNAME, MESSAGE-INTEGRITY)    │
  │──────────────────────────────────→│
  │                                   │  서버가 릴레이 주소 할당:
  │  Allocate Success Response        │  6.6.6.6:12345
  │  (XOR-RELAYED-ADDRESS,            │
  │   XOR-MAPPED-ADDRESS,             │
  │   LIFETIME: 600)                  │
  │←──────────────────────────────────│
```

- Allocation은 기본 **10분**(600초) 유효
- Refresh Request로 갱신 가능
- 최대 동시 Allocation 수는 서버 설정에 따름

#### Permission (허가)

```
Client                           TURN Server
  │                                   │
  │  CreatePermission Request         │
  │  (XOR-PEER-ADDRESS: 2.2.2.2)     │
  │──────────────────────────────────→│
  │                                   │  "2.2.2.2에서 오는 패킷은
  │  CreatePermission Success         │   이 클라이언트에게 전달 허용"
  │←──────────────────────────────────│
```

- Permission은 **5분** 유효
- IP 주소 기반 (포트는 무시)
- Permission이 없으면 외부에서 온 패킷은 DROP

#### Channel Binding (채널 바인딩)

```
일반 Send/Data 방식:
┌──────────────────────────────────┐
│ STUN Header (20B) + Attributes   │  → 오버헤드 ~36바이트
│ + XOR-PEER-ADDRESS + DATA        │
└──────────────────────────────────┘

Channel Binding 방식:
┌──────────────────────────────────┐
│ Channel Number (2B) + Length (2B)│  → 오버헤드 단 4바이트!
│ + Application Data               │
└──────────────────────────────────┘
```

- 채널 번호(0x4000~0x7FFF)를 피어 주소에 바인딩
- 헤더 오버헤드가 36바이트 → 4바이트로 대폭 감소
- 게임처럼 빈번한 소규모 패킷에 유리
- Channel Binding은 **10분** 유효

### 4.3 비용 및 대역폭 이슈

| 항목 | STUN | TURN |
|------|------|------|
| 서버 부하 | 거의 없음 (요청-응답만) | 매우 높음 (모든 패킷 릴레이) |
| 대역폭 비용 | 무시 가능 | 전체 트래픽의 2배 (수신+발신) |
| 지연 시간 | 추가 없음 (직접 연결) | +20~100ms (릴레이 경유) |
| 월 비용 예시 | 무료~$5 | $50~$500+ (트래픽 비례) |
| 확장성 | 뛰어남 | 병목 가능 |

> **게임 개발자 팁**: TURN은 "최후의 수단"이다. 가능하면 STUN + Hole Punching으로
> 직접 연결을 시도하고, 실패 시에만 TURN으로 폴백하라. 이것이 ICE의 철학이다.

---

## 5. UDP Hole Punching 상세 메커니즘

### 5.1 단계별 동작 원리

```
    Peer A                Rendezvous Server              Peer B
  (NAT A 뒤)               (공인 서버)                (NAT B 뒤)
192.168.1.10:5000          5.5.5.5:3000              10.0.0.5:6000
      │                        │                          │
      │  ① 등록                 │                          │
      │  "나는 A, 게임방 참가"    │                          │
      │───────────────────────→│                          │
      │  NAT A 변환:            │                          │
      │  192.168.1.10:5000      │                          │
      │  → 1.1.1.1:8000        │                          │
      │                        │   ② 등록                  │
      │                        │   "나는 B, 게임방 참가"    │
      │                        │←─────────────────────────│
      │                        │  NAT B 변환:              │
      │                        │  10.0.0.5:6000            │
      │                        │  → 2.2.2.2:9000          │
      │                        │                          │
      │  ③ 서버가 양쪽에 상대방의 공인 주소를 알려줌           │
      │  "B는 2.2.2.2:9000"    │                          │
      │←───────────────────────│                          │
      │                        │  "A는 1.1.1.1:8000"      │
      │                        │─────────────────────────→│
      │                        │                          │
      │  ④ 동시에 서로에게 UDP 패킷 전송 (Hole Punch!)      │
      │                        │                          │
      │  A → 2.2.2.2:9000     │                          │
      │──────────────────────────────────────────────────→│
      │  (NAT A에 "2.2.2.2:9000 → 1.1.1.1:8000" 매핑 생성)│
      │                        │                          │
      │                        │    B → 1.1.1.1:8000      │
      │←──────────────────────────────────────────────────│
      │  (NAT B에 "1.1.1.1:8000 → 2.2.2.2:9000" 매핑 생성)│
      │                        │                          │
      │  ⑤ 양쪽 NAT에 매핑이 생겼으므로 직접 통신 가능!      │
      │                        │                          │
      │  A ←──── UDP ────→ B   │                          │
      │     직접 P2P 연결 성립!  │                          │
```

### 5.2 타이밍 이슈와 동시성

홀펀칭의 핵심은 **"거의 동시에"** 양쪽이 패킷을 보내는 것이다.

```
시나리오 1: 동시 전송 (성공) ✅

시간 ─→
A: ────[SEND]──────────────────[RECV]────  NAT A가 먼저 구멍을 뚫어놓음
B: ──────────[SEND]──────[RECV]──────────  NAT B도 구멍을 뚫어놓음
         ↑        ↑
      A 전송   B 전송
      (거의 동시)


시나리오 2: 시간차 큼 (실패 가능) ❌

시간 ─→
A: ────[SEND]─────────────────────────────[retry?]────
B: ──────────────────────────────[SEND]───────────────
         ↑                          ↑
      A 전송                     B 전송
      (너무 오래 후)

A의 패킷이 NAT B에 도착했을 때, B는 아직 A에게 패킷을 보내지 않았음
→ NAT B가 A의 패킷을 DROP
→ 이후 B가 보내도 NAT A의 매핑이 이미 만료되었을 수 있음
```

**실무 해결책**:
- Rendezvous 서버가 양쪽에 **동시에** "지금 보내라" 신호를 보냄
- 실패 시 **여러 번 재시도** (보통 3~5회, 간격 100~500ms)
- 첫 패킷은 DROP될 수 있으므로 **응답 확인** 후 연결 확립

### 5.3 NAT 매핑 유지 (Keepalive)

```
NAT 매핑의 수명 (일반적인 값):

┌──────────────────────────────────────────────────┐
│ UDP 매핑 유지 시간                                 │
│                                                  │
│ ├─ 가정용 공유기:     30초 ~ 5분                   │
│ ├─ 기업 방화벽:       1분 ~ 10분                   │
│ ├─ CGNAT:            30초 ~ 2분                   │
│ └─ 모바일 네트워크:   30초 ~ 1분 (매우 짧음!)       │
│                                                  │
│ RFC 4787 권장: 최소 2분                            │
└──────────────────────────────────────────────────┘

Keepalive 전략:

Peer A                                        Peer B
  │                                              │
  │  ──── Data Packet ────→                      │  일반 데이터
  │                                              │
  │  (20초 경과, 데이터 없음)                      │
  │                                              │
  │  ──── Keepalive Ping ────→                   │  빈 UDP 패킷
  │  ←── Keepalive Pong ─────                    │  또는 1바이트
  │                                              │
  │  (20초 경과)                                  │
  │                                              │
  │  ──── Keepalive Ping ────→                   │  반복
  │  ...                                         │
```

**Keepalive 구현 가이드**:

| 환경 | 권장 Keepalive 간격 | 이유 |
|------|-------------------|------|
| 가정용 Wi-Fi | 25초 | 일반 공유기 타임아웃 30초 대비 |
| 모바일 (LTE/5G) | 15초 | CGNAT 타임아웃이 매우 짧음 |
| 기업 네트워크 | 30초 | 비교적 긴 타임아웃 |
| 게임 (액션) | 불필요 | 게임 패킷 자체가 keepalive 역할 |

### 5.4 성공/실패 조건 정리

| 조건 | 결과 | 대안 |
|------|------|------|
| 양쪽 Cone NAT | ✅ 성공 | - |
| 한쪽 Symmetric + 한쪽 Full/Restricted Cone | ✅ 성공 | - |
| Port Restricted ↔ Symmetric | ❌ 실패 | TURN |
| Symmetric ↔ Symmetric | ❌ 실패 | TURN |
| 방화벽이 UDP 완전 차단 | ❌ 실패 | TURN over TCP/TLS |
| CGNAT 이중 NAT | ⚠️ 불안정 | TURN 권장 |
| NAT 매핑 만료 | ❌ 실패 | Keepalive 강화 |
| 포트 예측 가능한 Symmetric NAT | ⚠️ 가능 | 포트 예측 알고리즘 |

---

## 6. TCP Hole Punching

### 6.1 UDP와의 차이점

| 특성 | UDP Hole Punching | TCP Hole Punching |
|------|------------------|------------------|
| 연결 방식 | 비연결 (데이터그램) | 연결 지향 (3-way handshake) |
| 성공률 | ~82-95% | ~60-64% |
| 구현 복잡도 | 낮음 | 높음 |
| NAT 호환성 | 대부분 | 제한적 |
| 소켓 옵션 | 특별한 설정 불필요 | SO_REUSEADDR 필요 |
| 타이밍 민감도 | 보통 | 매우 높음 |

### 6.2 TCP Simultaneous Open

TCP의 유일한 홀펀칭 방법은 **Simultaneous Open** (동시 열기)이다.

```
정상 TCP 연결 (Client → Server):

Client                          Server
  │  SYN ───────────────────→     │
  │  ←─────────────── SYN+ACK    │
  │  ACK ───────────────────→     │
  │  [ESTABLISHED]                │


TCP Simultaneous Open (양쪽이 동시에 SYN):

Peer A                          Peer B
  │                                │
  │  SYN ──────────────────→       │  A가 SYN 보냄
  │       ←────────────────── SYN  │  B도 SYN 보냄 (거의 동시!)
  │                                │
  │  SYN+ACK ──────────────→       │  A가 B의 SYN에 대해 SYN+ACK
  │       ←────────────── SYN+ACK  │  B가 A의 SYN에 대해 SYN+ACK
  │                                │
  │  [ESTABLISHED]  ←──→  [ESTABLISHED]
```

**핵심 요구사항**:
1. 양쪽이 **같은 소스 포트**를 사용해야 함 (`SO_REUSEADDR` + `SO_REUSEPORT`)
2. SYN 패킷이 **거의 동시에** 도착해야 함 (수 ms 이내)
3. NAT가 TCP Simultaneous Open을 **지원**해야 함

### 6.3 실무에서 잘 안 쓰이는 이유

```
TCP Hole Punching이 어려운 이유들:

1. NAT 호환성 문제
   ┌─────────────────────────────────────────────┐
   │ 많은 NAT 장비가 TCP에 대해 Symmetric 매핑을  │
   │ 강제한다 (UDP는 Cone이더라도).                │
   │ → UDP에서 성공해도 TCP에서는 실패             │
   └─────────────────────────────────────────────┘

2. OS / 방화벽 차단
   ┌─────────────────────────────────────────────┐
   │ 일부 OS와 방화벽은 들어오는 SYN 패킷을        │
   │ 무조건 차단한다 (SYN-SENT 상태의 소켓에       │
   │ 들어오는 SYN을 거부).                        │
   └─────────────────────────────────────────────┘

3. 타이밍 극도로 민감
   ┌─────────────────────────────────────────────┐
   │ UDP: 패킷이 몇 초 차이나도 OK                │
   │ TCP: SYN이 거의 동시에 도착해야 함            │
   │     → 인터넷 지연 변동(jitter)에 취약         │
   └─────────────────────────────────────────────┘

4. 포트 재사용 문제
   ┌─────────────────────────────────────────────┐
   │ SO_REUSEADDR 사용 시 보안 위험               │
   │ TCP TIME_WAIT 상태의 소켓과 충돌 가능         │
   │ RFC 6888: CGNAT은 포트 랜덤화 필수           │
   └─────────────────────────────────────────────┘
```

**결론**: 실무에서는 거의 항상 UDP Hole Punching을 사용하고, TCP가 필요한 경우 TURN over TCP로 릴레이한다. libp2p가 TCP Hole Punching을 구현한 거의 유일한 대규모 프로젝트이다.

---

## 7. ICE (Interactive Connectivity Establishment)

### 7.1 개요 (RFC 8445)

ICE는 STUN과 TURN을 조합하여 **최적의 연결 경로를 자동으로 찾아주는 프레임워크**이다.

> 게임 개발자 비유: ICE는 "매치메이킹의 네트워크 버전"이다.
> 가능한 모든 연결 방법을 시도해보고, 가장 빠르고 안정적인 것을 선택한다.

```
ICE의 목표:

  우선순위 1: 직접 연결 (host candidate)          ← 최고 품질
  우선순위 2: STUN 경유 연결 (server reflexive)    ← 좋은 품질
  우선순위 3: TURN 릴레이 연결 (relay)             ← 최후의 수단

  ┌─────────────────────────────────────────┐
  │ "될 수 있으면 직접, 안 되면 릴레이로"      │
  │  → 비용과 품질의 최적 균형                 │
  └─────────────────────────────────────────┘
```

### 7.2 Candidate 수집 (Gathering)

```
ICE Agent가 수집하는 Candidate 유형:

1. Host Candidate (호스트 후보)
   ┌──────────────────────────────────────┐
   │ 로컬 네트워크 인터페이스의 IP:Port     │
   │ 예: 192.168.1.10:5000                │
   │ → 같은 LAN에 있으면 이것만으로 연결    │
   └──────────────────────────────────────┘

2. Server Reflexive Candidate (서버 반사 후보, srflx)
   ┌──────────────────────────────────────┐
   │ STUN 서버를 통해 알아낸 공인 IP:Port   │
   │ 예: 1.1.1.1:8000                     │
   │ → NAT 뒤에서 홀펀칭에 사용            │
   └──────────────────────────────────────┘

3. Relay Candidate (릴레이 후보)
   ┌──────────────────────────────────────┐
   │ TURN 서버가 할당한 릴레이 IP:Port      │
   │ 예: 6.6.6.6:12345                    │
   │ → 홀펀칭 실패 시 최후의 수단           │
   └──────────────────────────────────────┘

4. Peer Reflexive Candidate (피어 반사 후보, prflx)
   ┌──────────────────────────────────────┐
   │ Connectivity Check 중 발견되는 후보    │
   │ 상대방이 보낸 패킷의 소스 주소         │
   │ → 예상치 못한 경로 발견 시             │
   └──────────────────────────────────────┘
```

### 7.3 Connectivity Check 과정

```
Peer A                                              Peer B
  │                                                    │
  │  1. Candidate 수집                                  │
  │  [host: 192.168.1.10:5000]                         │
  │  [srflx: 1.1.1.1:8000]                            │
  │  [relay: 6.6.6.6:12345]                            │
  │                                                    │
  │  ◄──── 시그널링 채널로 Candidate 교환 ────►         │
  │                                                    │
  │                                   [host: 10.0.0.5:6000]
  │                                   [srflx: 2.2.2.2:9000]
  │                                   [relay: 7.7.7.7:54321]
  │                                                    │
  │  2. Candidate Pair 생성 (3 x 3 = 9개 조합)         │
  │                                                    │
  │  3. 우선순위 순으로 Connectivity Check 실행         │
  │                                                    │
  │  [Check 1] host ↔ host (같은 LAN?)                │
  │  A:192.168.1.10:5000 → B:10.0.0.5:6000           │
  │──────────── STUN Binding Request ────────────────→ │
  │  (다른 서브넷이면 실패)                              │
  │                                                    │
  │  [Check 2] srflx ↔ srflx (홀펀칭 시도)            │
  │  A:1.1.1.1:8000 → B:2.2.2.2:9000                 │
  │──────────── STUN Binding Request ────────────────→ │
  │←─────────── STUN Binding Response ────────────────│
  │  ✅ 성공! 이 경로를 선택                            │
  │                                                    │
  │  [Check 3~9] 나머지는 생략 또는 백업으로 유지         │
  │                                                    │
  │  4. 선택된 Candidate Pair로 미디어/데이터 전송       │
  │  A ←────────── Direct P2P ──────────→ B            │
```

### 7.4 ICE-LITE vs Full ICE

| 특성 | Full ICE | ICE-LITE |
|------|----------|----------|
| Candidate 수집 | host + srflx + relay | host만 |
| Connectivity Check | 양방향 실행 | 응답만 (능동적 체크 안 함) |
| NAT 지원 | NAT 뒤 장비 가능 | 공인 IP 장비만 가능 |
| 구현 복잡도 | 높음 | 낮음 |
| 사용 사례 | 일반 클라이언트 | SFU/미디어 서버 |

```
Full ICE:
  Client A ←──── Check ────→ Client B
  (양쪽 모두 능동적으로 연결 시도)

ICE-LITE:
  Client A ────── Check ────→ Server (공인 IP)
  (서버는 응답만, 클라이언트가 주도)

  → WebRTC SFU 서버는 공인 IP에 있으므로 ICE-LITE로 충분
  → 클라이언트 간 P2P라면 Full ICE 필요
```

---

## 8. 실제 활용 사례

### 8.1 WebRTC에서의 NAT Traversal

```
WebRTC 연결 수립 흐름:

Browser A                Signaling Server             Browser B
    │                         │                          │
    │  1. createOffer()       │                          │
    │  (SDP + ICE candidates) │                          │
    │────────────────────────→│                          │
    │                         │─────────────────────────→│
    │                         │                          │
    │                         │  2. createAnswer()       │
    │                         │  (SDP + ICE candidates)  │
    │                         │←─────────────────────────│
    │←────────────────────────│                          │
    │                         │                          │
    │  3. ICE Connectivity Checks (STUN Binding)        │
    │←─────────────────────────────────────────────────→│
    │                         │                          │
    │  4. DTLS Handshake (암호화)                        │
    │←─────────────────────────────────────────────────→│
    │                         │                          │
    │  5. SRTP 미디어 스트림 (직접 P2P)                  │
    │←════════════════════════════════════════════════→  │
    │         (또는 TURN 릴레이 경유)                     │
```

**WebRTC의 NAT Traversal 전략**:
- ICE를 기본 프레임워크로 사용
- Trickle ICE: Candidate를 발견하는 대로 즉시 전송 (대기 시간 단축)
- Offferer/Answerer 모델로 역할 분담
- 통계적으로 약 86%가 직접 연결, 14%가 TURN 릴레이 사용

### 8.2 게임 네트워킹 (P2P 매치메이킹)

```
게임 P2P 네트워킹 아키텍처:

┌──────────────────────────────────────────────┐
│                매치메이킹 서버                  │
│  (로비, 방 관리, NAT 정보 교환)                │
└──────────┬───────────────────┬───────────────┘
           │                   │
           ▼                   ▼
     ┌──────────┐        ┌──────────┐
     │ Player A │◄──────►│ Player B │   직접 P2P
     │ (Host)   │ UDP    │ (Guest)  │   (홀펀칭 성공 시)
     └──────────┘        └──────────┘
                    또는
     ┌──────────┐  ┌──────────┐  ┌──────────┐
     │ Player A │─→│ 릴레이    │←─│ Player B │   릴레이
     └──────────┘  │ 서버     │  └──────────┘   (홀펀칭 실패 시)
                   └──────────┘
```

**게임에서의 구현 패턴**:

1. **로비 단계**: 매치메이킹 서버에 연결, STUN으로 공인 주소 확인
2. **매칭 완료**: 서버가 양쪽에 상대방의 공인 주소 전달
3. **홀펀칭 시도**: 양쪽이 동시에 UDP 패킷 전송 (3~5회 재시도)
4. **연결 확립**: 성공 시 직접 P2P, 실패 시 릴레이 서버 경유
5. **게임 중**: UDP 기반 게임 상태 동기화 (커스텀 프로토콜 또는 ENet, RakNet 등)

**대표적인 게임 네트워킹 라이브러리**:

| 라이브러리 | NAT Traversal 지원 | 특징 |
|-----------|-------------------|------|
| Steam Networking (Valve) | 자체 릴레이 네트워크 | Steam Datagram Relay (SDR) |
| Epic Online Services | STUN + TURN | EOS P2P Interface |
| Unity Netcode + Relay | Unity Relay 서비스 | 클라우드 릴레이 기본 |
| Photon | 릴레이 기본, P2P 옵션 | 매니지드 서비스 |
| RakNet (오픈소스) | NATPunchthrough 내장 | 클래식 P2P 라이브러리 |
| ENet | 없음 (직접 구현 필요) | 경량 UDP 라이브러리 |

### 8.3 IoT 디바이스 원격 접속

```
IoT NAT Traversal 과제:

┌─────────┐      ┌─────────┐      ┌─────────┐
│ 스마트폰  │      │ Cloud   │      │ IoT     │
│ (외부)   │─────→│ Server  │←─────│ (NAT뒤) │
└─────────┘      └─────────┘      └─────────┘
                       │
    문제: IoT 디바이스는 저전력이라
    - Keepalive 빈번하게 보내기 어려움
    - TURN 서버 비용 부담
    - 수천~수만 대 동시 접속

해결 전략:
  1. MQTT/WebSocket으로 클라우드 경유 (가장 흔함)
  2. Tailscale/ZeroTier 같은 VPN 메시 네트워크
  3. IPv6 + 직접 접속 (CGNAT 회피)
```

### 8.4 VPN에서의 활용 (WireGuard, Tailscale)

#### WireGuard의 NAT Traversal

```
WireGuard 피어 간 연결:

Peer A                                    Peer B
  │                                          │
  │  WireGuard는 기본적으로                    │
  │  Endpoint(공인IP:Port)를 설정 파일에 지정   │
  │                                          │
  │  PersistentKeepalive = 25               │
  │  (25초마다 keepalive → NAT 매핑 유지)     │
  │                                          │
  │  ──── Encrypted UDP ────→                │
  │  ←── Encrypted UDP ─────                 │
  │                                          │
  │  양쪽 모두 NAT 뒤라면?                     │
  │  → WireGuard 자체는 홀펀칭 미지원          │
  │  → 수동 포트포워딩 또는 외부 도구 필요      │
```

#### Tailscale의 NAT Traversal (DERP)

```
Tailscale의 3단계 연결 전략:

1단계: DERP 릴레이 (즉시 연결)
  ┌──────┐     ┌──────────┐     ┌──────┐
  │Node A│────→│DERP 서버  │←────│Node B│
  └──────┘     │(HTTPS)   │     └──────┘
               └──────────┘
  → 연결 지연 없이 즉시 통신 가능
  → 모든 트래픽은 WireGuard 암호화 (DERP는 내용 못 봄)

2단계: 직접 연결 시도 (홀펀칭)
  ┌──────┐                      ┌──────┐
  │Node A│←───── Direct UDP ──→ │Node B│
  └──────┘    (WireGuard)       └──────┘
  → DISCO 프로토콜로 NAT 탐색 + 홀펀칭
  → 성공 시 DERP 릴레이 종료, 직접 통신으로 전환

3단계: 피어 릴레이 (2025년 도입)
  ┌──────┐     ┌──────────┐     ┌──────┐
  │Node A│────→│다른 Peer  │←────│Node B│
  └──────┘     │(릴레이)   │     └──────┘
  → 직접 연결 실패 시, 네트워크 내 다른 피어를 릴레이로 활용
  → DERP보다 가까운 경로 가능
```

**Tailscale vs 기존 VPN의 NAT Traversal 비교**:

| 특성 | OpenVPN | WireGuard (단독) | Tailscale |
|------|---------|-----------------|-----------|
| NAT Traversal | 중앙 서버 경유 | 수동 설정 | 자동 (DERP + 홀펀칭) |
| P2P 직접 연결 | 불가 | 가능 (설정 필요) | 자동 시도 |
| 이중 NAT | 어려움 | 어려움 | DERP로 해결 |
| 모바일 지원 | 재연결 느림 | 빠름 | 매우 빠름 |

---

## 9. Carrier-Grade NAT (CGNAT) 문제

### 9.1 CGNAT이란?

```
일반 NAT (단일):

사설 네트워크         NAT            인터넷
192.168.x.x  ──→  공인 IP  ──→  외부 서버


CGNAT (이중 NAT / NAT444):

사설 네트워크     고객 NAT      ISP CGNAT        인터넷
192.168.x.x  ──→ 100.64.x.x ──→ 공인 IP ──→  외부 서버
(사설 IP)     (Shared Address   (ISP의 공인 IP
               Space RFC 6598)   수백~수천 가구 공유)

→ NAT 두 겹을 뚫어야 하므로 홀펀칭 성공률 급감!
```

### 9.2 CGNAT의 주요 문제점

| 문제 | 영향 | 심각도 |
|------|------|--------|
| 이중 NAT 매핑 | 홀펀칭 성공률 50% 이하로 하락 | 높음 |
| 포트 공유 | 한 공인 IP의 65535 포트를 수백 가구가 공유 | 높음 |
| 매핑 만료 빠름 | ISP가 리소스 절약 위해 30초~2분으로 설정 | 중간 |
| 포트포워딩 불가 | UPnP가 고객 NAT만 제어, CGNAT은 제어 불가 | 높음 |
| IP 기반 차단 | 한 사용자 악용 시 같은 공인 IP 전체 차단 | 높음 |

### 9.3 모바일 네트워크의 CGNAT

```
모바일 네트워크 NAT 구조:

스마트폰           기지국           PGW/CGNAT        인터넷
(10.x.x.x)  ──→  (내부망)  ──→  (공인 IP 풀)  ──→  외부
                                   │
                                   ├─ 수만 명이 같은 IP 공유
                                   ├─ Symmetric NAT 동작 흔함
                                   └─ UDP 타임아웃 30초~1분

실측 데이터 (2025년 기준):
  - 한국 LTE/5G: 대부분 CGNAT, Symmetric NAT 동작
  - 미국 T-Mobile: CGNAT + IPv6 듀얼스택
  - 일본 docomo: IPv6 우선, IPv4는 CGNAT
```

### 9.4 CGNAT 환경에서의 대응 전략

1. **TURN 릴레이 필수 준비**: CGNAT 환경에서는 직접 연결 실패 확률이 높으므로 TURN 서버를 반드시 준비
2. **IPv6 우선**: 가능하면 IPv6로 직접 연결 (CGNAT 우회)
3. **QUIC 프로토콜**: UDP 기반이면서 TCP의 안정성 → 일부 CGNAT에서 유리
4. **VPN 메시 네트워크**: Tailscale, ZeroTier 등으로 CGNAT 투과

---

## 10. IPv6와 NAT Traversal의 미래

### 10.1 IPv6에서는 NAT가 필요 없다?

```
IPv4 세계:                          IPv6 세계:

192.168.1.10 ──→ NAT ──→ 인터넷    2001:db8::1 ──────────→ 인터넷
(사설 IP)        (변환)             (글로벌 유니크 주소)

→ NAT 없이 End-to-End 직접 통신 가능!
→ 홀펀칭 자체가 불필요!
```

**하지만 현실은...**

| 요소 | 현실 |
|------|------|
| IPv6 보급률 | 전 세계 ~45% (2025년), 한국 ~15% |
| 방화벽 | IPv6에서도 방화벽은 존재 → 인바운드 차단 |
| 듀얼스택 | IPv4/IPv6 동시 운영 → NAT traversal 여전히 필요 |
| 전환 기간 | 완전 IPv6 전환은 2030년 이후 예상 |

### 10.2 Happy Eyeballs (RFC 8305)

```
IPv4/IPv6 동시 시도 알고리즘:

Client
  │
  ├─→ IPv6 연결 시도 (먼저)
  │     └─ 250ms 내 성공? → IPv6 사용 ✅
  │     └─ 250ms 내 실패? → 아래로
  │
  └─→ IPv4 연결 시도 (폴백)
        └─ 성공? → IPv4 사용 (NAT traversal 필요)
        └─ 실패? → 연결 불가

→ 사용자 입장에서 투명하게 최적 프로토콜 선택
```

### 10.3 미래 전망

| 시기 | 예상 변화 |
|------|----------|
| 현재 (2026) | IPv4 + CGNAT 주류, TURN 의존도 높음 |
| 2027~2028 | IPv6 보급 50% 돌파, NAT traversal 필요성 감소 시작 |
| 2030+ | IPv6 기본, NAT traversal은 레거시 환경에서만 |
| 장기 | QUIC + IPv6로 P2P 연결 단순화 |

---

## 11. 비교 대상 기술/프로토콜

### 11.1 UPnP / NAT-PMP / PCP 비교

| 특성 | UPnP IGD | NAT-PMP | PCP |
|------|----------|---------|-----|
| 표준 | UPnP Forum | RFC 6886 | RFC 6887 |
| 프로토콜 | HTTP/SOAP | UDP | UDP |
| 복잡도 | 높음 | 낮음 | 중간 |
| 보안 | 취약 (인증 없음) | 제한적 | EAP 인증 옵션 |
| IPv6 | 미지원 | 미지원 | 지원 |
| CGNAT 통과 | 불가 | 불가 | 가능 (설계상) |
| 구현 크기 | 수천 줄 | 수백 줄 | 수백 줄 |
| 도입 연도 | 2001 | 2005 (Apple) | 2013 |
| 주요 사용처 | 가정용 공유기 | macOS/iOS | 차세대 라우터 |

**동작 원리**:

```
UPnP / NAT-PMP / PCP 공통 개념:

Application                    NAT Router
    │                              │
    │  "포트 8080을 열어줘"          │
    │─────────────────────────────→│
    │                              │  외부:1234 → 내부:8080 매핑 생성
    │  "OK, 외부 포트 1234 할당"    │
    │←─────────────────────────────│
    │                              │

핵심 한계: NAT 라우터가 같은 LAN에 있어야만 동작
→ CGNAT처럼 ISP 장비에는 명령을 보낼 수 없음
```

### 11.2 STUN vs TURN vs ICE 비교표

| 특성 | STUN | TURN | ICE |
|------|------|------|-----|
| 역할 | 공인 주소 발견 | 패킷 릴레이 | 연결 방법 선택 프레임워크 |
| RFC | 5389 / 8489 | 5766 / 8656 | 8445 |
| 서버 부하 | 매우 낮음 | 높음 | STUN+TURN 합산 |
| 대역폭 비용 | 거의 없음 | 전체 트래픽 릴레이 | 가변적 |
| 직접 연결 | 지원 (홀펀칭 보조) | 미지원 (항상 릴레이) | 최적 경로 자동 선택 |
| Symmetric NAT | 주소 발견만 가능 | 완벽 지원 | TURN 폴백으로 지원 |
| 단독 사용 | 가능 (제한적) | 가능 | STUN+TURN 필요 |
| 게임 사용 | 주소 발견용 | 폴백 릴레이 | WebRTC 기반 게임 |
| 지연 시간 | 추가 없음 | +20~100ms | 최적 경로 선택 |

```
STUN, TURN, ICE의 관계:

┌─────────────────────────────────────────┐
│                  ICE                     │
│  ┌──────────┐       ┌──────────┐       │
│  │   STUN   │       │   TURN   │       │
│  │ (도구1)   │       │ (도구2)   │       │
│  └──────────┘       └──────────┘       │
│                                         │
│  ICE = STUN + TURN을 조합하는 전략 엔진   │
│  STUN = 주소 발견 + 연결 확인 도구        │
│  TURN = 릴레이 (최후의 수단) 도구         │
└─────────────────────────────────────────┘
```

### 11.3 libp2p (IPFS에서 사용하는 P2P 라이브러리)

```
libp2p의 NAT Traversal 스택:

┌──────────────────────────────────────┐
│           libp2p Application          │
├──────────────────────────────────────┤
│  DCUtR (Direct Connection Upgrade    │  ← 홀펀칭 조율
│         through Relay)               │
├──────────────────────────────────────┤
│  Circuit Relay v2                    │  ← TURN과 유사한 릴레이
├──────────────────────────────────────┤
│  AutoNAT                             │  ← STUN과 유사한 NAT 감지
├──────────────────────────────────────┤
│  Identify Protocol                   │  ← 피어 정보 교환
├──────────────────────────────────────┤
│  Transport (TCP, QUIC, WebTransport) │
└──────────────────────────────────────┘
```

**libp2p vs 전통적 STUN/TURN/ICE 비교**:

| 특성 | STUN/TURN/ICE | libp2p |
|------|--------------|--------|
| 중앙 서버 | STUN/TURN 서버 필요 | 탈중앙화 (DHT 기반) |
| 릴레이 | TURN 서버 (중앙) | Circuit Relay (아무 피어) |
| NAT 감지 | STUN 서버 | AutoNAT (다른 피어에게 요청) |
| 홀펀칭 성공률 | ~82-95% (UDP) | ~70% (DCUtR, 2024 측정) |
| 프로토콜 | UDP 중심 | TCP, QUIC, WebTransport 등 |
| 사용 사례 | WebRTC, VoIP, 게임 | IPFS, Filecoin, Ethereum |

---

## 12. 참고 자료

### RFC 문서

| RFC | 제목 | 연도 |
|-----|------|------|
| [RFC 3489](https://datatracker.ietf.org/doc/html/rfc3489) | STUN - Simple Traversal of UDP through NATs (구 버전) | 2003 |
| [RFC 4787](https://datatracker.ietf.org/doc/html/rfc4787) | NAT Behavioral Requirements for Unicast UDP | 2007 |
| [RFC 5389](https://datatracker.ietf.org/doc/html/rfc5389) | Session Traversal Utilities for NAT (STUN) | 2008 |
| [RFC 5766](https://datatracker.ietf.org/doc/html/rfc5766) | TURN: Relay Extensions to STUN | 2010 |
| [RFC 5780](https://datatracker.ietf.org/doc/html/rfc5780) | NAT Behavior Discovery Using STUN | 2010 |
| [RFC 6062](https://datatracker.ietf.org/doc/html/rfc6062) | TURN Extensions for TCP Allocations | 2010 |
| [RFC 6886](https://datatracker.ietf.org/doc/html/rfc6886) | NAT Port Mapping Protocol (NAT-PMP) | 2013 |
| [RFC 6887](https://datatracker.ietf.org/doc/html/rfc6887) | Port Control Protocol (PCP) | 2013 |
| [RFC 6888](https://datatracker.ietf.org/doc/html/rfc6888) | Common Requirements for CGNAT | 2013 |
| [RFC 8305](https://datatracker.ietf.org/doc/html/rfc8305) | Happy Eyeballs v2 | 2017 |
| [RFC 8445](https://datatracker.ietf.org/doc/html/rfc8445) | ICE: NAT Traversal Protocol | 2018 |
| [RFC 8489](https://datatracker.ietf.org/doc/html/rfc8489) | STUN (RFC 5389 개정) | 2020 |
| [RFC 8656](https://datatracker.ietf.org/doc/html/rfc8656) | TURN (RFC 5766 개정) | 2020 |

### 핵심 논문 및 기술 블로그

| 자료 | URL |
|------|-----|
| Peer-to-Peer Communication Across NATs (Ford, Srisuresh, Kegel, 2005) | [bford.info/pub/net/p2pnat](https://bford.info/pub/net/p2pnat/) |
| How NAT Traversal Works (Tailscale, 2020) | [tailscale.com/blog/how-nat-traversal-works](https://tailscale.com/blog/how-nat-traversal-works) |
| Decentralized Hole Punching (Protocol Labs, 2022) | [research.protocol.ai/publications/decentralized-hole-punching](https://research.protocol.ai/publications/decentralized-hole-punching/seemann2022.pdf) |
| libp2p Hole Punching Specification | [docs.libp2p.io/concepts/nat/hole-punching](https://docs.libp2p.io/concepts/nat/hole-punching/) |
| NAT Types and NAT Traversal (Kurento Docs) | [doc-kurento.readthedocs.io](https://doc-kurento.readthedocs.io/en/latest/knowledge/nat.html) |
| WebRTC ICE Guide (VideoSDK) | [videosdk.live/developer-hub/webrtc/webrtc-ice](https://videosdk.live/developer-hub/webrtc/webrtc-ice) |
| Tailscale NAT Traversal Improvements | [tailscale.com/blog/nat-traversal-improvements-pt-1](https://tailscale.com/blog/nat-traversal-improvements-pt-1) |
| Tailscale DERP Servers | [tailscale.com/docs/reference/derp-servers](https://tailscale.com/docs/reference/derp-servers) |
| Large-Scale NAT Traversal Measurement (arXiv, 2025) | [arxiv.org/html/2510.27500v1](https://arxiv.org/html/2510.27500v1) |

### 오픈소스 구현체

| 프로젝트 | 설명 | URL |
|---------|------|-----|
| coturn | STUN + TURN 서버 (C) | [github.com/coturn/coturn](https://github.com/coturn/coturn) |
| Pion (Go) | WebRTC + ICE + STUN + TURN | [github.com/pion/webrtc](https://github.com/pion/webrtc) |
| libp2p | 탈중앙 P2P 라이브러리 | [github.com/libp2p](https://github.com/libp2p) |
| Tailscale | WireGuard 기반 VPN 메시 | [github.com/tailscale/tailscale](https://github.com/tailscale/tailscale) |
| ZeroTier | P2P VPN 네트워크 | [github.com/zerotier/ZeroTierOne](https://github.com/zerotier/ZeroTierOne) |
| stunner | Kubernetes용 STUN/TURN | [github.com/l7mp/stunner](https://github.com/l7mp/stunner) |

---

> **마무리**: NAT Traversal은 "완벽한 솔루션"이 없는 분야다.
> Full Cone NAT끼리는 쉽게 뚫리지만, Symmetric NAT + CGNAT 조합이면 TURN 릴레이가 필수다.
> 실무에서는 ICE 프레임워크를 사용하여 "될 수 있으면 직접, 안 되면 릴레이"라는 전략을 취하는 것이 정석이다.
> IPv6가 보편화되면 NAT 자체가 사라지겠지만, 그때까지는 이 기술들이 P2P 통신의 핵심이다.
