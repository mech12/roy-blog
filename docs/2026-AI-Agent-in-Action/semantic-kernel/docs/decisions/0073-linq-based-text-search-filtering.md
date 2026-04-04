---
status: accepted
contact: alzarei
date: 2025-10-25
deciders: roji, westey-m, markwallace-microsoft
consulted:
informed:
---

# ITextSearch를 절 기반에서 LINQ 기반 필터링으로 마이그레이션

## 맥락과 문제 설명

**도전 과제**: 기존 `ITextSearch` 인터페이스는 필터링을 위해 절 기반 `TextSearchFilter`를 사용하며, 이는 속성 이름 오타로 인한 런타임 오류, IntelliSense 지원 부재, 더 이상 사용되지 않는 `VectorSearchFilter` API에 대한 의존성을 야기합니다. 현대 .NET 관행은 타입 안전성과 컴파일 타임 검증을 위해 LINQ 표현식을 선호합니다.

**제약 조건**: 호환성을 깨는 변경을 도입할 수 없습니다. `TextSearchFilter`를 사용하는 기존 코드는 계속 작동해야 합니다.

**질문**: 하위 호환성을 유지하면서 ITextSearch를 현대적인 LINQ 기반 필터링(`Expression<Func<TRecord, bool>>`)으로 어떻게 마이그레이션할 수 있습니까?

이슈: https://github.com/microsoft/semantic-kernel/issues/10456

## 결정 동인

- **타입 안전성**: 속성 이름 오타 및 타입 불일치로 인한 런타임 오류 제거
- **개발자 경험**: IntelliSense 및 컴파일 타임 검증 활성화
- **기술 부채**: 더 이상 사용되지 않는 VectorSearchFilter API에 대한 의존성 제거
- **성능**: 불필요한 변환 오버헤드 제거
- **일관성**: Microsoft.Extensions.VectorData LINQ 필터링 패턴과 정렬
- **하위 호환성**: 소비자를 위한 기존 기능 유지
- **AOT 호환성**: 사전 컴파일 시나리오 지원
- **마이그레이션 경로**: 레거시 인터페이스의 최종 제거를 위한 명확한 경로 수립

## 결정 결과

**선택한 옵션**: "이중 인터페이스 패턴". `[Obsolete]`로 표시된 기존 `ITextSearch`와 함께 LINQ 필터링을 사용하는 제네릭 `ITextSearch<TRecord>`를 도입합니다.

현대적 LINQ 기반 **`ITextSearch<TRecord>`**를 레거시 **`ITextSearch`**(`[Obsolete]`로 표시)와 함께 도입합니다. 두 인터페이스가 임시로 공존하여 다음을 제공합니다:

- ✅ **호환성을 깨는 변경 없음**: 기존 코드가 변경 없이 계속 작동
- ✅ **명확한 마이그레이션 신호**: 사용 중단 경고가 개발자를 현대적 인터페이스로 안내
- ✅ **새 코드의 타입 안전성**: LINQ 표현식이 컴파일 타임 검증 제공
- ✅ **깔끔한 분리**: 레거시와 현대적 경로가 완전히 독립적
- ✅ **향후 제거 경로**: 향후 메이저 버전에서의 레거시 인터페이스 제거 일정 수립

이것은 영구적인 설계가 아닌 명시적으로 **임시적인 아키텍처 상태**입니다. 이중 인터페이스 패턴은 호환성을 깨지 않는 마이그레이션을 가능하게 하면서 향후 메이저 버전에서 기술 부채를 제거할 수 있는 명확한 경로를 수립합니다.

### 결정의 장단점

**좋은 점**:

- **호환성을 깨는 변경 없음**: 기존 코드가 변경 없이 계속 작동
- **깔끔한 분리**: 레거시와 현대적 경로가 완전히 독립적(변환 오버헤드 없음)
- **타입 안전성**: 제네릭 인터페이스가 컴파일 타임 검증 및 IntelliSense 제공
- **AOT 호환성**: 두 인터페이스 모두 AOT 호환(차단 속성 없음)
- **명확한 마이그레이션 경로**: `[Obsolete]` 속성이 사용 중단을 신호하고 사용자를 현대적 인터페이스로 안내
- **미래 준비**: 향후 메이저 버전에서 레거시 인터페이스 제거를 위한 명확한 경로 수립
- **생태계 정렬**: 호환성을 깨는 변경 전에 소비자에게 마이그레이션 시간 제공
- **단계적 구현**: 위험을 줄이고 집중된 코드 리뷰 가능

**나쁜 점**:

- **이중 코드 경로**: 클래스당 두 가지 구현 유지(**전환 기간 동안 임시적**)
- **레거시 변환**: 비제네릭 경로가 런타임에 `FilterClause`를 LINQ 표현식 트리로 변환(**임시적**)
- **문서화 부담**: 전환 기간 동안 어떤 인터페이스를 사용할지 설명해야 함
- **임시적 복잡성**: 레거시 인터페이스 제거 전까지 추가 유지보수 부담

**핵심 통찰**: "나쁜" 측면은 명시적으로 **임시적**입니다. 마이그레이션 기간 동안에만 존재하며, 향후 메이저 버전에서 레거시 인터페이스가 제거될 때 제거됩니다.

## 구현 하위 결정

이 섹션은 이중 인터페이스 패턴을 실현하는 데 필요한 특정 구현 선택을 문서화합니다.

### 하위 결정 1: 아키텍처 개요

이중 인터페이스 패턴은 두 개의 병렬 실행 경로를 만듭니다:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          ITextSearch 현대화                                   │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 인터페이스 레이어                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [Obsolete]                              [Modern]                            │
│  ITextSearch                             ITextSearch<TRecord>                │
│  ├─ TextSearchOptions                    ├─ TextSearchOptions<TRecord>       │
│  │  └─ TextSearchFilter                  │  └─ Expression<Func<T, bool>>     │
│  └─ RequiresDynamicCode 없음              └─ RequiresDynamicCode 없음         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 구현 레이어: 두 가지 패턴                                                      │
└──────────────────────────────────────────────────────────────────────────────┘

패턴 A: LINQ 직접 전달                     패턴 B: LINQ→레거시 변환
(VectorStoreTextSearch)                     (BingTextSearch, GoogleTextSearch 등)

┌──────────────────────────────┐           ┌──────────────────────────────────┐
│ VectorStoreTextSearch        │           │ BingTextSearch                   │
│ : ITextSearch                │           │ : ITextSearch                    │
│ : ITextSearch<TRecord>       │           │ : ITextSearch<BingWebPage>       │
├──────────────────────────────┤           ├──────────────────────────────────┤
│ 레거시 경로:                  │           │ 레거시 경로:                      │
│  TextSearchFilter            │           │  TextSearchFilter                │
│       ↓                      │           │       ↓                          │
│  BuildFilterExpression()     │           │  Bing API 매개변수               │
│  (절 → LINQ 트리)            │           │       ↓                          │
│       ↓                      │           │  HTTP GET 요청                   │
│  VectorSearchOptions.Filter  │           │                                  │
│       ↓                      │           │ 현대적 경로:                      │
│  벡터 저장소                  │           │  Expression<Func<T, bool>>       │
│                              │           │       ↓                          │
│ 현대적 경로:                  │           │  LINQ 트리 분석                   │
│  Expression<Func<T, bool>>   │           │       ↓                          │
│       ↓                      │           │  TextSearchFilter (변환)          │
│  VectorSearchOptions.Filter  │           │       ↓                          │
│  (직접 전달)                  │           │  레거시 경로로 위임               │
│       ↓                      │           │                                  │
│  벡터 저장소                  │           │                                  │
└──────────────────────────────┘           └──────────────────────────────────┘

핵심: 두 경로 모두                       핵심: 현대적이 레거시로 변환
     VectorSearchOptions.Filter 사용          기존 구현 재사용
```

**핵심 아키텍처 특성**:

1. **인터페이스 레이어**: 두 개의 별도 인터페이스: 레거시(`ITextSearch`)와 현대적(`ITextSearch<TRecord>`)
2. **패턴 A (VectorStoreTextSearch)**: 두 경로 모두 `VectorSearchOptions.Filter`에 수렴 — 레거시 절은 `BuildFilterExpression()`을 통해 LINQ 표현식 트리로 변환되고, 현대적 경로는 LINQ를 직접 전달
3. **패턴 B (웹 커넥터)**: LINQ 표현식이 레거시 `TextSearchFilter`로 변환된 다음 기존 구현에 위임
4. **RequiresDynamicCode**: 없음 - 인터페이스 또는 구현에 `[RequiresDynamicCode]` 속성 없음
5. **AOT 호환성**: 두 인터페이스 모두 AOT 호환(컴파일이나 런타임을 차단하는 속성 없음)

### 하위 결정 2: 두 가지 구현 패턴

모든 구현은 이중 인터페이스 패턴을 따르지만, 기저 서비스 기능에 따라 **두 가지 다른 실행 전략**을 사용합니다:

#### 패턴 A: LINQ 직접 전달 (VectorStoreTextSearch)

VectorStoreTextSearch는 **두** 코드 경로 모두에 `VectorSearchOptions.Filter` (LINQ)를 사용합니다. 레거시 경로는 `BuildFilterExpression()`을 통해 `FilterClause` 값을 LINQ 표현식 트리로 변환합니다 — 이는 순수한 데이터 구조 구성이며 완전히 AOT 호환됩니다:

```csharp
#pragma warning disable CS0618 // ITextSearch는 더 이상 사용되지 않음 - 하위 호환성
public sealed class VectorStoreTextSearch<TRecord> : ITextSearch, ITextSearch<TRecord>
#pragma warning restore CS0618
{
    // ===== 레거시 경로 (비제네릭 인터페이스) =====
    public Task<KernelSearchResults<string>> SearchAsync(
        string query,
        TextSearchOptions? searchOptions = null,
        CancellationToken cancellationToken = default)
    {
        var searchResponse = ExecuteVectorSearchAsync(query, searchOptions, cancellationToken);
        return Task.FromResult(CreateStringSearchResponse(searchResponse));
    }

    // ===== 현대적 경로 (제네릭 인터페이스) =====
    Task<KernelSearchResults<string>> ITextSearch<TRecord>.SearchAsync(
        string query,
        TextSearchOptions<TRecord>? searchOptions,
        CancellationToken cancellationToken)
    {
        var searchResponse = ExecuteVectorSearchAsync(query, searchOptions, cancellationToken);
        return Task.FromResult(CreateStringSearchResponse(searchResponse));
    }

    // 레거시 경로: FilterClauses를 LINQ 표현식 트리로 변환
    private async IAsyncEnumerable<VectorSearchResult<TRecord>> ExecuteVectorSearchAsync(
        string query, TextSearchOptions? searchOptions, ...)
    {
        var vectorSearchOptions = new VectorSearchOptions<TRecord> {
            Filter = searchOptions.Filter?.FilterClauses is not null
                ? BuildFilterExpression(searchOptions.Filter.FilterClauses)
                : null,
        };
        // ... 실행
    }

    // 현대적 경로: LINQ 직접 전달 - 더 이상 사용되지 않는 API 없음
    private async IAsyncEnumerable<VectorSearchResult<TRecord>> ExecuteVectorSearchAsync(
        string query, TextSearchOptions<TRecord>? searchOptions, ...)
    {
        var vectorSearchOptions = new VectorSearchOptions<TRecord> {
            Filter = searchOptions.Filter,  // LINQ 직접 전달 - 변환 없음
        };
        // ... 실행
    }
}
```

#### 패턴 B: LINQ→레거시 변환 (웹 검색 커넥터)

BingTextSearch, GoogleTextSearch, TavilyTextSearch, BraveTextSearch는 제네릭 인터페이스 호출을 레거시 형식으로 변환합니다:

```csharp
#pragma warning disable CS0618 // ITextSearch는 더 이상 사용되지 않음
public sealed class BingTextSearch : ITextSearch, ITextSearch<BingWebPage>
#pragma warning restore CS0618
{
    // ===== 레거시 경로 (비제네릭 인터페이스) =====
    public Task<KernelSearchResults<string>> SearchAsync(
        string query,
        TextSearchOptions? searchOptions = null,
        CancellationToken cancellationToken = default)
    {
        // TextSearchFilter를 사용한 직접 Bing API 호출
        // ... 기존 로직
    }

    // ===== 현대적 경로 (제네릭 인터페이스) =====
    Task<KernelSearchResults<string>> ITextSearch<BingWebPage>.SearchAsync(
        string query,
        TextSearchOptions<BingWebPage>? searchOptions,
        CancellationToken cancellationToken)
    {
        // 제네릭 옵션을 레거시 형식으로 변환
        var legacyOptions = searchOptions != null
            ? ConvertToLegacyOptions(searchOptions)
            : new TextSearchOptions();

        // 기존 레거시 구현에 위임
        return this.SearchAsync(query, legacyOptions, cancellationToken);
    }

    // LINQ→TextSearchFilter 변환
    private static TextSearchOptions ConvertToLegacyOptions<TRecord>(
        TextSearchOptions<TRecord> genericOptions)
    {
        return new TextSearchOptions
        {
            Top = genericOptions.Top,
            Skip = genericOptions.Skip,
            Filter = genericOptions.Filter != null
                ? ConvertLinqExpressionToBingFilter(genericOptions.Filter)
                : null
        };
    }

    // 표현식 트리 분석 및 Bing API 구문으로 매핑
    private static TextSearchFilter ConvertLinqExpressionToBingFilter<TRecord>(
        Expression<Func<TRecord, bool>> linqExpression)
    {
        var filter = new TextSearchFilter();
        // 표현식 트리를 재귀적으로 처리:
        // - 동등성 (==) → language:en
        // - 부등식 (!=) → -language:fr
        // - Contains() → intitle:"AI" 또는 inbody:"term"
        // - AND (&&) → 여러 필터 절
        ProcessExpression(linqExpression.Body, filter);
        return filter;
    }
}
```

**핵심 차이점**:

| 측면 | 패턴 A (VectorStoreTextSearch) | 패턴 B (웹 커넥터) |
| ---------------------- | -------------------------------------------- | -------------------------------------------- |
| **실행 경로** | 두 개의 독립적인 경로 | 현대적이 레거시로 변환 |
| **변환 레이어** | 변환 없음 | LINQ → TextSearchFilter |
| **레거시 경로** | 더 이상 사용되지 않는 `VectorSearchFilter.OldFilter` 사용 | 기존 `TextSearchFilter` 직접 사용 |
| **현대적 경로** | `VectorSearchOptions.Filter` 직접 사용 | LINQ 변환 후 레거시 경로에 위임 |
| **성능** | 오버헤드 없음 (직접 전달) | 변환 오버헤드는 허용 가능 (네트워크 I/O) |
| **기저 지원** | 네이티브 LINQ 지원 | API별 매개변수 매핑 |

**두 가지 패턴이 필요한 이유?**

1. **VectorStoreTextSearch**: 기저 벡터 저장소가 `VectorSearchOptions<TRecord>.Filter`를 통해 LINQ 표현식을 네이티브로 지원합니다. 직접 전달로 오버헤드를 제거합니다.
2. **웹 커넥터**: 기저 API(Bing, Google)는 LINQ를 받지 않습니다. TextSearchFilter로 변환한 다음 API 매개변수로 변환하여 호환성을 유지합니다.

**참고**: 두 패턴 모두 **임시 마이그레이션 전략**으로 이중 코드 경로(레거시 + 현대적)를 유지합니다. 더 이상 사용되지 않는 `ITextSearch` 인터페이스가 향후 메이저 버전에서 제거되면, 현대적 LINQ 경로만 남아 이중 구현 복잡성이 제거됩니다.

### 하위 결정 3: AOT 호환성 전략

두 인터페이스 모두 **`[RequiresDynamicCode]` 속성 없이** AOT 호환되도록 설계되었습니다:

**비제네릭 인터페이스 (`ITextSearch`)**:

- ✅ 완전히 AOT 호환
- `TextSearchFilter`(절 기반, LINQ 없음) 사용
- 동적 코드 생성 불필요

**제네릭 인터페이스 (`ITextSearch<TRecord>`)**:

- ✅ AOT 호환
- LINQ 표현식 사용
- 동적 코드 생성이 아닌 **표현식 트리 분석**을 통해 처리
- `[RequiresDynamicCode]` 속성 불필요

**LINQ 표현식 처리**:

```csharp
// 단순 동등성 - AOT 호환
filter = doc => doc.Department == "HR" && doc.IsActive

// 복잡한 표현식 - AOT 호환 (표현식 트리 분석)
filter = doc => doc.Tags.Any(tag => tag.Contains("urgent"))
```

**AOT 호환성 매트릭스**:

| 시나리오 | ITextSearch | ITextSearch&lt;TRecord&gt; | 비고 |
| ------------------------------ | ----------------- | -------------------------- | ----------------------------- |
| 단순 검색 (필터링 없음) | ✅ AOT 호환 | ✅ AOT 호환 | 동적 코드 불필요 |
| TextSearchFilter 기반 | ✅ AOT 호환 | N/A | 레거시 절 기반 필터링 |
| 단순 LINQ (동등성) | N/A | ✅ AOT 호환 | 표현식 트리 분석 |
| 복잡한 LINQ (Contains, Any) | N/A | ✅ AOT 호환 | 표현식 트리 분석 |

### 하위 결정 4: 웹 검색 커넥터를 위한 Contains() 지원

**맥락**: `ITextSearch<TRecord>` 인터페이스는 `Title.Contains("value")` 패턴을 포함한 LINQ 표현식을 지원합니다. 다양한 검색 엔진 API는 서로 다른 기능을 가지고 있습니다:

- **Bing**: 네이티브 고급 검색 연산자 (`intitle:`, `inbody:`, `url:`)
- **Google**: 특수 API 매개변수 (추가 검색어를 위한 `orTerms`)
- **Brave/Tavily**: 필드별 연산자가 없는 일반 검색 API

**결정**: Brave 및 Tavily 검색 엔진에 대해 **쿼리 보강**을 사용하여 `Title.Contains()` 지원을 구현합니다:

1. **SearchQueryFilterClause**: 결과를 필터링하는 대신 검색 쿼리에 용어를 추가하는 새로운 필터 절 타입
2. **쿼리 보강 패턴**: `SearchQueryFilterClause` 인스턴스에서 용어를 추출하여 기본 검색 쿼리에 추가
3. **이중 처리**: `SearchQueryFilterClause`를 일반 필터 절과 다르게 처리

**구현 패턴**:

```csharp
// LINQ 표현식: results.Where(r => r.Title.Contains("AI"))
// 변환 대상: new SearchQueryFilterClause("AI")
// 쿼리 보강: "원래 쿼리" + " AI"
```

**검토한 대안**:

1. **직접 API 매개변수**: Brave/Tavily API에서 사용 불가
2. **검색 후 필터링**: 결과 관련성 및 성능 저하
3. **NotSupportedException**: LINQ 표현식 기능 제한

**결과**:

- ✅ 검색 엔진 전반에 걸친 일관된 LINQ 표현식 지원
- ✅ 결과를 필터링하는 대신 쿼리를 수정하여 검색 관련성 향상
- ✅ 향후 Contains() 구현을 위한 확장 가능한 패턴
- ⚠️ 검색 엔진 간 다른 구현 접근 방식 (일관성 우려)
- ⚠️ 필터 절 처리의 추가 복잡성

### 하위 결정 5: SearchQueryFilterClause 위치 및 FilterClause 생성자 가시성

**맥락**: `SearchQueryFilterClause`는 `Plugins.Web`의 웹 검색 커넥터(Brave, Tavily)에서만 사용됩니다. 공개 API 표면을 최소화하기 위해 소비자와 같은 어셈블리에 위치해야 합니다.

**문제**: `FilterClause` 기본 클래스는 원래 **internal 생성자**를 가지고 있어 `VectorData.Abstractions` 어셈블리 외부에서의 상속을 차단했습니다:

```csharp
public abstract class FilterClause
{
    internal FilterClause()  // ← 외부 상속 차단
}
```

`SearchQueryFilterClause`를 `Plugins.Web`으로 이동하면 다음과 같은 오류가 발생했습니다:

```
error CS0122: 'FilterClause.FilterClause()' is inaccessible due to its protection level
```

**결정**: `FilterClause` 생성자를 **`protected`**로 변경하고 `SearchQueryFilterClause`를 `Plugins.Web`에 **`internal sealed`**로 이동합니다.

```csharp
// VectorData.Abstractions에서
public abstract class FilterClause
{
    protected FilterClause()  // internal → protected
}

// Plugins.Web에서
internal sealed class SearchQueryFilterClause : FilterClause
```

**근거**:

- **최소 API 표면**: `SearchQueryFilterClause`가 internal로 유지됨 (public 아님)
- **제어된 확장성**: `protected`는 상속을 허용하면서 캡슐화를 유지
- **올바른 위치**: 클래스가 실제로 사용되는 `Plugins.Web`에 위치
- **표준 패턴**: `protected` 생성자는 추상 기본 클래스에서 일반적

**검토한 대안**:

1. **internal 생성자 유지 + VectorData에 public SearchQueryFilterClause**: 불필요한 public API 추가
2. **Internal + InternalsVisibleTo**: CI에서 200개의 CS0436 타입 충돌 오류 발생
3. **Public 생성자**: 너무 허용적, 무제한 외부 필터 타입 허용
4. **FilterClause에서 상속하지 않음**: 확립된 패턴 위반, 타입 안전성 상실

**결과**:

- ✅ 최소 공개 API 영향 (기존 추상 클래스의 생성자 가시성 변경만)
- ✅ `SearchQueryFilterClause`가 내부 구현 세부사항으로 유지
- ✅ VectorData 어셈블리 외부에서의 향후 필터 절 구현 가능
- ✅ 우회 방법 없는 깔끔한 구현

### 하위 결정 6: Obsolete 표시 전략

**결정**: 원래 `ITextSearch` 인터페이스에 즉시 `[Obsolete]` 속성을 표시합니다:

```csharp
[Obsolete("ITextSearch is deprecated. Use ITextSearch<TRecord> with LINQ filtering instead.")]
public interface ITextSearch
{
    // 레거시 구현
}
```

**Obsolete 표시의 목적**:

1. **개발자 안내**: 컴파일 타임 경고가 이 API를 새 코드에서 사용하지 말아야 함을 알림
2. **마이그레이션 신호**: 이 인터페이스가 향후 메이저 버전에서 제거될 것이라는 명확한 표시
3. **생태계 준비**: 라이브러리 소비자에게 마이그레이션 작업을 계획할 수 있는 사전 공지 제공
4. **IDE 지원**: 현대적 IDE가 사용 중단 경고를 표시하고 대안을 제안

**지금 Obsolete로 표시하는 이유** (기다리는 대신):

- 새 코드가 레거시 패턴을 채택하는 것을 방지
- 생태계 마이그레이션 시계를 즉시 시작
- API 진화에 대한 .NET 모범 사례와 정렬
- 실제 제거 전 충분한 마이그레이션 기간 허용 (일반적으로 1-2 메이저 버전)

## 마이그레이션 전략

이 결정은 레거시 절 기반 필터링에서 현대적 LINQ 기반 필터링으로의 **의도적인 3단계 마이그레이션 경로**를 구현합니다:

### 1단계: 전환 상태 (현재 - 이 ADR에서 구현)

- ✅ LINQ 필터링을 사용하는 `ITextSearch<TRecord>` 도입 (현대적, 권장)
- ✅ `ITextSearch`에 사용 중단 경고와 함께 `[Obsolete]` 표시
- ✅ 하위 호환성을 위해 두 인터페이스 공존
- ✅ 모든 구현이 두 인터페이스를 지원
- ✅ 제네릭 인터페이스를 권장하도록 문서 업데이트

**핵심 사항**: `ITextSearch`에 `[Obsolete]` 표시는 이중 목적을 가집니다:

- **즉각적**: 이 인터페이스가 더 이상 사용되지 않으며 새 코드에서 사용하지 말아야 한다는 개발자 신호
- **장기적**: 최종 제거를 위한 명확한 경로를 수립하여, 호환성을 깨는 변경 전에 생태계가 마이그레이션할 수 있도록 함

### 2단계: 사용 중단 강화 (향후 - 다음 메이저 버전)

- Obsolete 경고 심각도 증가 (`ObsoleteAttribute`에 `error: true`)
- 문서에 제거 일정 추가
- 지연된 마이그레이션을 위한 최종 마이그레이션 기간
- 생태계에 대한 커뮤니케이션 캠페인

### 3단계: 레거시 제거 (최종적으로 - 향후 메이저 버전)

- **호환성을 깨는 변경**: `ITextSearch` 인터페이스 완전 제거
- `TextSearchOptions`에서 `TextSearchFilter`의 공개 API 사용 제거
- `VectorSearchFilter.OldFilter` 제거
- 모든 레거시 공개 API 코드 경로 제거
- LINQ 표현식을 사용하는 단일 현대적 인터페이스만 남음
- **참고**: `TextSearchFilter` 및 `FilterClause` 타입은 웹 플러그인 전용 LINQ 변환 레이어로 내부적으로 유지됨; 벡터 저장소는 `VectorSearchOptions<TRecord>.Filter`를 통해 LINQ 표현식을 직접 사용

**예상 일정**: 2단계는 다음 메이저 버전(예: SK 2.0), 3단계는 이후 메이저 버전(예: SK 3.0). 이는 생태계에 최소 1-2년의 마이그레이션 기간을 제공합니다.

### 마이그레이션 경로 다이어그램

```
1단계 (현재):
├─ 두 인터페이스 공존
├─ 레거시 ITextSearch에 [Obsolete] 표시
├─ 사용 중단 경고가 사용자를 ITextSearch<TRecord>로 안내
└─ 모든 구현이 두 인터페이스를 지원

2단계 (향후):
├─ 사용 중단 심각도 증가
├─ 경고에 제거 일정 추가
└─ 문서에서 마이그레이션 강조

3단계 (최종적으로):
├─ ITextSearch 인터페이스 제거
├─ TextSearchFilter 클래스 제거
├─ VectorSearchFilter.OldFilter 제거
└─ LINQ 표현식을 사용하는 단일 인터페이스
```

이중 인터페이스 패턴은 명시적으로 **임시적인 아키텍처 상태**이지 영구적인 설계가 아닙니다. 다음을 제공합니다:

- 기존 소비자를 위한 호환성을 깨지 않는 마이그레이션
- 사용 중단 경고를 통한 명확한 마이그레이션 신호
- 제거 전 생태계 채택을 위한 시간
- 향후 메이저 버전에서 기술 부채를 제거하는 능력

## 부록: 검토한 대안 옵션

이 섹션은 평가되었지만 선택되지 않은 대안 접근 방식을 문서화합니다.

### 옵션 1: 직접 LINQ 대체 (네이티브 LINQ 전용)

TextSearchFilter를 Expression<Func<T, bool>>로 완전히 대체합니다. 비제네릭 인터페이스를 완전히 제거합니다.

**평가**:

- 좋은 점, 강한 타입 안전성을 가진 균일한 API 설계
- 좋은 점, 모든 기술 부채를 즉시 제거
- 좋은 점, 전체 표현식 지원을 갖춘 최상의 장기 아키텍처
- 좋은 점, Microsoft.Extensions.VectorData 패턴과 정렬
- 나쁜 점, **호환성을 깨는 변경**: 모든 소비자가 마이그레이션해야 함
- 나쁜 점, 전이적 종속성에 대한 높은 혼란 비용

**선택하지 않은 이유**: 안정적인 API에 대한 호환성을 깨는 변경은 허용 불가.

### 옵션 2: 네이티브 LINQ + 변환 레이어

두 인터페이스를 모두 유지하되 TextSearchFilter를 내부적으로 LINQ로 변환합니다.

**평가**:

- 좋은 점, 더 이상 사용되지 않는 API 사용을 피함 (VectorSearchFilter 종속성 없음)
- 좋은 점, 단일 구현 경로 재사용
- 좋은 점, 표현식 트리 구축은 순수한 데이터 구조 구성이며 완전히 AOT 호환
- 나쁜 점, 변환 오버헤드 도입 (단순 동등성 절에 대해서는 최소)

**업데이트**: 이 옵션은 `RequiresDynamicCode`가 모든 TextSearch API에 전파될 것이라는 잘못된 평가를 기반으로 원래 거부되었습니다. 실제로 표현식 트리 **구축** (`Expression.Property`, `Expression.Equal`, `Expression.Lambda`)은 완전히 AOT 호환됩니다 — 표현식 트리 **컴파일** (`Expression.Compile()`)만이 동적 코드 생성을 필요로 합니다. MEVD의 `VectorSearchOptions<TRecord>.Filter`가 표현식 트리를 컴파일하지 않고 분석하므로 AOT 비호환성이 없습니다. 이 접근 방식은 MEVD가 1.0 공급자 버전 게시 전에 더 이상 사용되지 않는 `OldFilter` 속성을 제거할 수 있도록 `VectorStoreTextSearch` 레거시 경로에서 채택되었습니다.

### 옵션 3: 어댑터 패턴

기존 구현에 대한 래퍼로 제네릭 인터페이스를 구현합니다.

**평가**:

- 좋은 점, 기존 구현에 대한 최소한의 코드 변경
- 좋은 점, 관심사의 명확한 분리
- 나쁜 점, 불필요한 추상화 레이어 추가
- 나쁜 점, 모든 작업에 대한 변환 오버헤드
- 나쁜 점, 기저 기술 부채를 해결하지 못함

**선택하지 않은 이유**: 더 이상 사용되지 않는 API 종속성이라는 핵심 문제를 해결하지 못함.

### 옵션 4: 점진적 마이그레이션 (사용 중단 및 도입)

TextSearchFilter를 사용 중단하고 동일 인터페이스 내에서 LINQ를 도입합니다.

**평가**:

- 좋은 점, 유지할 단일 인터페이스
- 나쁜 점, 어떤 필터 메커니즘을 사용할지에 대한 모호성 생성
- 나쁜 점, 복잡한 런타임 타입 검사 필요
- 나쁜 점, 명확한 마이그레이션 경로를 제공하지 못함

**선택하지 않은 이유**: 모호한 API 설계와 불량한 개발자 경험.

## 추가 정보

### 관련 결정

- ADR-0058: 업데이트된 벡터 검색 설계 (LINQ 기반 필터링 기초 수립)
- ADR-0059: 텍스트 검색 추상화 (ITextSearch 인터페이스 요구사항 정의)

### 보안 고려사항

LINQ 표현식은 서버 측에서만 처리됩니다. 사용자 제공 표현식 실행 없음. 표현식 트리 분석은 실행 전에 지원되는 작업을 검증합니다. 지원되지 않는 작업은 명확한 오류 메시지와 함께 ArgumentException을 발생시킵니다.

### 호환성을 깨는 변경 분석

즉각적인 호환성을 깨는 변경 없음:

- 기존 TextSearchFilter 기반 코드가 계속 작동
- 새로운 제네릭 인터페이스는 추가적임
- 마이그레이션 경로 문서화
- 사용 중단 경고가 향후 마이그레이션을 안내
