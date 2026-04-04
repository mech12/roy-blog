---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: proposed
contact: westey-m
date: 2024-08-14
deciders: sergeymenshykh, markwallace, rbarreto, dmytrostruk, westey-m, matthewbolanos, eavanvalkenburg
consulted: stephentoub, dluc, ajcvickers, roji
informed: 
---

# 업데이트된 벡터 검색 설계

## 요구 사항

1. 벡터를 통한 검색 지원.
1. 다양한 타입의 요소를 가진 벡터를 지원하고 향후 새로운 벡터 타입(예: sparse)을 지원할 수 있는 확장성 허용.
1. 텍스트를 통한 검색 지원. 이는 서비스가 임베딩 생성을 수행하거나 임베딩 생성이 파이프라인에서 수행되는 시나리오를 지원하기 위해 필요합니다.
1. 다른 모달리티, 예: 이미지로 검색하기 위한 확장성 허용.
1. 하이브리드 검색을 수행하기 위한 확장성 허용.
1. 향후 확장 가능성이 있는 기본 필터링 허용.
1. 검색 경험을 단순화하는 확장 메서드 제공.

## 인터페이스

벡터 검색 인터페이스는 `VectorSearchQuery` 객체를 받습니다. 이 객체는 다양한 유형의 검색을 나타내는 여러 하위 클래스를 가진 추상 기본 클래스입니다.

```csharp
interface IVectorSearch<TRecord>
{
    IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync(
        VectorSearchQuery vectorQuery,
        CancellationToken cancellationToken = default);
}
```

각 `VectorSearchQuery` 하위 클래스는 특정 유형의 검색을 나타냅니다.
가능한 변형은 `VectorSearchQuery`와 모든 하위 클래스가 내부 생성자를 가진다는 사실에 의해 제한됩니다.
따라서 개발자는 커스텀 검색 쿼리 타입을 만들어 `IVectorSearch.SearchAsync`로 실행할 수 없습니다.
그러나 이러한 방식으로 하위 클래스를 가지면, 각 쿼리가 서로 다른 파라미터와 옵션을 가질 수 있습니다.

```csharp
// 모든 벡터 검색 쿼리의 기본 클래스.
abstract class VectorSearchQuery(
    string queryType,
    object? searchOptions)
{
    public static VectorizedSearchQuery<TVector> CreateQuery<TVector>(TVector vector, VectorSearchOptions? options = default) => new(vector, options);
    public static VectorizableTextSearchQuery CreateQuery(string text, VectorSearchOptions? options = default) => new(text, options);

    // 향후 확장 가능성 예시.
    public static HybridTextVectorizedSearchQuery<TVector> CreateHybridQuery<TVector>(TVector vector, string text, HybridVectorSearchOptions? options = default) => new(vector, text, options);
    public static HybridVectorizableTextSearchQuery CreateHybridQuery(string text, HybridVectorSearchOptions? options = default) => new(text, options);
}

// 벡터를 사용한 벡터 검색.
class VectorizedSearchQuery<TVector>(
    TVector vector,
    VectorSearchOptions? searchOptions) : VectorSearchQuery;

// 다운스트림에서 벡터화될 쿼리 텍스트를 사용한 벡터 검색.
class VectorizableTextSearchQuery(
    string queryText,
    VectorSearchOptions? searchOptions) : VectorSearchQuery;

// 벡터와 키워드 검색에 사용될 텍스트 부분을 사용한 하이브리드 검색.
class HybridTextVectorizedSearchQuery<TVector>(
    TVector vector,
    string queryText,
    HybridVectorSearchOptions? searchOptions) : VectorSearchQuery;

// 다운스트림에서 벡터화되고 키워드 검색에도 사용될 텍스트를 사용한 하이브리드 검색.
class HybridVectorizableTextSearchQuery(
    string queryText,
    HybridVectorSearchOptions? searchOptions) : VectorSearchQuery

// 기본 벡터 검색 옵션.
public class VectorSearchOptions
{
    public static VectorSearchOptions Default { get; } = new VectorSearchOptions();
    public VectorSearchFilter? Filter { get; init; } = new VectorSearchFilter();
    public string? VectorFieldName { get; init; }
    public int Limit { get; init; } = 3;
    public int Offset { get; init; } = 0;
    public bool IncludeVectors { get; init; } = false;
}

// 하이브리드 벡터 검색 옵션.
public sealed class HybridVectorSearchOptions
{
    public static HybridVectorSearchOptions Default { get; } = new HybridVectorSearchOptions();
    public VectorSearchFilter? Filter { get; init; } = new VectorSearchFilter();
    public string? VectorFieldName { get; init; }
    public int Limit { get; init; } = 3;
    public int Offset { get; init; } = 0;
    public bool IncludeVectors { get; init; } = false;

    public string? HybridFieldName { get; init; }
}
```

CreateQuery를 호출하지 않고 검색을 간소화하기 위해 확장 메서드를 사용할 수 있습니다.
예: `SearchAsync(VectorSearchQuery.CreateQuery(vector))` 대신 `SearchAsync(vector)`를 호출할 수 있습니다.

```csharp
public static class VectorSearchExtensions
{
    public static IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync<TRecord, TVector>(
        this IVectorSearch<TRecord> search,
        TVector vector,
        VectorSearchOptions? options = default,
        CancellationToken cancellationToken = default)
        where TRecord : class
    {
        return search.SearchAsync(new VectorizedSearchQuery<TVector>(vector, options), cancellationToken);
    }

    public static IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync<TRecord>(
        this IVectorSearch<TRecord> search,
        string searchText,
        VectorSearchOptions? options = default,
        CancellationToken cancellationToken = default)
        where TRecord : class
    {
        return search.SearchAsync(new VectorizableTextSearchQuery(searchText, options), cancellationToken);
    }

    // 등등...
}
```

## 사용 예시

```csharp
public sealed class Glossary
{
    [VectorStoreRecordKey]
    public ulong Key { get; set; }
    [VectorStoreRecordData]
    public string Category { get; set; }
    [VectorStoreRecordData]
    public string Term { get; set; }
    [VectorStoreRecordData]
    public string Definition { get; set; }
    [VectorStoreRecordVector(1536)]
    public ReadOnlyMemory<float> DefinitionEmbedding { get; set; }
}

public async Task VectorSearchAsync(IVectorSearch<Glossary> vectorSearch)
{
    var searchEmbedding = new ReadOnlyMemory<float>(new float[1536]);

    // 벡터 검색.
    var searchResults = vectorSearch.SearchAsync(VectorSearchQuery.CreateQuery(searchEmbedding));
    searchResults = vectorSearch.SearchAsync(searchEmbedding); // 확장 메서드.

    // 특정 벡터 필드로 벡터 검색.
    searchResults = vectorSearch.SearchAsync(VectorSearchQuery.CreateQuery(searchEmbedding, new() { VectorFieldName = nameof(Glossary.DefinitionEmbedding) }));
    searchResults = vectorSearch.SearchAsync(searchEmbedding, new() { VectorFieldName = nameof(Glossary.DefinitionEmbedding) }); // 확장 메서드.

    // 텍스트 벡터 검색.
    searchResults = vectorSearch.SearchAsync(VectorSearchQuery.CreateQuery("What does Semantic Kernel mean?"));
    searchResults = vectorSearch.SearchAsync("What does Semantic Kernel mean?"); // 확장 메서드.

    // 특정 벡터 필드로 텍스트 벡터 검색.
    searchResults = vectorSearch.SearchAsync(VectorSearchQuery.CreateQuery("What does Semantic Kernel mean?", new() { VectorFieldName = nameof(Glossary.DefinitionEmbedding) }));
    searchResults = vectorSearch.SearchAsync("What does Semantic Kernel mean?", new() { VectorFieldName = nameof(Glossary.DefinitionEmbedding) }); // 확장 메서드.

    // 하이브리드 벡터 검색.
    searchResults = vectorSearch.SearchAsync(VectorSearchQuery.CreateHybridQuery(searchEmbedding, "What does Semantic Kernel mean?", new() { HybridFieldName = nameof(Glossary.Definition) }));
    searchResults = vectorSearch.HybridVectorizedTextSearchAsync(searchEmbedding, "What does Semantic Kernel mean?", new() { HybridFieldName = nameof(Glossary.Definition) }); // 확장 메서드.

    // 벡터 및 키워드 검색 모두에 필드 이름이 지정된 하이브리드 텍스트 벡터 검색.
    searchResults = vectorSearch.SearchAsync(VectorSearchQuery.CreateHybridQuery("What does Semantic Kernel mean?", new() { VectorFieldName = nameof(Glossary.DefinitionEmbedding), HybridFieldName = nameof(Glossary.Definition) }));
    searchResults = vectorSearch.HybridVectorizableTextSearchAsync("What does Semantic Kernel mean?", new() { VectorFieldName = nameof(Glossary.DefinitionEmbedding), HybridFieldName = nameof(Glossary.Definition) }); // 확장 메서드.

    // 향후 이미지 또는 다른 모달리티도 지원 가능, 예:
    IVectorSearch<Images> imageVectorSearch = ...
    searchResults = imageVectorSearch.SearchAsync(VectorSearchQuery.CreateBase64EncodedImageQuery(base64EncodedImageString, new() { VectorFieldName = nameof(Images.ImageEmbedding) }));

    // 필터링이 있는 벡터 검색.
    var filter = new BasicVectorSearchFilter().EqualTo(nameof(Glossary.Category), "Core Definitions");
    searchResults = vectorSearch.SearchAsync(
        VectorSearchQuery.CreateQuery(
            searchEmbedding,
            new()
            {
                Filter = filter,
                VectorFieldName = nameof(Glossary.DefinitionEmbedding)
            }));
}
```

## 고려된 옵션

### 옵션 1: 검색 객체

위의 [인터페이스](#인터페이스) 섹션에서 이 옵션에 대한 설명을 참조하세요.

장점:

- 각각 다른 옵션을 가진 여러 쿼리 타입을 지원할 수 있습니다.
- 호환성 깨짐 변경 없이 향후 더 많은 쿼리 타입을 쉽게 추가할 수 있습니다.

단점:

- 커넥터 구현에서 지원하지 않는 쿼리 타입은 예외를 발생시킵니다.

### 옵션 2: 벡터 전용

추상화는 가장 기본적인 기능만 지원하고 다른 모든 기능은 구체적인 구현에서 지원합니다.
예: 일부 벡터 데이터베이스는 서비스에서 임베딩 생성을 지원하지 않으므로, 커넥터는 옵션 1의 `VectorizableTextSearchQuery`를 지원하지 않습니다.

장점:

- 어떤 쿼리 타입이 어떤 벡터 스토어 커넥터 타입에서 지원되는지 사용자가 알 필요가 없습니다.

단점:

- 추상화에서 벡터로만 검색할 수 있어 매우 낮은 공통 분모입니다.

```csharp
interface IVectorSearch<TRecord>
{
    IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync<TVector>(
        TVector vector,
        VectorSearchOptions? searchOptions
        CancellationToken cancellationToken = default);
}

class AzureAISearchVectorStoreRecordCollection<TRecord> : IVectorSearch<TRecord>
{
    public IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync<TVector>(
        TVector vector,
        VectorSearchOptions? searchOptions
        CancellationToken cancellationToken = default);

    public IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync(
        string queryText,
        VectorSearchOptions? searchOptions
        CancellationToken cancellationToken = default);
}
```

### 옵션 3: 추상 기본 클래스

주요 요구 사항 중 하나는 추가 쿼리 타입으로의 향후 확장성을 허용하는 것입니다.
이를 달성하는 한 가지 방법은 각 구현에서 재정의하지 않는 한 NotSupported로 throw하는 새 메서드를 자동 구현할 수 있는 추상 기본 클래스를 사용하는 것입니다. 이 동작은 옵션 1과 유사합니다. 옵션 1에서는 확장 메서드를 통해 동일한 동작이 달성됩니다.
메서드 세트는 옵션 1과 옵션 3에서 동일하게 됩니다. 다만 옵션 1에는 `VectorSearchQuery`를 입력으로 받는 Search 메서드도 있습니다.

`IVectorSearch`는 `IVectorStoreRecordCollection`과 별도의 인터페이스이지만, `IVectorStoreRecordCollection`이 `IVectorSearch`를 상속하도록 의도되어 있습니다.

이는 `IVectorSearch`의 일부(대부분의) 구현이 `IVectorStoreRecordCollection` 구현의 일부가 됨을 의미합니다.
스토어가 검색을 지원하지만 반드시 쓰기가 가능하지 않은 독립 실행형 `IVectorSearch` 구현을 지원해야 하는 경우를 예상합니다.

따라서 추상 기본 클래스의 계층 구조가 필요합니다.

또한 기본 인터페이스 메서드를 고려했지만, .net Framework에서는 이에 대한 지원이 없으며, SK는 .net Framework를 지원해야 합니다.

장점:

- 각각 다른 옵션을 가진 여러 쿼리 타입을 지원할 수 있습니다.
- 호환성 깨짐 변경 없이 향후 더 많은 쿼리 타입을 쉽게 추가할 수 있습니다.
- 각 검색 타입에 대해 다른 반환 타입 허용.

단점:

- 커넥터 구현에서 지원하지 않는 쿼리 타입은 예외를 발생시킵니다.
- 다중 상속을 지원하지 않아, 여러 키 타입을 지원해야 하는 경우 작동하지 않습니다.
- 다중 상속을 지원하지 않아, `VectorStoreRecordCollection`에 추가 기능을 추가해야 하는 경우 유사한 메커니즘을 사용할 수 없습니다.

```csharp
abstract class BaseVectorSearch<TRecord>
    where TRecord : class
{
    public virtual IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync<TVector>(
        this IVectorSearch<TRecord> search,
        TVector vector,
        VectorSearchOptions? options = default,
        CancellationToken cancellationToken = default)
    {
        throw new NotSupportedException($"Vectorized search is not supported by the {this._connectorName} connector");
    }

    public virtual IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync(
        this IVectorSearch<TRecord> search,
        string searchText,
        VectorSearchOptions? options = default,
        CancellationToken cancellationToken = default)
    {
        throw new NotSupportedException($"Vectorizable text search is not supported by the {this._connectorName} connector");
    }
}

abstract class BaseVectorStoreRecordCollection<TKey, TRecord> : BaseVectorSearch<TRecord>
{
    public virtual async Task CreateCollectionIfNotExistsAsync(CancellationToken cancellationToken = default)
    {
        if (!await this.CollectionExistsAsync(cancellationToken).ConfigureAwait(false))
        {
            await this.CreateCollectionAsync(cancellationToken).ConfigureAwait(false);
        }
    }
}

// 여기서 여러 타입의 키를 지원하지만, 여러 기본 클래스에서 상속할 수 없습니다.
class QdrantVectorStoreRecordCollection<TRecord> : BaseVectorStoreRecordCollection<ulong, TRecord> : BaseVectorStoreRecordCollection<Guid, TRecord>
{
}
```

### 옵션 4: 검색 타입별 인터페이스

주요 요구 사항 중 하나는 추가 쿼리 타입으로의 향후 확장성을 허용하는 것입니다.
이를 달성하는 한 가지 방법은 구현이 추가 기능을 지원할 때 추가 인터페이스를 추가하는 것입니다.

장점:

- 다른 구현이 지원되지 않는 기능에 대해 예외를 throw할 필요 없이 서로 다른 검색 타입을 지원할 수 있습니다.
- 각 검색 타입에 대해 다른 반환 타입 허용.

단점:

- 사용자가 각 구현에서 어떤 인터페이스가 구현되어 있는지 알아야 하며, 필요에 따라 캐스팅해야 합니다.
- 호환성 깨짐 변경이 되므로 시간이 지남에 따라 `IVectorStoreRecordCollection`에 더 많은 검색 기능을 추가할 수 없습니다. 따라서 `IVectorStoreRecordCollection` 인스턴스를 가지고 있지만 예: 하이브리드 검색을 하고 싶은 사용자는, 먼저 `IHybridTextVectorizedSearch`로 캐스팅해야 검색할 수 있습니다.

```csharp

// 벡터를 사용한 벡터 검색.
interface IVectorizedSearch<TRecord>
{
    IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync<TVector>(
        TVector vector,
        VectorSearchOptions? searchOptions);
}

// 다운스트림에서 벡터화될 쿼리 텍스트를 사용한 벡터 검색.
interface IVectorizableTextSearch<TRecord>
{
    IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync<TVector>(
        string queryText,
        VectorSearchOptions? searchOptions);
}

// 벡터와 키워드 검색에 사용될 텍스트 부분을 사용한 하이브리드 검색.
interface IHybridTextVectorizedSearch<TRecord>
{
    IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync<TVector>(
        TVector vector,
        string queryText,
        HybridVectorSearchOptions? searchOptions);
}

// 다운스트림에서 벡터화되고 키워드 검색에도 사용될 텍스트를 사용한 하이브리드 검색.
interface IHybridVectorizableTextSearch<TRecord>
{
    IAsyncEnumerable<VectorSearchResult<TRecord>> SearchAsync<TVector>(
    string queryText,
    HybridVectorSearchOptions? searchOptions);
}

class AzureAISearchVectorStoreRecordCollection<TRecord>: IVectorStoreRecordCollection<string, TRecord>, IVectorizedSearch<TRecord>, IVectorizableTextSearch<TRecord>
{
}

```

## 결정 결과

선택된 옵션: 4

합의점은 옵션 4가 사용자에게 이해하기 더 쉽다는 것이며, 모든 벡터 스토어에서 작동하는 기능만 기본적으로 노출됩니다.
