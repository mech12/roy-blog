---
# 이것들은 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: westey-m
date: 2024-03-10
deciders: westey-m, rbarreto, markwallace, sergeymenshykh, eavanvalkenburg, roji, dmytrostruk
consulted: rbarreto, markwallace, sergeymenshykh, eavanvalkenburg, roji, dmytrostruk
informed: rbarreto, markwallace, sergeymenshykh, eavanvalkenburg, roji, dmytrostruk
---

# VectorStore 추상화에서 하이브리드 검색 지원

## 맥락과 문제 설명

단순한 벡터 검색 외에도, 많은 데이터베이스가 하이브리드 검색도 지원합니다.
하이브리드 검색은 일반적으로 더 높은 품질의 검색 결과를 제공하므로, VectorStore 추상화를 통해 하이브리드 검색을 수행하는 능력은 추가해야 할 중요한 기능입니다.

하이브리드 검색이 지원되는 방식은 데이터베이스마다 다릅니다. 하이브리드 검색을 지원하는 가장 일반적인 두 가지 방법은:

1. 밀집 벡터 검색과 키워드/전문 검색을 병렬로 사용한 후 결과를 결합하는 것.
1. 밀집 벡터 검색과 희소 벡터 검색을 병렬로 사용한 후 결과를 결합하는 것.

희소 벡터는 밀집 벡터와 다르게 일반적으로 훨씬 더 많은 차원을 가지지만, 많은 차원이 0인 특성이 있습니다.
텍스트 검색에 사용될 때 희소 벡터는 어휘의 각 단어/토큰에 대한 차원을 가지며, 값은 소스 텍스트에서 단어의 중요도를 나타냅니다.
특정 텍스트 청크에서 단어가 더 흔하고, 말뭉치에서 단어가 덜 흔할수록, 희소 벡터에서의 값이 높아집니다.

희소 벡터를 생성하는 다양한 메커니즘이 있습니다:

- [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [SPLADE](https://www.pinecone.io/learn/splade/)
- [BGE-m3 sparse embedding model](https://huggingface.co/BAAI/bge-m3)
- [pinecone-sparse-english-v0](https://docs.pinecone.io/models/pinecone-sparse-english-v0)

Python에서는 이들이 잘 지원되지만, 현재 .net에서는 잘 지원되지 않습니다.
희소 벡터 생성 지원을 추가하는 것은 이 ADR의 범위 밖입니다.

추가 배경 정보:

- [하이브리드 검색을 위한 희소 벡터 사용에 대한 Qdrant의 배경 기사](https://qdrant.tech/articles/sparse-vectors)
- [초보자를 위한 TF-IDF 설명](https://medium.com/@coldstart_coder/understanding-and-implementing-tf-idf-in-python-a325d1301484)

ML.Net에는 .net에서 희소 벡터를 생성하는 데 사용할 수 있는 TF-IDF 구현이 포함되어 있습니다. [여기](https://github.com/dotnet/machinelearning/blob/886e2ff125c0060f5a251056c7eb2a7d28738984/docs/samples/Microsoft.ML.Samples/Dynamic/Transforms/Text/ProduceWordBags.cs#L55-L105)에서 예시를 참조하세요.

### 다양한 데이터베이스에서의 하이브리드 검색 지원

|Feature|Azure AI Search|Weaviate|Redis|Chroma|Pinecone|PostgreSql|Qdrant|Milvus|Elasticsearch|CosmosDB NoSql|MongoDB|
|-|-|-|-|-|-|-|-|-|-|-|-|
|Hybrid search supported|Y|Y|N (No parallel execution with fusion)|N|Y|Y|Y|Y|Y|Y|Y|
|Hybrid search definition|Vector + FullText|[Vector + Keyword (BM25F)](https://weaviate.io/developers/weaviate/search/hybrid)|||[Vector + Sparse Vector for keywords](https://docs.pinecone.io/guides/get-started/key-features#hybrid-search)|[Vector + Keyword](https://jkatz05.com/post/postgres/hybrid-search-postgres-pgvector/)|[Vector + SparseVector / Keyword](https://qdrant.tech/documentation/concepts/hybrid-queries/)|[Vector + SparseVector](https://milvus.io/docs/multi-vector-search.md)|Vector + FullText|[Vector + Fulltext (BM25)](https://learn.microsoft.com/en-us/azure/cosmos-db/gen-ai/hybrid-search)|[Vector + FullText](https://www.mongodb.com/docs/atlas/atlas-search/tutorial/hybrid-search)|
|Fusion method configurable|N|Y|||?|Y|Y|Y|Y, but only one option|Y, but only one option|N|
|Fusion methods|[RRF](https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking)|Ranked/RelativeScore|||?|[Build your own](https://jkatz05.com/post/postgres/hybrid-search-postgres-pgvector/)|RRF / DBSF|[RRF / Weighted](https://milvus.io/docs/multi-vector-search.md)|[RRF](https://www.elastic.co/search-labs/tutorials/search-tutorial/vector-search/hybrid-search)|[RRF](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/query/rrf)|[RRF](https://www.mongodb.com/docs/atlas/atlas-search/tutorial/hybrid-search)|
|Hybrid Search Input Params|Vector + string|[Vector + string](https://weaviate.io/developers/weaviate/api/graphql/search-operators#hybrid)|||Vector + SparseVector|Vector + String|[Vector + SparseVector](https://qdrant.tech/documentation/concepts/hybrid-queries/)|[Vector + SparseVector](https://milvus.io/docs/multi-vector-search.md)|Vector + string|Vector + string array|Vector + string|
|Sparse Distance Function|n/a|n/a|||[dotproduct only for both dense and sparse, 1 setting for both](https://docs.pinecone.io/guides/data/understanding-hybrid-search#sparse-dense-workflow)|n/a|dotproduct|Inner Product|n/a|n/a|n/a|
|Sparse Indexing options|n/a|n/a|||no separate config to dense|n/a|ondisk / inmemory  + IDF|[SPARSE_INVERTED_INDEX / SPARSE_WAND](https://milvus.io/docs/index.md?tab=sparse)|n/a|n/a|n/a|
|Sparse data model|n/a|n/a|||[indices & values arrays](https://docs.pinecone.io/guides/data/upsert-sparse-dense-vectors)|n/a|indices & values arrays|[sparse matrix / List of dict / list of tuples](https://milvus.io/docs/sparse_vector.md#Use-sparse-vectors-in-Milvus)|n/a|n/a|n/a|
|Keyword matching behavior|[Space Separated with SearchMode=any does OR, searchmode=all does AND](https://learn.microsoft.com/en-us/azure/search/search-lucene-query-architecture)|[Tokenization with split by space, affects ranking](https://weaviate.io/developers/weaviate/search/bm25)|||n/a|[Tokenization](https://www.postgresql.org/docs/current/textsearch-controls.html)|[<p>No FTS Index: Exact Substring match</p><p>FTS Index present: All words must be present</p>](https://qdrant.tech/documentation/concepts/filtering/#full-text-match)|n/a|[And/Or capabilities](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-bool-prefix-query.html)|-|[Allows multiple multi-word phrases with OR](https://www.mongodb.com/docs/atlas/atlas-search/phrase/) and [a single multi-word prhase where the words can be OR'd or AND'd](https://www.mongodb.com/docs/atlas/atlas-search/text/)|

용어:

- RRF = Reciprical Rank Fusion (역순위 융합)
- DBSF = Distribution-Based Score Fusion (분포 기반 점수 융합)
- IDF = Inverse Document Frequency (역문서 빈도)

### Cosmos DB NoSQL 전문 검색 설정에 필요한 언어

Cosmos DB NoSQL은 전문 검색에 언어를 지정해야 하며, 하이브리드 검색을 활성화하려면 전문 검색 인덱싱이 필요합니다.
따라서 인덱스를 생성할 때 언어를 지정하는 방법을 지원해야 합니다.

Cosmos DB NoSQL은 우리 샘플에서 이 유형의 필수 설정을 가진 유일한 데이터베이스입니다.

|Feature|Azure AI Search|Weaviate|Redis|Chroma|Pinecone|PostgreSql|Qdrant|Milvus|Elasticsearch|CosmosDB NoSql|MongoDB|
|-|-|-|-|-|-|-|-|-|-|-|-|
|Requires FullTextSearch indexing for hybrid search|Y|Y|n/a|n/a|n/a|Y|N [optional](https://qdrant.tech/documentation/concepts/filtering/#full-text-match)|n/a|Y|Y|[Y](https://www.mongodb.com/docs/atlas/atlas-search/tutorial/hybrid-search/?msockid=04b550d92f2f619c271a45a42e066050#create-the-atlas-vector-search-and-fts-indexes)|
|Required FullTextSearch index options|None required, [many optional](https://learn.microsoft.com/en-us/rest/api/searchservice/indexes/create?view=rest-searchservice-2024-07-01&tabs=HTTP)|None required, [none optional](https://weaviate.io/developers/weaviate/concepts/indexing#collections-without-indexes)||||[language required](https://jkatz05.com/post/postgres/hybrid-search-postgres-pgvector/)|none required, [some optional](https://qdrant.tech/documentation/concepts/indexing/#full-text-index)||None required, [many optional](https://elastic.github.io/elasticsearch-net/8.16.3/api/Elastic.Clients.Elasticsearch.Mapping.TextProperty.html)|Language Required|None required, [many optional](https://www.mongodb.com/docs/atlas/atlas-search/field-types/string-type/#configure-fts-field-type-field-properties)|

### 키워드 검색 인터페이스 옵션

각 DB는 서로 다른 키워드 검색 기능을 가지고 있습니다. 일부는 하이브리드 검색을 위해 키워드를 나열할 때 매우 기본적인 인터페이스만 지원합니다. 다음 표는 우리가 지원하려는 특정 키워드 공개 인터페이스와 각 DB의 호환성을 나열합니다.

|Feature|Azure AI Search|Weaviate|PostgreSql|Qdrant|Elasticsearch|CosmosDB NoSql|MongoDB|
|-|-|-|-|-|-|-|-|
|<p>string[] keyword</p><p>요소당 한 단어</p><p>일치하는 단어가 랭킹을 높임.</p>|Y|Y (have to join with spaces)|[Y (have to join with spaces)](https://www.postgresql.org/docs/current/textsearch-controls.html)|Y (via filter with multiple OR'd matches)|Y|Y|[Y (have to join with spaces)](https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.find_one)|
|<p>string[] keyword</p><p>요소당 하나 이상의 단어</p><p>단일 요소의 모든 단어가 존재해야 랭킹을 높임.</p>|Y|N|Y|Y (via filter with multiple OR'd matches and FTS Index)|-|N|N|
|<p>string[] keyword</p><p>요소당 하나 이상의 단어</p><p>단일 요소의 여러 단어는 정확히 일치하는 구문이어야 랭킹을 높임.</p>|Y|N|Y|Only via filter with multiple OR'd matches and NO Index|-|N|Y|
|<p>string keyword</p><p>공백으로 구분된 단어</p><p>일치하는 단어가 랭킹을 높임.</p>|Y|Y|Y|N (would need to split words)|-|N (would need to split words)|Y|

### 이름 지정 옵션

|Interface Name|Method Name|Parameters|Options Class Name|Keyword Property Selector|Dense Vector Property Selector|
|-|-|-|-|-|-|
|KeywordVectorizedHybridSearch|KeywordVectorizedHybridSearch|string[] + Dense Vector|KeywordVectorizedHybridSearchOptions|FullTextPropertyName|VectorPropertyName|
|SparseVectorizedHybridSearch|SparseVectorizedHybridSearch|Sparse Vector + Dense Vector|SparseVectorizedHybridSearchOptions|SparseVectorPropertyName|VectorPropertyName|
|KeywordVectorizableTextHybridSearch|KeywordVectorizableTextHybridSearch|string[] + string|KeywordVectorizableTextHybridSearchOptions|FullTextPropertyName|VectorPropertyName|
|SparseVectorizableTextHybridSearch|SparseVectorizableTextHybridSearch|string[] + string|SparseVectorizableTextHybridSearchOptions|SparseVectorPropertyName|VectorPropertyName|

|Interface Name|Method Name|Parameters|Options Class Name|Keyword Property Selector|Dense Vector Property Selector|
|-|-|-|-|-|-|
|KeywordVectorizedHybridSearch|HybridSearch|string[] + Dense Vector|KeywordVectorizedHybridSearchOptions|FullTextPropertyName|VectorPropertyName|
|SparseVectorizedHybridSearch|HybridSearch|Sparse Vector + Dense Vector|SparseVectorizedHybridSearchOptions|SparseVectorPropertyName|VectorPropertyName|
|KeywordVectorizableTextHybridSearch|HybridSearch|string[] + string|KeywordVectorizableTextHybridSearchOptions|FullTextPropertyName|VectorPropertyName|
|SparseVectorizableTextHybridSearch|HybridSearch|string[] + string|SparseVectorizableTextHybridSearchOptions|SparseVectorPropertyName|VectorPropertyName|

|Interface Name|Method Name|Parameters|Options Class Name|Keyword Property Selector|Dense Vector Property Selector|
|-|-|-|-|-|-|
|HybridSearchWithKeywords|HybridSearch|string[] + Dense Vector|HybridSearchOptions|FullTextPropertyName|VectorPropertyName|
|HybridSearchWithSparseVector|HybridSearchWithSparseVector|Sparse Vector + Dense Vector|HybridSearchWithSparseVectorOptions|SparseVectorPropertyName|VectorPropertyName|
|HybridSearchWithKeywordsAndVectorizableText|HybridSearch|string[] + string|HybridSearchOptions|FullTextPropertyName|VectorPropertyName|
|HybridSearchWithVectorizableKeywordsAndText|HybridSearchWithSparseVector|string[] + string|HybridSearchWithSparseVectorOptions|SparseVectorPropertyName|VectorPropertyName|

|Area|Type of search|Params|Method Name|
|-|-|-|-|
|**비벡터 검색**||||
|비벡터 검색|벡터 없는 일반 검색||Search|
|**이름 지정 메서드를 사용한 벡터 검색**||||
|벡터 검색|벡터 사용|`ReadonlyMemory<float> vector`|VectorSearch|
|벡터 검색|벡터화 가능한 텍스트 사용|`string text`|VectorSearchWithText|
|벡터 검색|벡터화 가능한 이미지 사용|`string/byte[]/other image`|VectorSearchWithImage|
|벡터 검색|벡터화 가능한 이미지+텍스트 사용|`string/byte[]/other image, string text`|VectorSearchWithImageAndText|
|**이름 지정 매개변수를 사용한 벡터 검색**||||
|벡터 검색|벡터 사용|`new Vector(ReadonlyMemory<float>)`|VectorSearch|
|벡터 검색|벡터화 가능한 텍스트 사용|`new VectorizableText(string text)`|VectorSearch|
|벡터 검색|벡터화 가능한 이미지 사용|`new VectorizableImage(string/byte[]/other image)`|VectorSearch|
|벡터 검색|벡터화 가능한 이미지+텍스트 사용|`VectorizableMultimodal(string/byte[]/other image, string text)`|VectorSearch|
|**하이브리드 검색**||||
|하이브리드 검색|밀집벡터 + string[] 키워드|`ReadonlyMemory<float> vector, string[] keywords`|HybridSearch|
|하이브리드 검색|벡터화 가능 문자열 + string[] 키워드|`string vectorizableText, string[] keywords`|HybridSearch|
|하이브리드 검색|밀집벡터 + 희소벡터|`ReadonlyMemory<float> vector, ? sparseVector`|HybridSearchWithSparseVector|
|하이브리드 검색|벡터화 가능 문자열 + 희소 벡터화 가능 string[] 키워드|`string vectorizableText, string[] vectorizableKeywords`|HybridSearchWithSparseVector|

```csharp
var collection;

// ----------------------- 메서드 이름이 달라짐 -----------------------
// 검색하려는 각 데이터 타입에 대해 새 메서드 이름을 가진 새 인터페이스를 추가해야 합니다.

public Task VectorSearch(ReadonlyMemory<float> vector, VectorSearchOptions options = null, CancellationToken cancellationToken);
public Task VectorSearchWithText(string text, VectorSearchOptions options = null, CancellationToken cancellationToken = null);
public Task VectorSearchWithImage(VectorizableData image, VectorSearchOptions options = null, CancellationToken cancellationToken = null);
collection.VectorSearchWithImageAndText(VectorizableData image, string text, VectorSearchOptions options = null, CancellationToken cancellationToken = null);

collection.VectorSearch(new ReadonlyMemory<float>([...]));
collection.VectorSearchWithText("Apples and oranges are tasty.");
collection.VectorSearchWithImage("fdslkjfskdlfjdslkjfdskljfdslkjfsd");
collection.VectorSearchWithImageAndText("fdslkjfskdlfjdslkjfdskljfdslkjfsd", "Apples and oranges are tasty.");

// ----------------------- 매개변수 타입이 달라짐 -----------------------
// 검색하려는 각 데이터 타입에 대해 새 인터페이스를 추가해야 합니다.

// 벡터 검색
public Task VectorSearch<TRecord>(Embedding embedding, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken);
public Task VectorSearch<TRecord>(VectorizableImage vectorizableImage, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);
public Task VectorSearch<TRecord>(VectorizableMultimodal vectorizableMultiModal, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);

collection.VectorSearch(new Embedding(new ReadonlyMemory<float>([...])));
collection.VectorSearch(new VectorizableText("Apples and oranges are tasty."));
collection.VectorSearch(new VectorizableImage("fdslkjfskdlfjdslkjfdskljfdslkjfsd"));
collection.VectorSearch(new VectorizableMultimodal("fdslkjfskdlfjdslkjfdskljfdslkjfsd", "Apples and oranges are tasty."));

// 하이브리드 검색
// 다음 옵션과 동일, 하이브리드는 현재 명시적으로 밀집 벡터와 키워드를 사용합니다.

// ----------------------- 공통 기본 타입을 상속하는 매개변수 배열 -----------------------
// 사용을 더 쉽게 하기 위해 확장 메서드를 추가할 수 있습니다.
// 검색하려는 새 데이터 타입에 대해 새 임베딩 또는 벡터화 가능한 데이터 타입만 추가하면 됩니다.

// 벡터 검색
public Task VectorSearch<TRecord>(Embedding embedding, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);
public Task VectorSearch<TRecord>(VectorizableData vectorizableData, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);
public Task VectorSearch<TRecord>(VectorizableData[] vectorizableData, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);
public Task VectorSearch<TRecord, TVectorType>(TVectorType embedding, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken);

// 편의 확장 메서드
public Task VectorSearch<TRecord>(Embedding embedding, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken);
public Task VectorSearch<TRecord>(string text, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);

public Task Search<TRecord>(NonVectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken);

collection.VectorSearch(new Embedding(new ReadonlyMemory<float>([...])));
collection.VectorSearch("Apples and oranges are tasty."); // 확장을 통해?
collection.VectorSearch(new VectorizableData("Apples and oranges are tasty.", "text/plain"));

collection.VectorSearch(["Apples and oranges are tasty."]); // 확장을 통해?
collection.VectorSearch([new VectorizableData("Apples and oranges are tasty.", "text/plain")]);
collection.VectorSearch([new VectorizableData("fdslkjfskdlfjdslkjfdskljfdslkjfsd", "image/jpeg")]);
collection.VectorSearch([new VectorizableData("fdslkjfskdlfjdslkjfdskljfdslkjfsd", "image/jpeg"), new VectorizableText("Apples and oranges are tasty.")]);

// 하이브리드 검색
public Task HybridSearch<TRecord, TVectorType>(TVector vector, VectorizableData vectorizableData, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);

public Task HybridSearch<TRecord>(Embedding denseVector, Embedding sparseVector, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);
public Task HybridSearch<TRecord>(Embedding Densevector, VectorizableData sparseVectorizableData, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);
public Task HybridSearch<TRecord>(VectorizableData denseVectorizableData, VectorizableData sparseVectorizableData, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);
public Task HybridSearch<TRecord>(VectorizableData denseVectorizableData, Embedding sparseVector, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);

collection.HybridSearch(new Embedding(new ReadonlyMemory<float>([...])), ["Apples", "Oranges"], new() { VectorPropertyName = "DescriptionEmbedding", FullTextPropertyName = "Keywords" })
collection.HybridSearch(new VectorizableText("Apples and oranges are tasty."), ["Apples", "Oranges"], new() { VectorPropertyName = "DescriptionEmbedding", FullTextPropertyName = "Keywords" });
collection.HybridSearchWithSparseVector(new Embedding(new ReadonlyMemory<float>([...])), new SparseEmbedding(), new() { VectorPropertyName = "DescriptionEmbedding", SparseVectorPropertyName = "KeywordsEmbedding" });
collection.HybridSearchWithSparseVector(new VectorizableText("Apples and oranges are tasty."), new SparseEmbedding(), new() { VectorPropertyName = "DescriptionEmbedding", SparseVectorPropertyName = "KeywordsEmbedding" });
collection.HybridSearchWithSparseVector(new VectorizableText("Apples and oranges are tasty."), new SparseVectorizableText("Apples", "Oranges"), new() { VectorPropertyName = "DescriptionEmbedding", SparseVectorPropertyName = "KeywordsEmbedding" });

// ----------------------- 하나의 이름, 일반 매개변수, 공통 옵션, 대상 속성 타입이 검색 타입을 결정 -----------------------

// 제네릭 벡터 사용 (단기)
public Task HybridSearch<TRecord, TVectorType>(TVector vector, string[] keywords, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken);

// 임베딩 사용 (장기)
public Task HybridSearch<TRecord>(Embedding vector, string[] keywords, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken);
public Task HybridSearch<TRecord>(Embedding vector, SparseEmbedding sparseVector, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken);
public Task HybridSearch<TRecord>(string vectorizableText, SparseEmbedding sparseVector, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken);
public Task HybridSearch<TRecord>(string vectorizableText, string[] sparseVectorizableText, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken);
public Task HybridSearch<TRecord>(Embedding vector, string[] sparseVectorizableText, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken);

// fulltextsearchproperty/sparsevectorproperty에 대한 좋은 이름이 있을까요.
HybridSearchPropertyName
AdditionalSearchPropertyName
AdditionalPropertyName
SecondaryPropertyName
HybridSearchSecondaryPropertyName
KeywordsPropertyName
KeywordsSearchPropertyName

// ----------------------- 공통 기본 클래스를 통한 Embedding/VectorizableContent 전달과 대상 속성 이름 -----------------------

class SearchTarget<TRecord>();
class VectorSearchTarget<TRecord, TVectorType>(ReadonlyMemory<TVectorType> vector, Expression<Func<TRecord, object>> targetProperty) : SearchTarget<TRecord>();
class KeywordsSearchTarget<TRecord>(string[] keywords, Expression<Func<TRecord, object>> targetProperty) : SearchTarget<TRecord>();
class SparseSearchTarget<TRecord>(SparseVector vector, Expression<Func<TRecord, object>> targetProperty) : SearchTarget<TRecord>();

public Task HybridSearch(
    SearchTarget<TRecord>[] searchParams,
    HybridSearchOptions options = null,
    CancellationToken cancellationToken);
// 확장 메서드:
public Task HybridSearch(
    ReadonlyMemory<float> vector vector,
    string targetVectorPropertyName,
    string[] keywords,
    string targetHybridSearchPropertyName,
    HybridSearchOptions options = null,
    CancellationToken cancellationToken);
public Task HybridSearch(
    ReadonlyMemory<float> vector vector,
    string targetVectorFieldName,
    SparseVector sparseVector,
    string targetHybridSearchPropertyName,
    HybridSearchOptions options = null,
    CancellationToken cancellationToken);
```

### 키워드 기반 하이브리드 검색

```csharp
interface IKeywordVectorizedHybridSearch<TRecord>
{
    Task<VectorSearchResults<TRecord>> KeywordVectorizedHybridSearch<TVector>(
        TVector vector,
        ICollection<string> keywords,
        KeywordVectorizedHybridSearchOptions options,
        CancellationToken cancellationToken);
}

class KeywordVectorizedHybridSearchOptions
{
    // 벡터 검색 대상 속성의 이름.
    public string? VectorPropertyName { get; init; }

    // 텍스트 검색 대상 속성의 이름.
    public string? FullTextPropertyName { get; init; }

    public VectorSearchFilter? Filter { get; init; }
    public int Top { get; init; } = 3;
    public int Skip { get; init; } = 0;
    public bool IncludeVectors { get; init; } = false;
    public bool IncludeTotalCount { get; init; } = false;
}
```

### 희소 벡터 기반 하이브리드 검색

```csharp
interface ISparseVectorizedHybridSearch<TRecord>
{
    Task<VectorSearchResults<TRecord>> SparseVectorizedHybridSearch<TVector, TSparseVector>(
        TVector vector,
        TSparseVector sparsevector,
        SparseVectorizedHybridSearchOptions options,
        CancellationToken cancellationToken);
}

class SparseVectorizedHybridSearchOptions
{
    // 밀집 벡터 검색 대상 속성의 이름.
    public string? VectorPropertyName { get; init; }
    // 희소 벡터 검색 대상 속성의 이름.
    public string? SparseVectorPropertyName { get; init; }

    public VectorSearchFilter? Filter { get; init; }
    public int Top { get; init; } = 3;
    public int Skip { get; init; } = 0;
    public bool IncludeVectors { get; init; } = false;
    public bool IncludeTotalCount { get; init; } = false;
}
```

### 키워드 벡터화 가능 텍스트 기반 하이브리드 검색

```csharp
interface IKeywordVectorizableHybridSearch<TRecord>
{
    Task<VectorSearchResults<TRecord>> KeywordVectorizableHybridSearch(
        string searchText,
        ICollection<string> keywords,
        KeywordVectorizableHybridSearchOptions options = default,
        CancellationToken cancellationToken = default);
}

class KeywordVectorizableHybridSearchOptions
{
    // 밀집 벡터 검색 대상 속성의 이름.
    public string? VectorPropertyName { get; init; }
    // 텍스트 검색 대상 속성의 이름.
    public string? FullTextPropertyName { get; init; }

    public VectorSearchFilter? Filter { get; init; }
    public int Top { get; init; } = 3;
    public int Skip { get; init; } = 0;
    public bool IncludeVectors { get; init; } = false;
    public bool IncludeTotalCount { get; init; } = false;
}
```

### 희소 벡터 기반 벡터화 가능 텍스트 하이브리드 검색

```csharp
interface ISparseVectorizableTextHybridSearch<TRecord>
{
    Task<VectorSearchResults<TRecord>> SparseVectorizableTextHybridSearch(
        string searchText,
        ICollection<string> keywords,
        SparseVectorizableTextHybridSearchOptions options = default,
        CancellationToken cancellationToken = default);
}

class SparseVectorizableTextHybridSearchOptions
{
    // 밀집 벡터 검색 대상 속성의 이름.
    public string? VectorPropertyName { get; init; }
    // 희소 벡터 검색 대상 속성의 이름.
    public string? SparseVectorPropertyName { get; init; }

    public VectorSearchFilter? Filter { get; init; }
    public int Top { get; init; } = 3;
    public int Skip { get; init; } = 0;
    public bool IncludeVectors { get; init; } = false;
    public bool IncludeTotalCount { get; init; } = false;
}
```

## 결정 동인

- 희소 벡터 기반 하이브리드 검색을 실행 가능하게 만들려면 희소 벡터 생성 지원이 필요합니다.
- 레코드당 여러 벡터 시나리오를 지원해야 합니다.
- 평가 세트의 어떤 데이터베이스도 업서트 시 텍스트를 데이터베이스에서 희소 벡터로 변환하고 이를 검색 가능한 필드에 저장하는 것을 지원하는 것으로 확인되지 않았습니다. 물론 이러한 DB 중 일부는 키워드 검색을 구현하기 위해 내부적으로 희소 벡터를 사용할 수 있지만, 호출자에게 노출하지 않습니다.

## 범위 지정 검토 옵션

### 1. 키워드 하이브리드 검색만

희소 벡터 생성 지원을 추가할 때까지 현재로서는 KeywordVectorizedHybridSearch 및 KeywordVectorizableTextHybridSearch만 구현합니다.

### 2. 키워드 및 SparseVectorized 하이브리드 검색

KeywordVectorizedHybridSearch 및 KeywordVectorizableTextHybridSearch를 구현하되,
평가 세트의 어떤 데이터베이스도 데이터베이스에서 희소 벡터 생성을 지원하지 않으므로 KeywordVectorizableTextHybridSearch만 구현합니다.
이를 위해 텍스트에서 희소 벡터를 생성할 수 있는 코드를 만들어야 합니다.

### 3. 위에 언급된 모든 하이브리드 검색

네 가지 인터페이스를 모두 생성하고 클라이언트 코드에서 희소 벡터를 생성하는 SparseVectorizableTextHybridSearch 구현을 만듭니다.
이를 위해 텍스트에서 희소 벡터를 생성할 수 있는 코드를 만들어야 합니다.

### 4. 일반화된 하이브리드 검색

일부 데이터베이스는 더 일반화된 버전의 하이브리드 검색을 지원하며, 모든 유형의 두 가지(또는 그 이상의) 검색을 가져와 선택한 융합 방법을 사용하여 결과를 결합할 수 있습니다.
이 더 일반화된 검색을 사용하여 벡터 + 키워드 검색을 구현할 수 있습니다.
그러나 벡터 + 키워드 하이브리드 검색만 지원하는 데이터베이스의 경우, 해당 데이터베이스 위에 일반화된 하이브리드 검색을 구현하는 것은 불가능합니다.

## PropertyName 이름 지정 검토 옵션

### 1. 명시적 Dense 이름 지정

DenseVectorPropertyName
SparseVectorPropertyName

DenseVectorPropertyName
FullTextPropertyName

- 장점: 희소 벡터도 관련되어 있다는 점을 고려할 때 더 명시적입니다.
- 단점: 비하이브리드 벡터 검색의 이름 지정과 불일치합니다.

### 2. 암시적 Dense 이름 지정

VectorPropertyName
SparseVectorPropertyName

VectorPropertyName
FullTextPropertyName

- 장점: 비하이브리드 벡터 검색의 이름 지정과 일치합니다.
- 단점: 내부적으로 불일치합니다. 즉, sparse vector가 있지만 dense의 경우 그냥 vector입니다.

## 키워드 분리 검토 옵션

### 1. 인터페이스에서 분리된 키워드 허용

각 값이 별도의 키워드인 문자열의 ICollection을 허용합니다.
단일 키워드를 받아 `ICollection<string>` 버전을 호출하는 버전도 확장 메서드로 제공할 수 있습니다.

```csharp
    Task<VectorSearchResults<TRecord>> KeywordVectorizedHybridSearch(
        TVector vector,
        ICollection<string> keywords,
        KeywordVectorizedHybridSearchOptions options,
        CancellationToken cancellationToken);
```

- 장점: 기저 DB가 분리된 키워드를 필요로 하는 경우 커넥터에서 사용하기 더 쉽습니다
- 장점: 위의 비교 표에서 볼 수 있듯이 광범위하게 지원되는 유일한 솔루션입니다.

### 2. 인터페이스에서 단일 문자열 허용

모든 키워드를 포함하는 단일 문자열을 허용합니다.

```csharp
    Task<VectorSearchResults<TRecord>> KeywordVectorizedHybridSearch(
        TVector vector,
        string keywords,
        KeywordVectorizedHybridSearchOptions options,
        CancellationToken cancellationToken);
```

- 장점: 사용자가 키워드 분리를 할 필요가 없어 사용하기 더 쉽습니다.
- 단점: 언어에 적합하게 단어를 분리하고 필러 단어를 제거하는 등 문자열을 적절히 정리하는 기능이 없습니다.

### 3. 인터페이스에서 둘 다 허용

두 옵션 중 하나를 허용하고 기저 DB에 필요한 대로 커넥터에서 키워드를 결합하거나 분리합니다.

```csharp
    Task<VectorSearchResults<TRecord>> KeywordVectorizedHybridSearch(
        TVector vector,
        ICollection<string> keywords,
        KeywordVectorizedHybridSearchOptions options,
        CancellationToken cancellationToken);
    Task<VectorSearchResults<TRecord>> KeywordVectorizedHybridSearch(
        TVector vector,
        string keywords,
        KeywordVectorizedHybridSearchOptions options,
        CancellationToken cancellationToken);
```

- 장점: 사용자가 자신에게 더 맞는 것을 선택할 수 있어 사용하기 더 쉽습니다
- 단점: 키워드를 결합하거나 분리하여 내부 표현으로 변환해야 합니다.
- 단점: 단일 문자열을 적절히 정리하는 기능이 없습니다.

### 4. 인터페이스에서 둘 다 허용하되 미지원 시 예외 발생

두 옵션 중 하나를 허용하되 기저 DB에서 지원되지 않는 것은 예외를 발생시킵니다.

- 장점: 우리가 구현하기 더 쉽습니다.
- 단점: 사용자가 사용하기 더 어렵습니다.

### 5. 각각에 대한 별도 인터페이스

열거형과 단일 문자열 옵션에 대해 별도의 인터페이스를 만들고, 각 DB에 대해 기저 시스템에서 지원하는 것만 구현합니다.

- 장점: 우리가 구현하기 더 쉽습니다.
- 단점: 사용자가 사용하기 더 어렵습니다.

## 전문 검색 인덱스 필수 설정 검토 옵션

Cosmos DB NoSQL은 전문 검색 인덱스를 생성할 때 언어를 지정해야 합니다.
다른 DB에는 설정할 수 있는 선택적 값이 있습니다.

### 1. 컬렉션 옵션을 통해 옵션 전달

이 옵션은 컬렉션의 옵션 클래스에 언어 옵션을 추가하는 최소한의 작업을 수행합니다.
이 언어는 컬렉션에 의해 생성되는 모든 전문 검색 인덱스에 사용됩니다.

- 장점: 구현하기 가장 간단합니다
- 단점: 하나의 레코드에서 다른 필드에 여러 언어를 사용할 수 없습니다
- 단점: 모든 DB의 모든 전문 검색 옵션에 대한 지원을 추가하지 않습니다

### 2. RecordDefinition 및 데이터 모델 Attributes에 대한 확장 추가

VectorStoreRecordProperty에 데이터베이스별 메타데이터를 제공할 수 있는 속성 백을 추가합니다.
데이터 모델에 추가 메타데이터를 추가할 수 있는 상속 가능한 추상 기본 속성을 추가하며,
각 데이터베이스가 자체 설정을 지정하기 위한 고유한 속성을 가지고, VectorStoreRecordProperty에 필요한 속성 백으로 내용을 변환하는 메서드를 포함합니다.

- 장점: 하나의 레코드에서 다른 필드에 여러 언어를 사용할 수 있습니다
- 장점: 다른 DB가 자체 속성을 통해 자체 설정을 추가할 수 있습니다
- 단점: 구현에 더 많은 작업이 필요합니다

## 결정 결과

### 범위 지정

선택한 옵션 "1. 키워드 하이브리드 검색만", 희소 벡터 생성을 위한 엔터프라이즈 지원이 부족하고 엔드투엔드 스토리 없이는 가치가 낮기 때문입니다.

### PropertyName 이름 지정

선택한 옵션 "2. 암시적 Dense 이름 지정", 기존 벡터 검색 옵션 이름 지정과 일치하기 때문입니다.

### 키워드 분리

선택한 옵션 "1. 인터페이스에서 분리된 키워드 허용", 데이터베이스들 사이에서 광범위하게 지원되는 유일한 옵션이기 때문입니다.

### 이름 지정 옵션 결정

우리의 노스스타 설계는 일반 검색과 하이브리드 검색 모두에 대한 입력으로 Embedding 타입과 벡터화 가능한 데이터(아마도 MEAI의 DataContent) 형태를 지원하는 것이 될 것이라고 합의했습니다.

```csharp
public Task VectorSearch<TRecord>(Embedding embedding, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);
public Task VectorSearch<TRecord>(VectorizableData vectorizableData, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);
public Task VectorSearch<TRecord>(VectorizableData[] vectorizableData, VectorSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);

public Task HybridSearch<TRecord, TVectorType>(TVector vector, VectorizableData vectorizableData, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken = null);
```

다양한 입력에 대해 향후 다른 오버로드를 가진 단일 HybridSearch 메서드 이름을 사용하지만, 단일 옵션 클래스가 있을 것입니다.
대상 키워드 필드 또는 향후 희소 벡터 필드를 선택하기 위한 속성 셀렉터는 `AdditionalPropertyName`으로 불릴 것입니다.

올바른 데이터 타입과 Embedding 타입을 사용할 수 있게 되기까지 작업하는 동안, 다음 인터페이스를 출시할 것입니다.

```csharp
public Task HybridSearch<TVector>(TVector vector, ICollection<string> keywords, HybridSearchOptions<TRecord> options = null, CancellationToken cancellationToken);
```
