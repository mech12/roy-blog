---
layout: default
title: 엔디언 CPU별 역사
parent: On Holy Wars and a Plea for Peace
grand_parent: 걸리버 여행기 원작에 대해
nav_order: 1
---

# Big-endian / Little-endian의 CPU별 역사

걸리버 여행기의 빅엔디언/리틀엔디언 풍자에서 유래한 컴퓨터 용어의 역사를 살펴봅니다.

---

## 초기 컴퓨터 시대 (1960~1970년대)

| 시스템 | 엔디언 | 출시 연도 | 비고 |
|--------|--------|-----------|------|
| IBM System/360 | Big-endian | 1964 | 메인프레임의 표준 |
| PDP-11 | Little-endian | 1970 | DEC의 선택 |
| PDP-10 | Big-endian | 1966 | 36비트 워드 |

---

## 1980년대: 분열의 시대

Danny Cohen이 1980년 논문을 쓸 당시, 컴퓨터 세계는 혼란 그 자체였습니다.

```
Big-endian 진영          Little-endian 진영
─────────────────        ─────────────────
IBM 메인프레임            Intel 8080/8086
Motorola 68000           DEC VAX
Sun SPARC
```

**왜 이런 분열이 생겼나?**

- **Big-endian 지지자**: "사람이 읽는 순서와 같다. 0x1234는 12 34로 저장되어야 자연스럽다."
- **Little-endian 지지자**: "하위 바이트가 낮은 주소에 있으면 타입 캐스팅이 쉽다. 32비트 → 16비트 변환 시 주소 변경 불필요."

---

## 주요 CPU 아키텍처별 엔디언 역사

### Intel x86 (Little-endian)

```
1978: 8086 출시 - Little-endian 채택
이유: 8비트 8080과의 호환성 + 하드웨어 설계 단순화

0x12345678 저장 시:
주소:  0x00  0x01  0x02  0x03
값:    0x78  0x56  0x34  0x12
       ↑ 최하위 바이트가 가장 낮은 주소
```

### Motorola 68000 (Big-endian)

```
1979: 68000 출시 - Big-endian 채택
Apple Macintosh, Amiga, Atari ST에 사용

0x12345678 저장 시:
주소:  0x00  0x01  0x02  0x03
값:    0x12  0x34  0x56  0x78
       ↑ 최상위 바이트가 가장 낮은 주소
```

### MIPS (양쪽 지원)

```
1985: MIPS R2000 출시
특징: Bi-endian - 부팅 시 엔디언 선택 가능

SGI 워크스테이션: Big-endian으로 운영
PlayStation 1/2: Little-endian으로 운영
```

### ARM (양쪽 지원, 기본 Little-endian)

```
1985: ARM1 출시 - Little-endian 기본
2000년대 이후: Bi-endian 지원하지만 Little-endian이 사실상 표준

iPhone, Android 기기: 모두 Little-endian
```

---

## 참고 자료

- Danny Cohen, "On Holy Wars and a Plea for Peace", IEEE Computer, 1981
- Intel 64 and IA-32 Architectures Software Developer's Manual
