---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: proposed
contact: dmytrostruk
date: 2024-08-20
deciders: sergeymenshykh, markwallace, rbarreto, westey-m
---

# Entity Framework를 벡터 스토어 커넥터로 사용

## 컨텍스트 및 문제 설명

이 ADR은 Semantic Kernel 코드베이스에 Entity Framework를 벡터 스토어 커넥터로 추가하는 것에 대한 조사 결과를 포함합니다.

Entity Framework는 SQL Database(온프레미스 및 Azure), SQLite, MySQL, PostgreSQL, Azure Cosmos DB 등 다양한 데이터베이스에서 .NET(C#)으로 깔끔하고 이식 가능하며 고수준의 데이터 접근 계층을 구축할 수 있게 하는 현대적인 객체-관계 매퍼입니다. LINQ 쿼리, 변경 추적, 업데이트 및 스키마 마이그레이션을 지원합니다.

Semantic Kernel에 대한 Entity Framework의 큰 장점 중 하나는 여러 데이터베이스를 지원한다는 것입니다. 이론적으로 하나의 Entity Framework 커넥터가 여러 데이터베이스에 대한 허브 역할을 동시에 수행할 수 있어, 이러한 데이터베이스와의 통합 개발 및 유지 보수를 단순화할 수 있습니다.

그러나 Entity Framework가 업데이트된 벡터 스토어 설계에 맞지 않게 하는 몇 가지 제한 사항이 있습니다.

### 컬렉션 생성

새 벡터 스토어 설계에서 인터페이스 `IVectorStoreRecordCollection<TKey, TRecord>`는 데이터베이스 컬렉션을 조작하는 메서드를 포함합니다:
- `CollectionExistsAsync`
- `CreateCollectionAsync`
- `CreateCollectionIfNotExistsAsync`
- `DeleteCollectionAsync`

Entity Framework에서는 프로그래밍 방식의 컬렉션(스키마/테이블이라고도 함) 생성이 프로덕션 시나리오에서 권장되지 않습니다. 권장되는 접근 방식은 마이그레이션(코드 우선 접근 방식의 경우)을 사용하거나 리버스 엔지니어링(스캐폴딩/데이터베이스 우선 접근 방식이라고도 함)을 사용하는 것입니다. 프로그래밍 방식의 스키마 생성은 테스트/로컬 시나리오에서만 권장됩니다. 또한 컬렉션 생성 프로세스는 데이터베이스마다 다릅니다. 예를 들어 MongoDB EF Core 공급자는 스키마 마이그레이션이나 데이터베이스 우선/모델 우선 접근 방식을 지원하지 않습니다. 대신 컬렉션이 존재하지 않는 경우 문서가 처음 삽입될 때 자동으로 생성됩니다. 이는 `IVectorStoreRecordCollection<TKey, TRecord>` 인터페이스의 `CreateCollectionAsync`와 같은 메서드에 복잡성을 야기하는데, 대부분의 데이터베이스에서 작동하는 컬렉션 관리에 대한 추상화가 EF에 없기 때문입니다. 이러한 경우 권장되는 접근 방식은 자동 생성에 의존하거나 각 데이터베이스에 대해 개별적으로 컬렉션 생성을 처리하는 것입니다. 예를 들어 MongoDB에서는 MongoDB C# Driver를 직접 사용하는 것이 권장됩니다.

출처:
- https://learn.microsoft.com/en-us/ef/core/managing-schemas/
- https://learn.microsoft.com/en-us/ef/core/managing-schemas/ensure-created
- https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/applying?tabs=dotnet-core-cli#apply-migrations-at-runtime
- https://github.com/mongodb/mongo-efcore-provider?tab=readme-ov-file#not-supported--out-of-scope-features

### 키 관리

모든 데이터베이스가 모든 타입을 키로 지원하지는 않으므로, 하나의 유효한 키 타입 세트를 정의하는 것은 불가능합니다. 이 경우 `string`과 같은 표준 타입의 키만 지원하고, 특정 데이터베이스의 키 제약 사항을 충족하기 위해 변환을 수행해야 합니다. 이는 키 관리가 각 데이터베이스마다 개별적으로 처리되어야 하므로 통합 커넥터 구현의 이점을 제거합니다.

출처:
- https://learn.microsoft.com/en-us/ef/core/modeling/keys?tabs=data-annotations

### 벡터 관리

임베딩을 보유하기 위해 현재 대부분의 SK 커넥터에서 사용되는 `ReadOnlyMemory<T>` 타입은 Entity Framework에서 기본적으로 지원되지 않습니다. 이 타입을 사용하려고 하면 다음 오류가 발생합니다:

```
The property '{Property Name}' could not be mapped because it is of type 'ReadOnlyMemory<float>?', which is not a supported primitive type or a valid entity type. Either explicitly map this property, or ignore it using the '[NotMapped]' attribute or by using 'EntityTypeBuilder.Ignore' in 'OnModelCreating'.
```

그러나 `byte[]` 타입을 사용하거나 `ReadOnlyMemory<T>`를 지원하기 위해 명시적 매핑을 생성할 수 있습니다. 이것은 `pgvector` 패키지에서 이미 구현되어 있지만, 다른 데이터베이스에서도 작동하는지는 명확하지 않습니다.

출처: 
- https://github.com/pgvector/pgvector-dotnet/blob/master/README.md#entity-framework-core
- https://github.com/pgvector/pgvector-dotnet/blob/master/src/Pgvector/Vector.cs
- https://github.com/pgvector/pgvector-dotnet/blob/master/src/Pgvector.EntityFrameworkCore/VectorTypeMapping.cs

### 테스트

Entity Framework 커넥터를 만들고 SQLite 데이터베이스를 사용하여 테스트를 작성하는 것이 다른 EF 지원 데이터베이스에서도 이 통합이 작동한다는 것을 의미하지는 않습니다. 각 데이터베이스는 자체적인 Entity Framework 기능 세트를 구현하므로, Entity Framework 커넥터가 특정 데이터베이스의 주요 사용 사례를 커버하는지 확인하려면 각 데이터베이스를 별도로 사용하여 단위/통합 테스트를 추가해야 합니다.

출처:
- https://github.com/mongodb/mongo-efcore-provider?tab=readme-ov-file#supported-features

### 호환성

최신 Entity Framework Core 패키지를 사용하면서 .NET Standard용으로 개발하는 것은 불가능합니다. .NET Standard를 지원하는 EF Core의 마지막 버전은 5.0이었습니다(최신 EF Core 버전은 8.0). 이는 Entity Framework 커넥터가 net8.0만 대상으로 할 수 있음을 의미합니다(현재 net8.0과 netstandard2.0을 모두 대상으로 하는 다른 사용 가능한 SK 커넥터와 다릅니다).

다른 방법은 net8.0과 netstandard2.0을 모두 대상으로 할 수 있는 Entity Framework 6을 사용하는 것이지만, 이 버전의 Entity Framework는 더 이상 적극적으로 개발되지 않습니다. Entity Framework Core는 EF6에서 구현되지 않을 새로운 기능을 제공합니다.

출처: 
- https://learn.microsoft.com/en-us/ef/core/miscellaneous/platforms
- https://learn.microsoft.com/en-us/ef/efcore-and-ef6/

### 기존 SK 커넥터의 존재

Semantic Kernel이 이미 Entity Framework에서도 지원하는 일부 데이터베이스와의 통합을 가지고 있다는 점을 고려하면, 진행 방법에 대한 여러 옵션이 있습니다:
- Entity Framework와 DB 커넥터를 모두 지원 (예: `Microsoft.SemanticKernel.Connectors.EntityFramework`와 `Microsoft.SemanticKernel.Connectors.MongoDB`) - 이 경우 두 커넥터가 정확히 동일한 결과를 생성해야 하므로, 이 상태를 보장하기 위해 추가 작업(예: 동일한 단위/통합 테스트 세트 구현)이 필요합니다. 또한 로직에 대한 모든 수정은 두 커넥터 모두에 적용되어야 합니다.
- 하나의 Entity Framework 커넥터만 지원 (예: `Microsoft.SemanticKernel.Connectors.EntityFramework`) - 이 경우 기존 DB 커넥터를 제거해야 하며, 이는 기존 고객에 대한 호환성 깨짐 변경이 될 수 있습니다. Entity Framework가 이전 DB 커넥터와 정확히 동일한 기능 세트를 커버하는지 확인하기 위해 추가 작업이 필요합니다.
- 하나의 DB 커넥터만 지원 (예: `Microsoft.SemanticKernel.Connectors.MongoDB`) - 이 경우 해당 커넥터가 이미 존재하면 추가 작업이 필요하지 않습니다. 해당 커넥터가 존재하지 않고 추가가 중요하면 해당 DB 커넥터를 구현하기 위한 추가 작업이 필요합니다.


Entity Framework와 Semantic Kernel 데이터베이스 지원 표 (벡터 검색을 지원하는 데이터베이스만):

|데이터베이스 엔진|유지 관리자 / 벤더|EF 지원|SK 지원|SK 메모리 v2 설계로 업데이트됨
|-|-|-|-|-|
|Azure Cosmos|Microsoft|예|예|예|
|Azure SQL 및 SQL Server|Microsoft|예|예|아니오|
|SQLite|Microsoft|예|예|아니오|
|PostgreSQL|Npgsql Development Team|예|예|아니오|
|MongoDB|MongoDB|예|예|아니오|
|MySQL|Oracle|예|아니오|아니오|
|Oracle DB|Oracle|예|아니오|아니오|
|Google Cloud Spanner|Cloud Spanner Ecosystem|예|아니오|아니오|

**참고**:
하나의 데이터베이스 엔진에 서로 다른 벤더가 유지 관리하는 여러 Entity Framework 통합이 있을 수 있습니다(예: MySQL EF NuGet 패키지가 2개 있음 - 하나는 Oracle이 유지 관리하고 다른 하나는 Pomelo Foundation Project가 유지 관리).

Semantic Kernel에서 추가로 지원하는 벡터 DB 커넥터:
- Azure AI Search
- Chroma
- Milvus
- Pinecone
- Qdrant
- Redis
- Weaviate

출처:
- https://learn.microsoft.com/en-us/ef/core/providers/?tabs=dotnet-core-cli#current-providers

## 고려된 옵션

- 새 `Microsoft.SemanticKernel.Connectors.EntityFramework` 커넥터 추가.
- `Microsoft.SemanticKernel.Connectors.EntityFramework` 커넥터를 추가하지 않고, 필요할 때 개별 데이터베이스용 새 커넥터를 추가.

## 결정 결과

위의 조사를 바탕으로, Entity Framework 커넥터를 추가하지 않고 필요할 때 개별 데이터베이스용 새 커넥터를 추가하기로 결정했습니다. 이 결정의 이유는 Entity Framework 공급자가 컬렉션 관리 작업을 균일하게 지원하지 않으며, 키 처리와 객체 매핑에 데이터베이스별 코드가 필요하기 때문입니다. 이러한 요소들은 Entity Framework 커넥터의 사용을 신뢰할 수 없게 만들며 기본 데이터베이스를 추상화하지 못합니다. 또한 Entity Framework가 지원하지만 Semantic Kernel에 메모리 커넥터가 없는 벡터 데이터베이스의 수가 매우 적습니다.
