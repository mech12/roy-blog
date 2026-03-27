# 네트워크 및 자동화 인프라 구축

> 다른 분야 시니어 엔지니어를 위한 핵심 용어 해설 포함

## 세부 문서

| # | 주제 | 세부 문서 |
| --- | ------ | ----------- |
| 03-01 | WireGuard | [03-01-WireGuard.md](03-01-WireGuard.md) |
| 03-02 | Tailscale | [03-02-Tailscale.md](03-02-Tailscale.md) |
| 03-03 | NAT Traversal / Hole Punching | [03-03-NAT-Traversal-HolePunching.md](03-03-NAT-Traversal-HolePunching.md) |

---

## 1. 기본 개념: NAT란?

### NAT (Network Address Translation)

**한 줄 요약**: 사설 IP 주소를 공인 IP 주소로 변환하는 기술

```
사설 네트워크                    인터넷
┌──────────────┐               ┌──────────────┐
│ 192.168.1.10 │──┐            │              │
│ 192.168.1.11 │──┤── NAT ──→ │  203.0.113.1 │ ← 공인 IP 1개
│ 192.168.1.12 │──┘  (라우터)   │              │
└──────────────┘               └──────────────┘
   디바이스 3대                   외부에서는 1개로 보임
```

- 가정/사무실 대부분이 NAT 환경 (공유기 = NAT 장비)
- IPv4 주소 부족 문제 해결을 위해 등장
- **문제점**: 외부에서 내부 디바이스로의 직접 접근이 차단됨 → 서버 간 통신에 장애

### NAT의 종류

| 타입 | 설명 | 뚫기 난이도 |
|------|------|------------|
| **Full Cone** | 외부 어디서든 매핑된 포트로 접근 가능 | 쉬움 |
| **Restricted Cone** | 내부에서 먼저 통신한 IP만 접근 허용 | 보통 |
| **Port Restricted** | IP + 포트 모두 일치해야 접근 허용 | 어려움 |
| **Symmetric** | 목적지마다 다른 포트 매핑 | 매우 어려움 |

---

## 2. NAT 극복 기술

### STUN (Session Traversal Utilities for NAT)

**한 줄 요약**: "내 공인 IP와 포트가 뭔지 알려주는 서비스"

```
┌─────────┐                    ┌─────────────┐
│ 클라이언트 │ ──── 요청 ────→  │ STUN 서버    │
│ (NAT 뒤) │ ←── 응답 ────   │ (공인 IP)    │
└─────────┘  "너의 공인 IP는   └─────────────┘
              203.0.113.1:5000
              이야"
```

- **동작 원리**: 클라이언트가 STUN 서버에 요청 → 서버가 클라이언트의 공인 IP:포트를 응답
- **용도**: P2P 연결 시 상대방에게 알려줄 자신의 공인 주소 파악
- **한계**: Symmetric NAT에서는 작동하지 않음
- **비용**: 거의 없음 (주소 확인만 수행)

### TURN (Traversal Using Relays around NAT)

**한 줄 요약**: "직접 연결 불가능할 때 중계 서버를 통해 트래픽을 전달"

```
┌──────────┐         ┌─────────────┐         ┌──────────┐
│ 피어 A    │ ──────→ │ TURN 서버    │ ──────→ │ 피어 B    │
│ (NAT 뒤) │ ←────── │ (중계 역할)   │ ←────── │ (NAT 뒤) │
└──────────┘         └─────────────┘         └──────────┘
```

- **동작 원리**: 양쪽 피어가 모두 TURN 서버에 연결 → 서버가 트래픽을 중계
- **vs STUN**: STUN은 주소만 알려주고 끝, TURN은 실제 트래픽을 중계
- **비용**: 높음 (모든 트래픽이 서버를 경유 → 대역폭 비용)
- **용도**: Symmetric NAT 등 STUN만으로 불가능한 환경의 최후 수단

### UDP Hole Punching

**한 줄 요약**: "양쪽이 동시에 패킷을 보내서 NAT에 구멍을 뚫는 기법"

```
1. 피어 A → STUN 서버: "내 공인 주소 알려줘" → 203.0.113.1:5000
2. 피어 B → STUN 서버: "내 공인 주소 알려줘" → 198.51.100.2:6000
3. 중개 서버가 서로의 주소를 교환
4. 피어 A → 198.51.100.2:6000 (동시에)
   피어 B → 203.0.113.1:5000 (동시에)
5. NAT 장비가 "나가는 패킷이 있으니 들어오는 것도 허용" → 연결 성립!
```

- 대부분의 NAT는 UDP 패킷 매칭이 느슨하여 이 방법이 통함
- STUN으로 주소 확인 → Hole Punching 시도 → 실패 시 TURN 폴백

---

## 3. VPN 기술

### VPN (Virtual Private Network) 이란?

**한 줄 요약**: "인터넷 위에 암호화된 가상 사설 네트워크를 구축하는 기술"

```
서버 A (서울)                    서버 B (부산)
┌──────────┐    암호화 터널     ┌──────────┐
│ 10.0.1.1 │ ═══════════════ │ 10.0.1.2 │
└──────────┘   인터넷 통과      └──────────┘
               하지만 암호화됨
```

- 물리적으로 떨어진 서버들을 같은 사설 네트워크에 있는 것처럼 연결
- 모든 트래픽이 암호화되어 보안 통신 보장

### WireGuard

**한 줄 요약**: "빠르고 간단한 차세대 VPN 프로토콜"

| 항목 | OpenVPN | WireGuard |
|------|---------|-----------|
| **코드량** | ~100,000줄 | ~4,000줄 |
| **암호화** | OpenSSL (다양한 알고리즘) | Noise Protocol (ChaCha20, Curve25519) |
| **성능** | 보통 | 매우 빠름 (Linux 커널 모듈) |
| **설정** | 복잡 (인증서 관리 등) | 간단 (공개키 교환) |
| **프로토콜** | TCP/UDP | UDP만 |
| **상태** | 연결 유지 상태 관리 | Cryptokey Routing (무상태) |

**WireGuard 핵심 개념**:

- **Cryptokey Routing**: 공개키와 허용 IP 대역을 매핑하여 라우팅
  ```ini
  [Peer]
  PublicKey = xTIBA5rbo...     # 상대방 공개키
  AllowedIPs = 10.0.1.2/32     # 이 키로 오는 패킷의 허용 IP
  Endpoint = 203.0.113.5:51820 # 상대방 실제 주소
  ```
- **Linux 커널 모듈**: 유저스페이스가 아닌 커널에서 동작 → 네이티브에 가까운 속도

### Tailscale

**한 줄 요약**: "WireGuard 위에 자동 설정/NAT 극복을 얹은 메시 VPN 서비스"

```
전통적 VPN (Hub-Spoke)          Tailscale (Mesh)
       ┌───┐                    A ←→ B
   A → │ S │ ← B               A ←→ C
   C → │   │ ← D               B ←→ C
       └───┘                    모든 노드가 직접 연결
 모든 트래픽이 서버 경유
```

- WireGuard를 내부적으로 사용하되, 키 교환/NAT 트래버설/ACL을 자동화
- **제어 평면**(coordination server): 피어 간 공개키/주소 교환 관리
- **데이터 평면**: 피어 간 직접 WireGuard 터널 (서버를 경유하지 않음)
- NAT 뒤에 있어도 자동으로 STUN → Hole Punching → TURN 폴백
- SSO 연동, ACL 정책, MagicDNS 등 엔터프라이즈 기능 제공

### 오버레이 네트워크 (Overlay Network)

**한 줄 요약**: "기존 물리 네트워크 위에 가상의 논리적 네트워크를 구성하는 것"

- **언더레이**: 실제 물리적 네트워크 (인터넷, LAN)
- **오버레이**: 언더레이 위에 터널링/캡슐화로 구축한 가상 네트워크
- 예: WireGuard 터널, VXLAN, Kubernetes의 Pod 네트워크 (Flannel, Calico)
- **장점**: 물리 네트워크 구조와 무관하게 논리적 네트워크 토폴로지 자유 설계

---

## 4. 인프라 자동화

### IaC (Infrastructure as Code)

**한 줄 요약**: "인프라를 코드로 정의하고 버전 관리하는 방법론"

| 도구 | 용도 | 언어 |
|------|------|------|
| **Terraform** | 클라우드/온프레미스 인프라 프로비저닝 | HCL (HashiCorp Configuration Language) |
| **Ansible** | 서버 구성 관리, 배포 자동화 | YAML (Playbook) |
| **Pulumi** | 인프라 프로비저닝 (프로그래밍 언어 사용) | Python, TypeScript, Go 등 |

### Bash/Python 자동화 스크립트

실무에서 자주 자동화하는 작업:

- **서버 초기 설정**: 패키지 설치, 사용자 생성, SSH 키 배포, 방화벽 규칙
- **배포 자동화**: Docker 이미지 빌드 → 레지스트리 푸시 → 서비스 재시작
- **백업/복원**: DB 덤프, 파일 시스템 스냅샷, S3 업로드
- **모니터링/알림**: 디스크 사용량, 프로세스 상태, 로그 패턴 감지
- **인증서 갱신**: Let's Encrypt 자동 갱신 크론잡

```bash
# 예: 서버 헬스체크 자동화 (Bash)
#!/bin/bash
for host in server1 server2 server3; do
    if ! ssh "$host" "systemctl is-active --quiet myservice"; then
        echo "[ALERT] $host: myservice is down" | send_slack_notification
        ssh "$host" "systemctl restart myservice"
    fi
done
```

```python
# 예: 인프라 상태 수집 (Python)
import subprocess, json

def get_disk_usage(host):
    result = subprocess.run(
        ["ssh", host, "df -h --output=pcent / | tail -1"],
        capture_output=True, text=True
    )
    return int(result.stdout.strip().replace('%', ''))
```

---

## 5. 실무 아키텍처 예시

### 다중 사이트 서버 연결 (WireGuard + NAT 극복)

```
┌─ 서울 사무실 (NAT 뒤) ──────┐       ┌─ AWS 클라우드 ──────────┐
│  Server A: 10.0.1.1         │       │  Server C: 10.0.1.3    │
│  Server B: 10.0.1.2         │       │  (공인 IP 보유)          │
│  WireGuard Interface: wg0   │═══════│  WireGuard Hub          │
└─────────────────────────────┘       └─────────────────────────┘
                                              ║
                                      ┌─ 부산 IDC (NAT 뒤) ─────┐
                                      │  Server D: 10.0.1.4     │
                                      │  Server E: 10.0.1.5     │
                                      │  WireGuard Interface: wg0│
                                      └─────────────────────────┘
```

- 공인 IP가 있는 서버를 Hub로 사용
- NAT 뒤의 서버들은 Hub에 WireGuard 터널 연결
- 모든 서버가 `10.0.1.x` 사설 대역으로 통신 가능
- 또는 Tailscale을 사용하면 Hub 없이 메시 구성 자동화

---

## 참고 자료

- [What is STUN? (Tailscale Docs)](https://tailscale.com/kb/1462/what-is-stun)
- [Mesh VPN with NAT Traversal via STUN/TURN (Uppsala University)](https://uu.diva-portal.org/smash/get/diva2:1897708/FULLTEXT01.pdf)
- [NAT Traversal with WireGuard (NordVPN)](https://nordvpn.com/blog/achieving-nat-traversal-with-wireguard/)
- [OpenVPN vs WireGuard vs Tailscale (GL.iNet)](https://www.gl-inet.com/blog/openvpn-vs-wireguard-vs-tailscale-which-vpn-to-choose/)
- [WireGuard vs Tailscale (Tailscale)](https://tailscale.com/compare/wireguard)
- [STUN and NAT (Coder Docs)](https://coder.com/docs/admin/networking/stun)
