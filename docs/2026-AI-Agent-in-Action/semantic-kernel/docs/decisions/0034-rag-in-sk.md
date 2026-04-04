---
# 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: proposed
contact: dmytrostruk
date: 2023-01-29
deciders: sergeymenshykh, markwallace, rbarreto, dmytrostruk
---

# Semantic Kernel에서의 검색 증강 생성 (RAG)

## 배경 및 문제 설명

### 일반 정보

Semantic Kernel(SK)에서 RAG 패턴을 사용하는 방법에는 여러 가지가 있습니다. 일부 접근 방식은 이미 SK에 존재하며, 일부는 다양한 개발 경험을 위해 향후 추가될 수 있습니다.

이 ADR의 목적은 SK의 메모리 관련 기능에서 문제가 되는 부분을 설명하고, 현재 버전의 SK에서 RAG를 달성하는 방법을 시연하며, RAG를 위한 공개 API의 새로운 설계를 제안하는 것입니다.

이 ADR에 제시된 검토 옵션들은 서로 모순되지 않으며 동시에 모두 지원될 수 있습니다. 어떤 옵션을 지원할지에 대한 결정은 우선순위, 특정 기능에 대한 실제 요구 사항, 일반적인 피드백 등 다양한 요소를 기반으로 합니다.

### 벡터 DB 통합 - 커넥터

현재 12개의 [벡터 DB 커넥터](https://github.com/microsoft/semantic-kernel/tree/main/dotnet/src/Connectors)(`메모리 커넥터`라고도 함)가 구현되어 있으며, 개발자에게 사용 방법이 불분명할 수 있습니다. 커넥터 메서드를 직접 호출하거나 [Plugins.Memory](https://www.nuget.org/packages/Microsoft.SemanticKernel.Plugins.Memory) NuGet 패키지의 `TextMemoryPlugin`을 통해 사용할 수 있습니다 (프롬프트 예시: `{{recall 'company budget by year'}} What is my budget for 2024?`)

각 커넥터는 고유한 구현을 가지며, 일부는 특정 벡터 DB 제공자의 기존 .NET SDK에 의존하고, 일부는 벡터 DB 제공자의 REST API를 사용하는 기능을 구현했습니다.

이상적으로 각 커넥터는 항상 최신 상태를 유지하고 새로운 기능을 지원해야 합니다. 일부 커넥터는 새 기능에 브레이킹 변경이 포함되지 않거나 벡터 DB가 비교적 쉽게 재사용할 수 있는 .NET SDK를 제공하므로 유지 보수 비용이 낮습니다. 다른 커넥터는 아직 `alpha` 또는 `beta` 개발 단계에 있거나, 브레이킹 변경이 포함될 수 있거나, .NET SDK가 제공되지 않아 업데이트가 어려우므로 유지 보수 비용이 높습니다.

### IMemoryStore 인터페이스

각 메모리 커넥터는 `CreateCollectionAsync`, `GetNearestMatchesAsync` 등의 메서드가 있는 `IMemoryStore` 인터페이스를 구현하므로, `TextMemoryPlugin`의 일부로 사용할 수 있습니다.

동일한 인터페이스를 구현함으로써 각 통합이 정렬되어 런타임에 다른 벡터 DB를 사용할 수 있게 됩니다. 동시에 이는 단점이기도 한데, 각 벡터 DB가 다르게 작동할 수 있으며 모든 통합을 기존 추상화에 맞추기가 어려워지기 때문입니다. 예를 들어, `IMemoryStore`의 `CreateCollectionAsync` 메서드는 애플리케이션이 존재하지 않는 컬렉션의 벡터 DB에 새 레코드를 추가하려 할 때 사용되므로, 삽입 작업 전에 새 컬렉션을 생성합니다. [Pinecone](https://www.pinecone.io/) 벡터 DB의 경우, Pinecone 인덱스 생성이 비동기 프로세스이므로 이 시나리오가 지원되지 않습니다 - API 서비스가 응답 본문에 다음 속성과 함께 201 Created HTTP 응답을 반환합니다(인덱스가 사용 준비되지 않음):

```json
{
    // 기타 속성...
    "status": {
        "ready": false,
        "state": "Initializing"
    }
}
```

이 경우 데이터베이스에 즉시 레코드를 삽입할 수 없으므로, 이 시나리오를 커버하기 위해 HTTP 폴링이나 유사한 메커니즘을 구현해야 합니다.

### 저장소 스키마로서의 MemoryRecord

`IMemoryStore` 인터페이스는 벡터 DB의 저장소 스키마로 `MemoryRecord` 클래스를 사용합니다. 이는 `MemoryRecord` 속성이 모든 가능한 커넥터에 맞춰져야 함을 의미합니다. 개발자가 데이터베이스에서 이 스키마를 사용하기 시작하면, 스키마의 변경이 애플리케이션을 깨뜨릴 수 있으므로 유연한 접근 방식이 아닙니다.

`MemoryRecord`는 임베딩을 위한 `ReadOnlyMemory<float> Embedding` 속성과 임베딩 메타데이터를 위한 `MemoryRecordMetadata Metadata` 속성을 포함합니다. `MemoryRecordMetadata`는 다음과 같은 속성을 포함합니다:

- `string Id` - 고유 식별자.
- `string Text` - 데이터 관련 텍스트.
- `string Description` - 콘텐츠를 설명하는 선택적 제목.
- `string AdditionalMetadata` - 레코드와 함께 사용자 정의 메타데이터를 저장하기 위한 필드.

`MemoryRecord`와 `MemoryRecordMetadata`는 sealed 클래스가 아니므로, 필요에 따라 확장하고 더 많은 속성을 추가할 수 있어야 합니다. 그러나 현재 접근 방식은 여전히 개발자에게 벡터 DB에 특정 기본 스키마를 강제하며, 이는 이상적으로 피해야 합니다. 개발자는 비즈니스 시나리오를 커버하는 자신이 선택한 어떤 스키마로든 작업할 수 있어야 합니다(Entity Framework의 Code First 접근 방식과 유사하게).

### TextMemoryPlugin

TextMemoryPlugin에는 4개의 커널 함수가 포함되어 있습니다:

- `Retrieve` - 키로 DB에서 구체적인 레코드를 반환합니다.
- `Recall` - 벡터 검색을 수행하고 관련성에 기반하여 여러 레코드를 반환합니다.
- `Save` - 벡터 DB에 레코드를 저장합니다.
- `Remove` - 벡터 DB에서 레코드를 제거합니다.

모든 함수는 프롬프트에서 직접 호출할 수 있습니다. 또한, 이러한 함수가 커널에 등록되고 함수 호출이 활성화되면, LLM이 제공된 목표를 달성하기 위해 특정 함수를 호출하기로 결정할 수 있습니다.

`Retrieve`와 `Recall` 함수는 LLM에 일부 컨텍스트를 제공하고 데이터를 기반으로 질문하는 데 유용하지만, `Save`와 `Remove` 함수는 벡터 DB의 데이터를 조작하므로 예측할 수 없거나 때로는 위험할 수 있습니다(LLM이 삭제해서는 안 되는 레코드를 제거하기로 결정하는 상황이 있어서는 안 됩니다).

## 결정 동인

1. Semantic Kernel에서의 모든 데이터 조작은 안전해야 합니다.
2. Semantic Kernel에서 RAG 패턴을 사용하는 명확한 방법(들)이 있어야 합니다.
3. 추상화가 제공된 인터페이스나 데이터 유형으로 달성할 수 없는 기능을 가진 자신이 선택한 벡터 DB를 사용하는 것을 개발자에게 차단해서는 안 됩니다.

## 범위 외

일부 RAG 관련 프레임워크에는 RAG 패턴의 전체 주기를 지원하는 기능이 포함되어 있습니다:

1. 특정 리소스에서 데이터 **읽기** (예: Wikipedia, OneDrive, 로컬 PDF 파일).
2. 특정 로직을 사용하여 데이터를 여러 청크로 **분할**.
3. 데이터에서 임베딩 **생성**.
4. 선호하는 벡터 DB에 데이터 **저장**.
5. 사용자 쿼리를 기반으로 선호하는 벡터 DB에서 데이터 **검색**.
6. 제공된 데이터를 기반으로 LLM에 질문 **요청**.

현재 Semantic Kernel에는 다음과 같은 실험적 기능이 있습니다:

- 데이터를 청크로 **분할**하기 위한 `TextChunker` 클래스.
- OpenAI 및 HuggingFace 모델을 사용하여 임베딩을 **생성**하기 위한 `ITextEmbeddingGenerationService` 추상화 및 구현.
- 데이터를 **저장**하고 **검색**하기 위한 메모리 커넥터.

이러한 기능은 실험적이므로, RAG 패턴에 대한 결정이 SK에서 나열된 추상화, 클래스, 커넥터를 제공하고 유지할 필요가 없는 경우 향후 폐기될 수 있습니다.

데이터 **읽기**를 위한 도구는 현재 범위 외입니다.

## 검토된 옵션

### 옵션 1 [지원됨] - 프롬프트 연결

이 옵션은 데이터를 포함하여 프롬프트를 수동으로 구성할 수 있게 하여, LLM이 제공된 컨텍스트를 기반으로 쿼리에 응답할 수 있게 합니다. 수동 문자열 연결이나 프롬프트 템플릿 및 커널 인수를 사용하여 달성할 수 있습니다. 개발자는 자신이 선택한 벡터 DB와의 통합, 데이터 검색, LLM에 보내기 위한 프롬프트 구성을 책임집니다.

이 접근 방식은 기본적으로 Semantic Kernel에 메모리 커넥터를 포함하지 않지만, 동시에 개발자에게 자신에게 가장 잘 작동하는 방식으로 데이터를 처리할 기회를 제공합니다.

문자열 연결:

```csharp
var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("model-id", "api-key")
    .Build();

var builder = new StringBuilder();

// 사용자가 자신이 선택한 방식으로 데이터를 검색할 책임이 있습니다. 이것은 어떻게 될 수 있는지의 예시입니다.
var data = await this._vectorDB.SearchAsync("Company budget by year");

builder.AppendLine(data);
builder.AppendLine("What is my budget for 2024?");

var result = await kernel.InvokePromptAsync(builder.ToString());
```

프롬프트 템플릿 및 커널 인수:

```csharp
var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("model-id", "api-key")
    .Build();

// 사용자가 자신이 선택한 방식으로 데이터를 검색할 책임이 있습니다. 이것은 어떻게 될 수 있는지의 예시입니다.
var data = await this._vectorDB.SearchAsync("Company budget by year");

var arguments = new KernelArguments { ["budgetByYear"] = data };

var result = await kernel.InvokePromptAsync("{{budgetByYear}} What is my budget for 2024?", arguments);
```

### 옵션 2 [지원됨] - 플러그인으로서의 메모리

이 접근 방식은 옵션 1과 유사하지만, 데이터 검색 단계가 프롬프트 렌더링 프로세스의 일부입니다. 다음 목록은 데이터 검색에 사용할 수 있는 플러그인을 포함합니다:

- [ChatGPT Retrieval Plugin](https://github.com/openai/chatgpt-retrieval-plugin) - 이 플러그인은 별도의 서비스로 호스팅되어야 합니다. 다양한 [벡터 데이터베이스](https://github.com/openai/chatgpt-retrieval-plugin?tab=readme-ov-file#choosing-a-vector-database)와의 통합이 있습니다.
- [SemanticKernel.Plugins.Memory.TextMemoryPlugin](https://www.nuget.org/packages/Microsoft.SemanticKernel.Plugins.Memory) - 다양한 벡터 데이터베이스를 지원하는 Semantic Kernel 솔루션.
- 사용자 정의 플러그인.

ChatGPT Retrieval Plugin:

```csharp
var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("model-id", "api-key")
    .Build();

// OpenAPI 명세를 사용하여 ChatGPT Retrieval Plugin 가져오기
// https://github.com/openai/chatgpt-retrieval-plugin/blob/main/.well-known/openapi.yaml
await kernel.ImportPluginFromOpenApiAsync("ChatGPTRetrievalPlugin", openApi!, executionParameters: new(authCallback: async (request, cancellationToken) =>
{
    request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", "chat-gpt-retrieval-plugin-token");
}));

const string Query = "What is my budget for 2024?";
const string Prompt = "{{ChatGPTRetrievalPlugin.query_query_post queries=$queries}} {{$query}}";

var arguments = new KernelArguments
{
    ["query"] = Query,
    ["queries"] = JsonSerializer.Serialize(new List<object> { new { query = Query, top_k = 1 } }),
};

var result = await kernel.InvokePromptAsync(Prompt, arguments);
```

TextMemoryPlugin:

```csharp
var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("model-id", "api-key")
    .Build();

// 참고: 메모리 관련 공개 API를 계속 지원하기로 결정되면 재검토해야 합니다.
// 새로운 Semantic Kernel 패턴에 맞게 업데이트되어야 합니다.
// 예시: `WithChromaMemoryStore` 대신 `AddChromaMemoryStore`가 되어야 합니다.
var memory = new MemoryBuilder()
    .WithChromaMemoryStore("https://chroma-endpoint")
    .WithOpenAITextEmbeddingGeneration("text-embedding-ada-002", "api-key")
    .Build();

kernel.ImportPluginFromObject(new TextMemoryPlugin(memory));

var result = await kernel.InvokePromptAsync("{{recall 'Company budget by year'}} What is my budget for 2024?");
```

사용자 정의 플러그인:

```csharp
public class MyDataPlugin
{
    [KernelFunction("search")]
    public async Task<string> SearchAsync(string query)
    {
        // 벡터 DB를 호출하고 결과를 반환합니다.
        // 여기서 개발자는 특정 벡터 DB 제공자의 기존 .NET SDK를 사용할 수 있습니다.
        // Semantic Kernel 메모리 커넥터를 여기서 직접 재사용하는 것도 가능합니다:
        // new ChromaMemoryStore(...).GetNearestMatchAsync(...)
    }
}

var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("model-id", "api-key")
    .Build();

kernel.ImportPluginFromType<MyDataPlugin>();

var result = await kernel.InvokePromptAsync("{{search 'Company budget by year'}} What is my budget for 2024?");
```

사용자 정의 플러그인이 `TextMemoryPlugin`보다 더 유연한 이유는, `TextMemoryPlugin`은 모든 벡터 DB가 위에서 설명한 단점이 있는 `IMemoryStore` 인터페이스를 구현하도록 요구하는 반면, 사용자 정의 플러그인은 개발자가 선택한 방식으로 구현할 수 있기 때문입니다. DB 레코드 스키마에 대한 제한이나 특정 인터페이스를 구현해야 하는 요구 사항이 없습니다.

### 옵션 3 [부분 지원] - 프롬프트 필터를 사용한 프롬프트 연결

이 옵션은 옵션 1과 유사하지만, 프롬프트 연결이 프롬프트 필터 수준에서 발생합니다:

프롬프트 필터:

```csharp
public sealed class MyPromptFilter : IPromptFilter
{
    public void OnPromptRendering(PromptRenderingContext context)
    {
        // 프롬프트 렌더링 이벤트 처리...
    }

    public void OnPromptRendered(PromptRenderedContext context)
    {
        var data = "some data";
        var builder = new StringBuilder();

        builder.AppendLine(data);
        builder.AppendLine(context.RenderedPrompt);

        // AI에 보내기 전 렌더링된 프롬프트를 재정의하고 데이터 포함
        context.RenderedPrompt = builder.ToString();
    }
}
```

사용법:

```csharp
var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("model-id", "api-key")
    .Build();

kernel.PromptFilters.Add(new MyPromptFilter());

var result = await kernel.InvokePromptAsync("What is my budget for 2024?");
```

사용 관점에서 프롬프트에는 추가 데이터 없이 사용자 쿼리만 포함됩니다. 데이터는 뒤에서 프롬프트에 추가됩니다.

이 접근 방식이 **부분 지원**인 이유는 벡터 DB에 대한 호출이 대부분 비동기일 것이지만, 현재 커널 필터가 비동기 시나리오를 지원하지 않기 때문입니다. 따라서 비동기 호출을 지원하려면 새로운 유형의 필터를 커널에 추가해야 합니다: `IAsyncFunctionFilter`와 `IAsyncPromptFilter`. 이들은 현재 `IFunctionFilter`와 `IPromptFilter`와 동일하지만 비동기 메서드를 가집니다.

### 옵션 4 [제안] - PromptExecutionSettings의 일부로서의 메모리

이 제안은 위에서 설명한 기존 접근 방식 위에 SK에서 RAG 패턴을 구현하는 또 다른 가능한 방법입니다. `TextMemoryPlugin`과 유사하게, 이 접근 방식은 추상화 계층을 요구하며 각 벡터 DB 통합은 SK와 호환되기 위해 특정 인터페이스(기존 `IMemoryStore` 또는 완전히 새로운 인터페이스)를 구현해야 합니다. _배경 및 문제 설명_ 섹션에서 설명한 대로, 추상화 계층에는 장점과 단점이 있습니다.

사용자 코드는 다음과 같습니다:

```csharp
var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("model-id", "api-key")
    .Build();

var executionSettings = new OpenAIPromptExecutionSettings
{
    Temperature = 0.8,
    MemoryConfig = new()
    {
        // 이 서비스는 특정 수명으로 DI를 사용하여 등록할 수도 있습니다
        Memory = new ChromaMemoryStore("https://chroma-endpoint"),
        MinRelevanceScore = 0.8,
        Limit = 3
    }
};

var function = KernelFunctionFactory.CreateFromPrompt("What is my budget for 2024?", executionSettings);

var result = await kernel.InvokePromptAsync("What is my budget for 2024?");
```

데이터 검색과 프롬프트 연결은 `KernelFunctionFromPrompt` 클래스에서 뒤에서 발생합니다.

## 결정 결과

임시 결정은 Semantic Kernel에서 플러그인으로 메모리를 사용하는 방법에 대한 더 많은 예제를 제공하는 것입니다.

최종 결정은 다음 메모리 관련 요구 사항에 기반하여 준비될 예정입니다.
