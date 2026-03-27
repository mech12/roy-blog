# WireGuard 심화 가이드

> 다른 분야 시니어 엔지니어를 위한 핵심 용어 해설 포함

---

## 1. WireGuard 개요 및 탄생 배경

### WireGuard란?

**한 줄 요약**: Linux 커널에 내장된 차세대 VPN 프로토콜. 약 4,000줄의 코드로 IPsec/OpenVPN을 대체한다.

WireGuard는 Layer 3 네트워크 터널 프로토콜로, UDP 위에서 동작하며 IPv4/IPv6를 모두 지원한다. SSH의 authorized_keys처럼 공개 키 기반 인증을 사용하며, 커널 공간에서 동작하여 높은 성능을 보장한다.

### 탄생 배경: Jason A. Donenfeld는 왜 만들었나?

Jason A. Donenfeld(온라인 닉네임 zx2c4)는 Columbia College에서 수학 및 철학을 전공한 뒤, 2012년 파리에서 **취약점 연구원(vulnerability researcher)**으로 활동했다.

그가 WireGuard를 만든 배경에는 두 가지 동기가 있다:

1. **기존 VPN의 압도적 복잡성**: IPsec과 OpenVPN을 사용하면서 설정이 "압도적으로 어렵다(overwhelmingly difficult)"고 느꼈다. IPsec의 경우 IKEv1/IKEv2, ESP, AH 등 여러 RFC에 걸친 프로토콜 스위트를 이해해야 하고, OpenVPN은 수십만 줄의 유저스페이스 코드에 TLS 설정이 복잡하다.

2. **커널 루트킷 연구에서의 영감**: 보안 연구 과정에서 커널 루트킷을 작성하며 "은밀하고 안전한 네트워크 터널"의 필요성을 절감했고, 이 설계 요구사항이 WireGuard의 기초가 되었다.

> "WireGuard actually worked, though he didn't really intend to do that when he began -- he just wanted the thing to exist because he needed it."

### 주요 이정표

| 시기 | 사건 |
|------|------|
| 2015 | WireGuard 최초 공개 |
| 2017 | FOSDEM 발표, 보안 감사 시작 |
| 2018 | Linus Torvalds가 "작품(work of art)"이라 칭찬 |
| 2020.03 | **Linux 5.6 커널에 공식 편입** |
| 2020~ | Windows, macOS, Android, iOS 등 크로스 플랫폼 지원 확대 |

---

## 2. 핵심 아키텍처

### 2.1 Linux 커널 모듈 구조

WireGuard는 커널 모듈(kernel module)로 구현된다. 이것이 OpenVPN(유저스페이스)과의 근본적인 차이다.

```
┌─────────────────────────────────────────────────────┐
│                    User Space                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ wg 도구   │  │ wg-quick │  │ 네트워크 앱       │  │
│  │ (설정)    │  │ (래퍼)   │  │ (curl, ssh 등)   │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       │              │                 │             │
├───────┼──────────────┼─────────────────┼─────────────┤
│       │         Kernel Space           │             │
│       v              v                 v             │
│  ┌──────────────────────────────────────────────┐   │
│  │           Netlink Interface                   │   │
│  └──────────────────┬───────────────────────────┘   │
│                     v                                │
│  ┌──────────────────────────────────────────────┐   │
│  │         WireGuard Kernel Module (~4,000 LoC)  │   │
│  │  ┌────────────┐ ┌───────────┐ ┌───────────┐  │   │
│  │  │ Noise IK   │ │ Cryptokey │ │ Timer     │  │   │
│  │  │ Handshake  │ │ Routing   │ │ State     │  │   │
│  │  │ Engine     │ │ Table     │ │ Machine   │  │   │
│  │  └────────────┘ └───────────┘ └───────────┘  │   │
│  └──────────────────┬───────────────────────────┘   │
│                     v                                │
│  ┌──────────────────────────────────────────────┐   │
│  │        Linux Networking Stack (Netfilter)      │   │
│  │        wg0 가상 네트워크 인터페이스              │   │
│  └──────────────────┬───────────────────────────┘   │
│                     v                                │
│  ┌──────────────────────────────────────────────┐   │
│  │        물리 NIC (eth0, wlan0 등)              │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**핵심 용어 해설**:
- **커널 모듈**: OS 핵심부에서 직접 실행되는 코드. 유저스페이스 대비 컨텍스트 스위칭 오버헤드가 없어 빠르다.
- **Netlink**: 커널과 유저스페이스 사이의 IPC(프로세스 간 통신) 메커니즘.
- **wg0**: WireGuard가 생성하는 가상 네트워크 인터페이스. eth0처럼 IP를 할당받고 라우팅 테이블에 등록된다.

### 2.2 Noise Protocol Framework (IK Handshake)

WireGuard는 Noise Protocol Framework의 **Noise_IK** 패턴을 사용한다. Noise는 TLS를 대체할 수 있는 현대적 핸드셰이크 프레임워크로, CurveCP, NaCL, SIGMA 등의 선행 연구를 기반으로 한다.

**핵심 용어 해설**:
- **Noise Protocol**: Trevor Perrin이 설계한 핸드셰이크 프레임워크. TLS보다 단순하면서도 수학적으로 검증 가능한 보안 속성을 제공한다.
- **IK 패턴**: Initiator가 Responder의 static public key를 이미 알고 있는 상황에서의 핸드셰이크 패턴. "I"는 Initiator의 static key가 전송됨을, "K"는 Responder의 static key가 사전에 알려져 있음을 의미한다.
- **PFS (Perfect Forward Secrecy)**: 장기 키가 유출되어도 과거 세션 데이터를 복호화할 수 없는 속성.

```
Noise_IK 핸드셰이크 흐름 (1-RTT):

  Initiator (클라이언트)                    Responder (서버)
  ========================                ========================
  알고 있음: S_resp_pub                    알고 있음: 자신의 키 쌍

  1) 임시 키 쌍(E_init) 생성
  2) DH(E_init, S_resp_pub) → 공유 비밀 도출
  3) S_init_pub 암호화

  ── Message 1 ──────────────────────────→
  │ E_init_pub (평문)                      │
  │ Enc(S_init_pub)  (암호화된 공개키)      │
  │ Enc(timestamp)   (암호화된 타임스탬프)   │
  │ MAC1, MAC2       (인증 태그)           │
                                          4) 임시 키 쌍(E_resp) 생성
                                          5) DH(E_resp, E_init) 수행
                                          6) DH(E_resp, S_init) 수행
                                          7) 세션 키 도출

  ←── Message 2 ─────────────────────────
  │ E_resp_pub (평문)                      │
  │ Enc(empty)       (암호화된 빈 페이로드)  │
  │ MAC1, MAC2       (인증 태그)           │

  양측: 최종 세션 키(송신용/수신용) 도출
  ── 암호화된 데이터 터널 시작 ──→
```

**DH(Diffie-Hellman) 연산 조합**:

| 단계 | 연산 | 목적 |
|------|------|------|
| 1 | DH(E_init, S_resp) | Responder 인증 |
| 2 | DH(S_init, E_resp) | Initiator 인증 |
| 3 | DH(E_init, E_resp) | Forward Secrecy 보장 |

총 3~4회의 DH 연산으로 상호 인증 + PFS를 동시에 달성한다. 인증서 교환이 불필요하며, 32바이트 base64 공개 키 교환만으로 완료된다.

### 2.3 Cryptokey Routing 상세 동작

**Cryptokey Routing**은 WireGuard의 핵심 개념이다. 전통적 라우팅 테이블이 "목적지 IP → 다음 홉 인터페이스" 매핑이라면, Cryptokey Routing은 **"공개 키 → 허용 IP 범위"** 매핑이다.

```
┌─────────────────────────────────────────────────────────┐
│              Cryptokey Routing Table (wg0)                │
├──────────────────────────┬──────────────────────────────┤
│       Public Key          │       AllowedIPs             │
├──────────────────────────┼──────────────────────────────┤
│ peer_A: gN65BkIK...      │ 10.0.0.2/32, 192.168.1.0/24 │
│ peer_B: HIgo9xNz...      │ 10.0.0.3/32                  │
│ peer_C: TrMvSoP4...      │ 10.0.0.4/32, 172.16.0.0/16  │
└──────────────────────────┴──────────────────────────────┘
```

**송신 시 (Outbound)**: AllowedIPs가 **라우팅 테이블** 역할

```
앱이 10.0.0.2로 패킷 전송
    │
    v
wg0 인터페이스 수신
    │
    v
AllowedIPs 테이블에서 10.0.0.2 매칭
    │
    v
peer_A의 공개 키로 암호화
    │
    v
peer_A의 최신 endpoint (IP:Port)로 UDP 전송
```

**수신 시 (Inbound)**: AllowedIPs가 **ACL(접근 제어 목록)** 역할

```
UDP 패킷 수신 (물리 인터페이스)
    │
    v
수신자 인덱스로 세션 식별
    │
    v
해당 피어의 세션 키로 복호화
    │
    v
내부 패킷의 소스 IP가 해당 피어의 AllowedIPs에 포함?
    │
    ├── YES → wg0 인터페이스로 전달
    └── NO  → 패킷 폐기 (스푸핑 방지)
```

이 구조 덕분에 별도의 방화벽 규칙 없이도 피어 간 접근 제어가 암호학적으로 보장된다.

### 2.4 암호화 알고리즘 상세

WireGuard는 **암호화 민첩성(crypto agility)**을 의도적으로 배제했다. 알고리즘 협상이 없으며, 단일 암호 스위트만 사용한다. 이는 공격 표면을 줄이고 구현 복잡도를 낮추기 위한 설계 결정이다.

| 알고리즘 | 역할 | 설명 |
|----------|------|------|
| **ChaCha20-Poly1305** | 대칭 암호화 + 인증 (AEAD) | RFC 7539 기반. AES-GCM 대비 하드웨어 가속 없이도 빠르다. ARM/MIPS 등 임베디드 환경에 유리. |
| **Curve25519** | ECDH 키 교환 | 타원곡선 디피-헬만(ECDH). 32바이트 키로 128비트 보안 수준 제공. 사이드 채널 공격에 강하다. |
| **BLAKE2s** | 해싱 및 키 유도 | SHA-256보다 빠르면서도 동등한 보안. MAC(메시지 인증 코드)에도 사용. RFC 7693. |
| **SipHash** | 해시테이블 키 | 해시 충돌 공격(HashDoS) 방어용. 내부 자료구조의 키 해싱에 사용. |
| **HKDF** | 키 유도 함수 | HMAC 기반 키 유도. 핸드셰이크 중간 비밀에서 최종 세션 키를 파생. |

**암호화 민첩성 배제의 의미**: 만약 ChaCha20에 취약점이 발견되면 WireGuard 버전 자체를 업그레이드한다. 프로토콜 내에서 알고리즘을 교체하는 것이 아니라, 프로토콜 버전을 올리는 방식이다. 이는 TLS의 POODLE, BEAST 같은 다운그레이드 공격을 원천 차단한다.

---

## 3. 동작 원리

### 3.1 전체 흐름: 핸드셰이크 → 키 교환 → 터널 생성 → 데이터 전송

```
시간 ──────────────────────────────────────────────────────────────→

  Peer A (Initiator)                         Peer B (Responder)
  ==================                         ==================

  [1] 패킷을 보내려 하나 세션이 없음
      → 핸드셰이크 시작

  ── Handshake Initiation (type=1) ────────→
  │ sender_index: 0x12345678                │
  │ ephemeral_pub: (32 bytes)               │
  │ encrypted_static: (48 bytes)            │  [2] 복호화 & 검증
  │ encrypted_timestamp: (28 bytes)         │      타임스탬프 > 이전 최대값?
  │ mac1: (16 bytes)                        │      → 리플레이 방지
  │ mac2: (16 bytes)                        │

                                             [3] 응답 생성

  ←── Handshake Response (type=2) ─────────
  │ sender_index: 0xABCDEF00                │
  │ receiver_index: 0x12345678              │
  │ ephemeral_pub: (32 bytes)               │
  │ encrypted_nothing: (16 bytes)           │
  │ mac1, mac2: (16+16 bytes)              │

  [4] 양측 세션 키 도출 완료
      (송신 키, 수신 키 별도)

  ── Transport Data (type=4) ──────────────→
  │ receiver_index: 0xABCDEF00              │
  │ counter: 0 (8 bytes, little-endian)     │
  │ encrypted_packet: (가변)                │
  │  └─ ChaCha20-Poly1305(                 │
  │       key=sending_key,                  │
  │       nonce=counter,                    │
  │       payload=원본 IP 패킷)              │

  ←── Transport Data (type=4) ─────────────
  │ ... (역방향 동일 구조)                   │

  [5] REKEY_AFTER_TIME(120초) 또는
      REKEY_AFTER_MESSAGES(2^60) 도달 시
      → 새 핸드셰이크 자동 시작 (키 로테이션)
```

### 3.2 타이머 및 상태 관리

WireGuard는 상태를 최소화한다. 핸드셰이크 전까지는 피어에 대한 상태를 전혀 유지하지 않는다(stateless).

| 타이머 | 값 | 설명 |
|--------|-----|------|
| REKEY_AFTER_TIME | 120초 | 이 시간 이후 Initiator가 새 핸드셰이크 시작 |
| REJECT_AFTER_TIME | 180초 | 세션의 최대 유효 시간. 이후 폐기 |
| REKEY_TIMEOUT | 5초 + 지터(0~333ms) | 핸드셰이크 재시도 간격 |
| KEEPALIVE_TIMEOUT | 설정값 (보통 25초) | NAT 매핑 유지용 빈 패킷 전송 주기 |
| REKEY_AFTER_MESSAGES | 2^60 | 메시지 카운터 임계값 도달 시 리키 |

### 3.3 DoS 방어: Cookie 메커니즘

서버에 부하가 집중되면 Cookie Reply 메커니즘이 활성화된다:

```
공격자가 대량의 Handshake Initiation 전송
    │
    v
서버 부하 감지
    │
    v
Cookie Reply (type=3) 응답
  │ XChaCha20Poly1305로 암호화
  │ Cookie = MAC(sender_IP, 2분마다 변경되는 서버 시크릿)
    │
    v
정상 클라이언트는 mac2 필드에 Cookie 포함하여 재전송
    │
    v
서버는 mac2 검증 후 정상 처리
```

이 메커니즘은 SYN Cookie와 유사하게 IP 소유권을 검증하여 IP 스푸핑 기반 DoS를 방어한다.

### 3.4 로밍 (Roaming)

WireGuard 피어의 endpoint는 고정이 아니다. 유효한 암호화 패킷이 수신되면, 해당 피어의 endpoint가 자동으로 갱신된다.

```
Peer A (모바일 디바이스)
  WiFi: 192.168.1.100 ──→ Peer B로 패킷 전송
  [이동 중...]
  LTE: 10.0.0.50      ──→ Peer B로 패킷 전송

Peer B 입장:
  Peer A의 endpoint: 192.168.1.100:51820
  → 새 유효 패킷 수신 (소스: 10.0.0.50:41023)
  → endpoint 갱신: 10.0.0.50:41023
  → 이후 응답은 새 주소로 전송
```

이는 모바일 환경에서 WiFi ↔ LTE 전환 시에도 VPN 연결이 자동으로 유지됨을 의미한다.

---

## 4. 설정 예시

### 4.1 Hub-Spoke 구성 (중앙 서버 + 다수 클라이언트)

가장 일반적인 배포 형태. 모든 트래픽이 Hub(서버)를 경유한다.

```
                    ┌──────────────┐
                    │   Hub 서버    │
                    │  10.0.0.1/24 │
                    │ :51820 (UDP) │
                    └──┬───┬───┬──┘
                       │   │   │
            ┌──────────┘   │   └──────────┐
            v              v              v
     ┌──────────┐  ┌──────────┐  ┌──────────┐
     │ Spoke A  │  │ Spoke B  │  │ Spoke C  │
     │ 10.0.0.2 │  │ 10.0.0.3 │  │ 10.0.0.4 │
     │ 노트북    │  │ 서버     │  │ IoT GW   │
     └──────────┘  └──────────┘  └──────────┘
```

**Hub 서버 설정** (`/etc/wireguard/wg0.conf`):

```ini
[Interface]
# 서버 개인 키 (wg genkey로 생성)
PrivateKey = YHubServerPrivateKeyBase64EncodedXXXXXXXX=
Address = 10.0.0.1/24
ListenPort = 51820

# IP 포워딩 및 NAT 설정
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE; sysctl -w net.ipv4.ip_forward=1
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Spoke A (노트북)
[Peer]
PublicKey = aSpokeAPublicKeyBase64EncodedXXXXXXXXXX=
AllowedIPs = 10.0.0.2/32

# Spoke B (원격 서버) - 서버 뒤 서브넷도 라우팅
[Peer]
PublicKey = bSpokeBPublicKeyBase64EncodedXXXXXXXXXX=
AllowedIPs = 10.0.0.3/32, 192.168.10.0/24

# Spoke C (IoT 게이트웨이) - IoT 디바이스 서브넷 라우팅
[Peer]
PublicKey = cSpokeCPublicKeyBase64EncodedXXXXXXXXXX=
AllowedIPs = 10.0.0.4/32, 172.16.0.0/16
```

**Spoke A (클라이언트) 설정**:

```ini
[Interface]
PrivateKey = xSpokeAPrivateKeyBase64EncodedXXXXXXXX=
Address = 10.0.0.2/32
# DNS도 VPN 터널을 통해 해석 (선택)
DNS = 10.0.0.1

[Peer]
PublicKey = zHubServerPublicKeyBase64EncodedXXXXXXXX=
# 모든 트래픽을 Hub으로 라우팅 (Full Tunnel)
AllowedIPs = 0.0.0.0/0, ::/0
# Hub 서버의 공인 IP와 포트
Endpoint = vpn.example.com:51820
# NAT 뒤에 있을 경우 킵얼라이브 필수
PersistentKeepalive = 25
```

**키 생성 명령어**:

```bash
# 개인 키 생성
wg genkey > privatekey

# 공개 키 도출
wg pubkey < privatekey > publickey

# Pre-shared Key 생성 (선택, 양자 컴퓨팅 대비 추가 보안 계층)
wg genpsk > presharedkey

# 서비스 시작
sudo wg-quick up wg0

# 상태 확인
sudo wg show
```

### 4.2 Mesh 구성 (모든 피어가 직접 연결)

피어 수가 적고(3~10개), 모든 노드 간 직접 통신이 필요한 경우 적합하다.

```
     ┌──────────┐
     │ Node A   │
     │ 10.0.0.1 │
     └──┬───┬───┘
        │   │
   ┌────┘   └────┐
   v              v
┌──────────┐  ┌──────────┐
│ Node B   │──│ Node C   │
│ 10.0.0.2 │  │ 10.0.0.3 │
└──────────┘  └──────────┘

각 노드는 다른 모든 노드를 [Peer]로 등록
총 연결 수 = N(N-1)/2 = 3개
```

**Node A 설정** (`/etc/wireguard/wg0.conf`):

```ini
[Interface]
PrivateKey = aNodeAPrivateKeyBase64EncodedXXXXXXXXXX=
Address = 10.0.0.1/24
ListenPort = 51820

# Node B
[Peer]
PublicKey = bNodeBPublicKeyBase64EncodedXXXXXXXXXXXX=
AllowedIPs = 10.0.0.2/32
Endpoint = node-b.example.com:51820
PersistentKeepalive = 25

# Node C
[Peer]
PublicKey = cNodeCPublicKeyBase64EncodedXXXXXXXXXXXX=
AllowedIPs = 10.0.0.3/32
Endpoint = node-c.example.com:51820
PersistentKeepalive = 25
```

**Node B 설정**:

```ini
[Interface]
PrivateKey = bNodeBPrivateKeyBase64EncodedXXXXXXXXXX=
Address = 10.0.0.2/24
ListenPort = 51820

# Node A
[Peer]
PublicKey = aNodeAPublicKeyBase64EncodedXXXXXXXXXXXX=
AllowedIPs = 10.0.0.1/32
Endpoint = node-a.example.com:51820
PersistentKeepalive = 25

# Node C
[Peer]
PublicKey = cNodeCPublicKeyBase64EncodedXXXXXXXXXXXX=
AllowedIPs = 10.0.0.3/32
Endpoint = node-c.example.com:51820
PersistentKeepalive = 25
```

**Mesh 구성의 한계**: 피어 수가 N개이면 각 노드에 N-1개의 Peer 설정이 필요하고, 새 노드 추가 시 모든 기존 노드 설정을 갱신해야 한다. 대규모 메시에는 Tailscale, Netmaker 같은 오케스트레이션 도구를 권장한다.

---

## 5. 성능 벤치마크

### 5.1 공식 벤치마크 (wireguard.com)

테스트 환경: Intel Core i7-3820QM / i7-5200U, 기가비트 이더넷, Linux 4.6.1, iperf3 (30분 평균)

| 프로토콜 | Throughput (Mbps) | Ping Latency (ms) | CPU 사용률 |
|----------|------------------:|-------------------:|-----------|
| **WireGuard** (ChaCha20-Poly1305) | **1,011** | **0.403** | 여유 있음 |
| IPsec (ChaCha20-Poly1305) | 825 | 0.521 | 100% (max) |
| IPsec (AES-256-GCM) | 881 | 0.508 | 100% (max) |
| OpenVPN | 258 | 1.541 | 100% (max) |
| 베어메탈 (VPN 없음) | ~1,000 | ~0.3 | - |

### 5.2 클라우드 환경 벤치마크 (2025 학술 논문)

VMware 가상 환경에서의 TCP 성능 비교:

| 지표 | WireGuard | OpenVPN | 비고 |
|------|----------:|--------:|------|
| TCP Throughput | 210.64 Mbps | 110.34 Mbps | WireGuard 1.9배 |
| Packet Loss | 12.35% | 47.01% | WireGuard 3.8배 낮음 |

### 5.3 리소스 사용량 (100 Mbps 암호화 부하 기준)

```
CPU 사용률 비교 (100 Mbps 암호화 기준)

WireGuard   ██░░░░░░░░░░░░░░░░░░  2~5%
IPsec       █████░░░░░░░░░░░░░░░  5~10%
OpenVPN     ███████████████░░░░░  ~15%+

             0%        10%       20%
```

**WireGuard가 빠른 이유**:

1. **커널 공간 실행**: 유저스페이스 ↔ 커널 간 데이터 복사 불필요
2. **멀티스레드 처리**: 패킷 암/복호화를 여러 CPU 코어에 분산
3. **최소 프로토콜 오버헤드**: 핸드셰이크 1-RTT, 데이터 패킷 헤더 32바이트
4. **최적화된 암호 알고리즘**: ChaCha20은 SIMD 명령어 활용에 유리

---

## 6. 비교 대상 솔루션과의 비교

### 6.1 종합 비교표

| 항목 | WireGuard | OpenVPN | IPsec/IKEv2 | Tinc | Nebula |
|------|-----------|---------|-------------|------|--------|
| **코드량** | ~4,000줄 | ~600,000줄 | ~400,000줄 (StrongSwan) | ~30,000줄 | ~20,000줄 (Go) |
| **프로토콜** | Noise IK (자체) | TLS/SSL 기반 | IKEv1/v2 + ESP/AH (IETF 표준) | SPTPS (자체) | Noise IX (자체) |
| **동작 계층** | Layer 3, 커널 | Layer 2/3, 유저스페이스 | Layer 3, 커널 | Layer 2/3, 유저스페이스 | Layer 3, 유저스페이스 |
| **대칭 암호화** | ChaCha20-Poly1305 | AES-256-GCM, ChaCha20 등 선택 | AES-GCM, ChaCha20 등 선택 | AES-256-CBC, ChaCha20 | ChaCha20-Poly1305 |
| **키 교환** | Curve25519 (DH) | RSA/ECDH + 인증서 | DH/ECDH + 인증서/PSK | RSA/Ed25519 | Curve25519 (DH) |
| **암호 민첩성** | 없음 (단일 스위트) | 있음 (협상 가능) | 있음 (협상 가능) | 있음 | 없음 (단일 스위트) |
| **Throughput** | ~1 Gbps | ~258 Mbps | ~880 Mbps | ~200 Mbps | ~500 Mbps |
| **Latency 추가** | +0.1ms | +1.2ms | +0.2ms | +1.5ms/홉 | +0.5ms |
| **설정 복잡도** | 매우 낮음 | 중간 | 높음 | 중간 | 중간 |
| **인증 방식** | 공개 키 (수동 교환) | 인증서/ID+PW | 인증서/PSK/EAP | 공개 키 (수동 교환) | 인증서 (자체 CA) |
| **NAT 통과** | 단방향 NAT 지원 | TCP 443 폴백 가능 | NAT-T (UDP 4500) | UDP 홀펀칭 | 양방향 NAT (Lighthouse) |
| **메시 지원** | 수동 (N^2 설정) | 수동 | 수동 | 자동 메시 | 자동 메시 |
| **플랫폼** | Linux, Windows, macOS, iOS, Android, BSD, 라우터 | 거의 모든 OS | 거의 모든 OS | Linux, BSD, macOS, Windows | Linux, macOS, Windows, iOS, Android |
| **라이선스** | GPL v2 | GPL v2 (CE), 상용 (AS) | 구현체마다 상이 | GPL v2 | MIT |
| **표준화** | 비표준 (사실상 표준) | 비표준 | IETF RFC 다수 | 비표준 | 비표준 |

### 6.2 개별 비교 요약

**WireGuard vs OpenVPN**:
- OpenVPN은 TLS 기반으로 인증서 관리가 필요하며, 유저스페이스에서 동작하여 성능이 낮다.
- OpenVPN은 TCP 모드로 방화벽 우회가 가능하지만, WireGuard는 UDP만 지원한다.
- OpenVPN은 20년 이상의 실전 검증과 광범위한 에코시스템을 보유한다.

**WireGuard vs IPsec/IKEv2**:
- IPsec은 IETF 표준으로 기업 네트워크 장비 간 호환성이 뛰어나다.
- IPsec 설정은 매우 복잡하며(SA, SP, IKE 설정 등), 디버깅이 어렵다.
- 성능은 WireGuard와 유사하나 CPU 사용률이 더 높다.

**WireGuard vs Tinc**:
- Tinc는 자동 메시 라우팅을 지원하여 대규모 분산 네트워크에 유리하다.
- 성능은 WireGuard 대비 크게 뒤지며, 각 홉마다 ~1.5ms 지연이 추가된다.
- Tinc 1.1(프리릴리즈)은 SPTPS로 PFS를 지원하지만, 안정 버전(1.0)은 미지원.

**WireGuard vs Nebula**:
- Nebula는 Slack(현 Salesforce)이 만든 오버레이 네트워크로, 인증서 기반 자동 메시를 제공한다.
- Lighthouse 노드를 통해 양방향 NAT 환경에서도 피어 탐색이 가능하다.
- 인증서에 그룹 정보를 포함하여 AWS Security Group과 유사한 내장 방화벽을 지원한다.
- WireGuard 대비 throughput은 낮지만, 대규모 동적 네트워크 관리에 강하다.

---

## 7. 장단점 정리

### 장점

| 항목 | 설명 |
|------|------|
| **단순성** | ~4,000줄 코드. 전체 프로토콜을 한 사람이 이해할 수 있다. 보안 감사(audit)가 현실적으로 가능. |
| **성능** | 커널 모듈 + 최적화된 암호 = 기가비트 회선에서 라인레이트 근접. CPU 여유. |
| **최신 암호학** | ChaCha20, Curve25519 등 현대적 프리미티브만 사용. 레거시 알고리즘 없음. |
| **최소 공격 표면** | 암호 협상 없음 → 다운그레이드 공격 불가. 코드가 적음 → 버그 확률 낮음. |
| **로밍 지원** | IP 변경 시 자동 endpoint 갱신. 모바일 환경에 최적. |
| **Stealth** | 핸드셰이크 전까지 어떤 패킷에도 응답하지 않음. 포트 스캔에 노출 안 됨. |
| **설정 간편** | SSH key처럼 공개 키 교환만으로 완료. 인증서 인프라(PKI) 불필요. |
| **크로스 플랫폼** | Linux, Windows, macOS, iOS, Android, BSD, 라우터(OpenWrt 등) 지원. |

### 단점

| 항목 | 설명 |
|------|------|
| **UDP 전용** | TCP 지원 없음. 기업 방화벽이 UDP를 차단하면 사용 불가. (Cloudflare WARP 등의 래퍼로 우회 가능) |
| **동적 IP 할당 없음** | DHCP 같은 IP 자동 할당 기능이 없다. 각 피어에 수동으로 IP 배정 필요. |
| **피어 관리** | 새 피어 추가 시 서버 설정 수동 갱신 필요. 대규모 환경에서는 Tailscale/Netmaker 같은 오케스트레이션 도구가 사실상 필수. |
| **암호 민첩성 부재** | 알고리즘 교체 시 전체 업그레이드 필요. 기업 컴플라이언스(FIPS 등)에서 문제 가능. |
| **로깅 최소** | 개인정보 보호를 위해 의도적으로 로그를 남기지 않음. 기업 환경 감사(audit trail)에 부적합. |
| **Layer 2 미지원** | Layer 3(IP)만 지원. 브릿지 모드(TAP)가 필요한 환경에서는 OpenVPN/Tinc 사용. |
| **비표준** | IETF RFC가 아님. 규제 산업에서 표준 준수가 요구되면 IPsec이 유리. |

---

## 8. 실무 활용 시나리오

### 8.1 IoT/임베디드 디바이스 연결

```
┌─────────────────────────────────────────────┐
│                 클라우드                      │
│  ┌──────────────────────────────────────┐   │
│  │  WireGuard Hub + 모니터링 서버        │   │
│  │  10.0.0.1/24                         │   │
│  └──────────────┬───────────────────────┘   │
└─────────────────┼───────────────────────────┘
                  │ UDP 51820
    ┌─────────────┼──────────────┐
    │             │              │
    v             v              v
┌────────┐  ┌────────┐  ┌────────────────┐
│ RPi 4  │  │ Jetson │  │ OpenWrt 라우터  │
│ 센서GW │  │ Nano   │  │ (공장 현장)     │
│10.0.0.2│  │10.0.0.3│  │ 10.0.0.4       │
│        │  │ 영상AI │  │   └─ 172.16.0.0/24│
└────────┘  └────────┘  │      (PLC/센서)  │
                        └────────────────┘
```

**적합한 이유**:
- ChaCha20은 AES 하드웨어 가속이 없는 ARM/MIPS 칩에서도 빠르다
- ~4,000줄 커널 모듈은 임베디드 리눅스의 제한된 스토리지에 적합
- PersistentKeepalive로 NAT 뒤 디바이스의 연결 유지
- IP 변경(DHCP 갱신, LTE 로밍) 시 자동 재연결

### 8.2 멀티사이트 서버 연결 (Site-to-Site)

```
┌───────────────────┐     WireGuard      ┌───────────────────┐
│  서울 데이터센터    │     Tunnel         │  부산 데이터센터    │
│  192.168.1.0/24   │◄──────────────────►│  192.168.2.0/24   │
│  wg: 10.0.0.1     │     UDP 51820      │  wg: 10.0.0.2     │
└────────┬──────────┘                    └────────┬──────────┘
         │         WireGuard Tunnel               │
         │◄──────────────────────────────────────►│
         │                                        │
         │              ┌───────────────────┐     │
         │              │  AWS VPC           │     │
         └─────────────►│  10.100.0.0/16    │◄────┘
                        │  wg: 10.0.0.3     │
                        └───────────────────┘
```

**설정 포인트**:
- 각 사이트 게이트웨이의 AllowedIPs에 상대 사이트 서브넷을 포함
- `PostUp`에서 `ip route add` 및 `iptables FORWARD` 규칙 추가
- MTU는 1420 (WireGuard 헤더 80바이트 감안) 기본값 사용

### 8.3 원격 개발자 접속 (Road Warrior)

```
개발자 노트북 (카페, 집, 해외)
    │
    │ WireGuard (AllowedIPs = 10.0.0.0/24, 172.16.0.0/12)
    │ Split Tunneling: 일반 웹은 로컬 인터넷, 사내만 VPN
    v
┌──────────────────────────────────┐
│  WireGuard 게이트웨이 (DMZ)       │
│  10.0.0.1                        │
│  iptables: FORWARD wg0 → eth1   │
└──────────────┬───────────────────┘
               │
    ┌──────────┼──────────┐
    v          v          v
  Git서버   CI/CD      내부 DB
  10.0.0.10  10.0.0.20  172.16.1.5
```

**Split Tunneling 설정**: AllowedIPs에 `0.0.0.0/0` 대신 사내 네트워크 대역만 지정하면, 일반 인터넷 트래픽은 VPN을 거치지 않아 성능이 유지된다.

### 8.4 Kubernetes 클러스터 간 연결

멀티 클라우드/하이브리드 환경에서 Kubernetes 클러스터 간 Pod 네트워크 연결:

```
AWS EKS                          GCP GKE
Pod CIDR: 10.244.0.0/16         Pod CIDR: 10.245.0.0/16
Service CIDR: 10.96.0.0/12      Service CIDR: 10.97.0.0/12
    │                                │
    v                                v
WireGuard Node (DaemonSet)      WireGuard Node (DaemonSet)
AllowedIPs:                     AllowedIPs:
  10.245.0.0/16                   10.244.0.0/16
  10.97.0.0/12                    10.96.0.0/12
```

### 8.5 제로 트러스트 네트워크 구축

WireGuard를 기반으로 한 제로 트러스트 아키텍처 구축 시:
- **Tailscale**: WireGuard 기반 + 중앙 관리 + ACL + SSO 통합
- **Netmaker**: 자체 호스팅 가능한 WireGuard 오케스트레이션
- **Headscale**: Tailscale의 오픈소스 컨트롤 플레인 대체

---

## 9. 참고 자료

### 공식 자료

| 자료 | URL |
|------|-----|
| WireGuard 공식 사이트 | [https://www.wireguard.com/](https://www.wireguard.com/) |
| WireGuard 백서 (학술 논문) | [https://www.wireguard.com/papers/wireguard.pdf](https://www.wireguard.com/papers/wireguard.pdf) |
| 프로토콜 & 암호화 상세 | [https://www.wireguard.com/protocol/](https://www.wireguard.com/protocol/) |
| 공식 성능 벤치마크 | [https://www.wireguard.com/performance/](https://www.wireguard.com/performance/) |
| WireGuard 소스 코드 (Git) | [https://git.zx2c4.com/wireguard-linux](https://git.zx2c4.com/wireguard-linux) |
| Jason Donenfeld 개인 사이트 | [https://www.zx2c4.com/](https://www.zx2c4.com/) |

### Noise Protocol Framework

| 자료 | URL |
|------|-----|
| Noise Protocol 명세 | [https://noiseprotocol.org/noise.html](https://noiseprotocol.org/noise.html) |
| Noise Explorer (형식 검증) | [https://noiseexplorer.com/](https://noiseexplorer.com/) |

### 관련 RFC

| RFC | 제목 |
|-----|------|
| RFC 7539 | ChaCha20 and Poly1305 for IETF Protocols |
| RFC 7693 | The BLAKE2 Cryptographic Hash and MAC |
| RFC 7748 | Elliptic Curves for Security (Curve25519) |
| RFC 5869 | HMAC-based Extract-and-Expand Key Derivation Function (HKDF) |
| RFC 6040 | Tunnelling of Explicit Congestion Notification (ECN) |
| RFC 7296 | Internet Key Exchange Protocol Version 2 (IKEv2) |

### 학술 논문 및 분석

| 자료 | URL |
|------|-----|
| WireGuard vs OpenVPN 성능 비교 논문 | [https://www.researchgate.net/publication/339954478](https://www.researchgate.net/publication/339954478_A_Performance_Comparison_of_WireGuard_and_OpenVPN) |
| WireGuard/IPSec 성능 평가 논문 | [https://www.researchgate.net/publication/392754145](https://www.researchgate.net/publication/392754145_Performance_Evaluation_of_WireGuard_and_IPSec_Protocols_in_Various_Network_Configurations) |
| IoT 환경 WireGuard 적용 논문 | [https://arxiv.org/pdf/2402.02093](https://arxiv.org/pdf/2402.02093) |
| 클라우드/가상화 환경 실증 분석 | [https://www.mdpi.com/2073-431X/14/8/326](https://www.mdpi.com/2073-431X/14/8/326) |

### 비교 대상 솔루션

| 솔루션 | URL |
|--------|-----|
| OpenVPN | [https://openvpn.net/](https://openvpn.net/) |
| StrongSwan (IPsec) | [https://www.strongswan.org/](https://www.strongswan.org/) |
| Tinc VPN | [https://www.tinc-vpn.org/](https://www.tinc-vpn.org/) |
| Nebula (Defined Networking) | [https://github.com/slackhq/nebula](https://github.com/slackhq/nebula) |
| Nebula vs WireGuard 비교 | [https://www.defined.net/blog/nebula-vs-wireguard/](https://www.defined.net/blog/nebula-vs-wireguard/) |
| Tailscale (WireGuard 기반) | [https://tailscale.com/](https://tailscale.com/) |
| Netmaker (WireGuard 기반) | [https://www.netmaker.io/](https://www.netmaker.io/) |

### 실습 가이드

| 자료 | URL |
|------|-----|
| DigitalOcean WireGuard 셋업 가이드 | [https://www.digitalocean.com/community/tutorials/how-to-set-up-wireguard-on-ubuntu-20-04](https://www.digitalocean.com/community/tutorials/how-to-set-up-wireguard-on-ubuntu-20-04) |
| Hub-Spoke 구성 상세 가이드 | [https://www.procustodibus.com/blog/2020/11/wireguard-hub-and-spoke-config/](https://www.procustodibus.com/blog/2020/11/wireguard-hub-and-spoke-config/) |
| Mesh VPN 구성 가이드 | [https://www.zenarmor.com/docs/network-security-tutorials/how-to-configure-wireguard-mesh-vpn](https://www.zenarmor.com/docs/network-security-tutorials/how-to-configure-wireguard-mesh-vpn) |
| 비공식 WireGuard 문서 모음 | [https://github.com/pirate/wireguard-docs](https://github.com/pirate/wireguard-docs) |

---

> 이 문서는 2026-03-27 기준으로 작성되었으며, WireGuard 프로토콜 및 관련 벤치마크 데이터는 각 출처의 측정 시점에 따라 달라질 수 있습니다.
