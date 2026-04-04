---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: proposed
contact: rogerbarreto
date: 2024-05-02
deciders: rogerbarreto, markwallace-microsoft, sergeymenkshi, dmytrostruk, sergeymenshik, westey-m, matthewbolanos
consulted: stephentoub
---

# Kernel Content 타입 졸업(Graduation)

## 컨텍스트 및 문제 설명

현재 많은 Content 타입이 실험적 상태에 있으며, 이 ADR은 이를 안정적 상태로 졸업시키는 방법에 대한 옵션을 제공합니다.

## 결정 요인

- 호환성 깨짐 변경 없음
- 단순한 접근 방식, 최소한의 복잡성
- 확장성 허용
- 간결하고 명확함

## BinaryContent 졸업

이 콘텐츠는 콘텐츠 특수화에 의해 사용되거나, 특정 타입이 아닌 경우 직접 사용되어야 합니다. "application/octet-stream" MIME 타입과 유사합니다.

> **Application/Octet-Stream**은 임의의 바이너리 데이터 또는 다른 더 구체적인 MIME 타입에 맞지 않는 바이트 스트림에 사용되는 MIME입니다. 이 MIME 타입은 기본 또는 폴백 타입으로 자주 사용되며, 파일을 순수 바이너리 데이터로 처리해야 함을 나타냅니다.

#### 현재

```csharp
public class BinaryContent : KernelContent
{
    public ReadOnlyMemory<byte>? Content { get; set; }
    public async Task<Stream> GetStreamAsync()
    public async Task<ReadOnlyMemory<byte>> GetContentAsync()

    ctor(ReadOnlyMemory<byte>? content = null)
    ctor(Func<Task<Stream>> streamProvider)
}
```

#### 제안

```csharp
public class BinaryContent : KernelContent
{
    ReadOnlyMemory<byte>? Data { get; set; }
    Uri? Uri { get; set; }
    string DataUri { get; set; }

    bool CanRead { get; } // 콘텐츠가 바이트 또는 data uri로 읽을 수 있는지 나타냄

    ctor(Uri? referencedUri)
    ctor(string dataUri)
    // MimeType은 선택 사항이 아니지만 nullable이며, 가능한 한 이 정보가 항상 전달되도록 권장합니다.
    ctor(ReadOnlyMemory<byte> data, string? mimeType)
    ctor() // 직렬화 시나리오를 위한 빈 생성자
}
```

- Content 속성 없음 (특수화된 타입 컨텍스트에서 사용 시 충돌 및/또는 오해의 소지 방지)

  예시:

  - `PdfContent.Content` (텍스트 전용 정보를 설명)
  - `PictureContent.Content` (`Picture` 타입을 노출)

- 지연(lazy loaded) 콘텐츠 공급자에서 벗어남, 더 단순한 API.
- `GetContentAsync` 제거 (더 이상 지연 API 없음)
- 바이트 배열 콘텐츠 정보의 setter 및 getter로 `Data` 속성 추가.

  이 속성을 설정하면 `DataUri`의 base64 데이터 부분이 재정의됩니다.

- data uri 콘텐츠 정보의 setter 및 getter로 `DataUri` 속성 추가.

  이 속성을 설정하면 현재 페이로드 세부 정보에 따라 `Data` 및 `MimeType` 속성이 재정의됩니다.

- 참조 콘텐츠 정보를 위한 `Uri` 속성 추가. 이 속성은 `UriData`를 허용하지 않으며 비-data 스킴만 지원합니다.
- `CanRead` 속성 추가 (`Data` 또는 `DataUri` 속성을 사용하여 콘텐츠를 읽을 수 있는지 나타냄)
- Uri, DataUri 및 ByteArray + MimeType 생성을 위한 전용 생성자.

장점:

- 지연 콘텐츠가 없어 더 단순한 API와 콘텐츠에 대한 단일 책임.
- `Data` 또는 `DataUri` 형식 모두로 쓰기 및 읽기 가능.
- 특수화된 컨텍스트에서 일반적인 `Uri` 참조 속성을 가질 수 있음.
- 완전한 직렬화 가능.
- Data Uri 파라미터 지원 (직렬화 포함).
- Data Uri 및 Base64 유효성 검사
- Data Uri와 Data를 동적으로 생성 가능
- `CanRead`로 콘텐츠가 `bytes` 또는 `DataUri`로 읽을 수 있는지 명확하게 식별.

단점:

- 실험적 `BinaryContent` 사용자에 대한 호환성 깨짐 변경

### Data Uri 파라미터

[RFC 2397](https://datatracker.ietf.org/doc/html/rfc2397)에 따르면, data uri 스킴은 파라미터를 지원합니다.

data uri에서 가져온 모든 파라미터는 "data-uri-parameter-name"을 키로 하여 Metadata 딕셔너리에 추가됩니다.

#### 파라미터가 포함된 data uri를 제공하면 해당 파라미터가 Metadata 딕셔너리에 포함됩니다.

```csharp
var content = new BinaryContent("data:application/json;parameter1=value1;parameter2=value2;base64,SGVsbG8gV29ybGQ=");
var parameter1 = content.Metadata["data-uri-parameter1"]; // value1
var parameter2 = content.Metadata["data-uri-parameter2"]; // value2
```

#### 콘텐츠 역직렬화 시에도 DataUri 속성을 가져올 때 해당 파라미터가 포함됩니다.

```csharp
var json = """
{
    "metadata":
    {
        "data-uri-parameter1":"value1",
        "data-uri-parameter2":"value2"
    },
    "mimeType":"application/json",
    "data":"SGVsbG8gV29ybGQ="
}
""";
var content = JsonSerializer.Deserialize<BinaryContent>(json);
content.DataUri // "data:application/json;parameter1=value1;parameter2=value2;base64,SGVsbG8gV29ybGQ="
```

### 특수화 예시

#### ImageContent

```csharp
public class ImageContent : BinaryContent
{
    ctor(Uri uri) : base(uri)
    ctor(string dataUri) : base(dataUri)
    ctor(ReadOnlyMemory<byte> data, string? mimeType) : base(data, mimeType)
    ctor() // 직렬화 시나리오
}

public class AudioContent : BinaryContent
{
    ctor(Uri uri)
}
```

장점:

- data uri 대용량 콘텐츠 지원
- dataUrl 스킴을 사용하여 바이너리 ImageContent를 생성하고 Url로도 참조 가능.
- Data Uri 유효성 검사 지원

## ImageContent 졸업

⚠️ 현재 이것은 실험적이 아니며, 잠재적 이점을 가진 안정적 상태로 졸업하기 위해 호환성 깨짐 변경이 필요합니다.

### 문제점

1. 현재 `ImageContent`가 `BinaryContent`에서 파생되지 않음
2. 같은 인스턴스에서 서로 다른 `DataUri`와 `Data`를 동시에 가질 수 있는 바람직하지 않은 동작
3. `Uri` 속성이 data uri와 참조 uri 정보 모두에 사용됨
4. `Uri`가 대규모 언어 data uri 형식을 지원하지 않음
5. 콘텐츠가 읽기 가능한지 `sk 개발자`에게 명확하지 않음

#### 현재

```csharp
public class ImageContent : KernelContent
{
    Uri? Uri { get; set; }
    public ReadOnlyMemory<byte>? Data { get; set; }

    ctor(ReadOnlyMemory<byte>? data)
    ctor(Uri uri)
    ctor()
}
```

#### 제안

`BinaryContent` 섹션 예시에서 이미 보여준 것처럼, `ImageContent`는 `BinaryContent` 특수화로 졸업하여 그것이 가져오는 모든 이점을 상속받을 수 있습니다.

```csharp
public class ImageContent : BinaryContent
{
    ctor(Uri uri) : base(uri)
    ctor(string dataUri) : base(dataUri)
    ctor(ReadOnlyMemory<byte> data, string? mimeType) : base(data, mimeType)
    ctor() // 직렬화 시나리오
}
```

장점:

- `BinaryContent` 타입으로 사용 가능
- `Data` 또는 `DataUri` 형식 모두로 쓰기 및 읽기 가능.
- 참조 위치를 위한 전용 `Uri`를 가질 수 있음.
- 완전한 직렬화 가능.
- Data Uri 파라미터 지원 (직렬화 포함).
- Data Uri 및 Base64 유효성 검사
- 검색 가능
- Data Uri와 Data를 동적으로 생성 가능
- `CanRead`로 콘텐츠가 `bytes` 또는 `DataUri`로 읽을 수 있는지 명확하게 식별.

단점:

- ⚠️ `ImageContent` 사용자에 대한 호환성 깨짐 변경

### ImageContent 호환성 깨짐 변경

- `Uri` 속성은 참조 위치(비-data-uri)에만 전용으로 사용되며, `data-uri` 형식을 추가하려고 하면 대신 `DataUri` 속성 사용을 제안하는 예외가 발생합니다.
- `DataUri`를 설정하면 제공된 정보에 따라 `Data` 및 `MimeType` 속성이 재정의됩니다.
- 유효하지 않은 `DataUri`를 설정하려고 하면 예외가 발생합니다.
- `Data`를 설정하면 이제 `DataUri`의 데이터 부분이 재정의됩니다.
- `Uri` 속성에 data-uri가 있는 `ImageContent`를 직렬화하려고 하면 예외가 발생합니다.

## AudioContent 졸업

`ImageContent` 제안과 유사하게 `AudioContent`도 `BinaryContent`로 졸업할 수 있습니다.

#### 현재

1. 현재 `AudioContent`가 `Uri` 참조 위치를 지원하지 않음
2. `Uri` 속성이 data uri와 참조 uri 정보 모두에 사용됨
3. `Uri`가 대규모 언어 data uri 형식을 지원하지 않음
4. 콘텐츠가 읽기 가능한지 `sk 개발자`에게 명확하지 않음

```csharp
public class AudioContent : KernelContent
{
    public ReadOnlyMemory<byte>? Data { get; set; }

    ctor(ReadOnlyMemory<byte>? data)
    ctor()
}
```

#### 제안

```csharp
public class AudioContent : BinaryContent
{
    ctor(Uri uri) : base(uri)
    ctor(string dataUri) : base(dataUri)
    ctor(ReadOnlyMemory<byte> data, string? mimeType) : base(data, mimeType)
    ctor() // 직렬화 시나리오
}
```

장점:

- `BinaryContent` 타입으로 사용 가능
- `Data` 또는 `DataUri` 형식 모두로 쓰기 및 읽기 가능.
- 참조 위치를 위한 전용 `Uri`를 가질 수 있음.
- 완전한 직렬화 가능.
- Data Uri 파라미터 지원 (직렬화 포함).
- Data Uri 및 Base64 유효성 검사
- 검색 가능
- Data Uri와 Data를 동적으로 생성 가능
- `CanRead`로 콘텐츠가 `bytes` 또는 `DataUri`로 읽을 수 있는지 명확하게 식별.

단점:

- `AudioContent` 사용자에 대한 실험적 호환성 깨짐 변경

## FunctionCallContent 졸업

### 현재

현재 구조에 대한 변경이 필요하지 않습니다.

잠재적으로 기본 `FunctionContent`를 가질 수 있지만, 동시에 이 두 가지가 `KernelContent`에서 파생되는 것은 명확한 관심사 분리를 제공하므로 좋습니다.

```csharp
public sealed class FunctionCallContent : KernelContent
{
    public string? Id { get; }
    public string? PluginName { get; }
    public string FunctionName { get; }
    public KernelArguments? Arguments { get; }
    public Exception? Exception { get; init; }

    ctor(string functionName, string? pluginName = null, string? id = null, KernelArguments? arguments = null)

    public async Task<FunctionResultContent> InvokeAsync(Kernel kernel, CancellationToken cancellationToken = default)
    public static IEnumerable<FunctionCallContent> GetFunctionCalls(ChatMessageContent messageContent)
}
```

## FunctionResultContent 졸업

일부 변경이 필요할 수 있지만 현재 구조는 좋습니다.

### 현재

- 순수성 관점에서 `Id` 속성은 응답 Id가 아닌 함수 호출 Id이기 때문에 혼란을 줄 수 있습니다.
- 생성자에서 같은 타입에 대해 `functionCall`과 `functionCallContent`라는 다른 파라미터 이름을 사용합니다.

```csharp
public sealed class FunctionResultContent : KernelContent
{
    public string? Id { get; }
    public string? PluginName { get; }
    public string? FunctionName { get; }
    public object? Result { get; }

    ctor(string? functionName = null, string? pluginName = null, string? id = null, object? result = null)
    ctor(FunctionCallContent functionCall, object? result = null)
    ctor(FunctionCallContent functionCallContent, FunctionResult result)
}
```

### 제안 - 옵션 1

- 혼란을 피하기 위해 `Id`를 `CallId`로 이름 변경.
- `ctor` 파라미터 이름 조정.

```csharp
public sealed class FunctionResultContent : KernelContent
{
    public string? CallId { get; }
    public string? PluginName { get; }
    public string? FunctionName { get; }
    public object? Result { get; }

    ctor(string? functionName = null, string? pluginName = null, string? callId = null, object? result = null)
    ctor(FunctionCallContent functionCallContent, object? result = null)
    ctor(FunctionCallContent functionCallContent, FunctionResult functionResult)
}
```

### 제안 - 옵션 2

합성(composition)을 사용하여 `FunctionResultContent` 내에 전용 CallContent를 갖습니다.

장점:

- `CallContent`에 결과에서 함수를 다시 호출할 수 있는 옵션이 있어 일부 시나리오에서 편리함
- 결과가 어디에서 왔는지, 그리고 결과 전용 데이터(루트 클래스)가 무엇인지 명확하게 함.
- 호출에 사용된 인수에 대한 정보.

단점:

- 결과에서 `call` 세부 정보를 가져오기 위한 추가 단계 도입.

```csharp
public sealed class FunctionResultContent : KernelContent
{
    public FunctionCallContent CallContent { get; }
    public object? Result { get; }

    ctor(FunctionCallContent functionCallContent, object? result = null)
    ctor(FunctionCallContent functionCallContent, FunctionResult functionResult)
}
```

## FileReferenceContent + AnnotationContent

이 두 콘텐츠는 직렬화 편의를 위해 `SemanticKernel.Abstractions`에 추가되었지만, **OpenAI Assistant API**에 매우 특화되어 있으므로 지금은 실험적으로 유지해야 합니다.

졸업 시 아래 제안에 따라 `SemanticKernel.Agents.OpenAI`로 이동해야 합니다.

```csharp
#pragma warning disable SKEXP0110
[JsonDerivedType(typeof(AnnotationContent), typeDiscriminator: nameof(AnnotationContent))]
[JsonDerivedType(typeof(FileReferenceContent), typeDiscriminator: nameof(FileReferenceContent))]
#pragma warning disable SKEXP0110
public abstract class KernelContent { ... }
```

이러한 결합은 `KernelContent` 특수화를 가진 다른 패키지에서 권장되지 않습니다.

### 솔루션 - [JsonConverter](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/converters-how-to?pivots=dotnet-6-0#registration-sample---jsonconverter-on-a-type) 어노테이션 사용

`Agents.OpenAI` 프로젝트에 해당 타입의 직렬화 및 역직렬화를 처리하기 위한 전용 `JsonConverter` 헬퍼를 생성합니다.

사용할 `JsonConverter`를 나타내기 위해 해당 Content 타입에 `[JsonConverter(typeof(KernelContentConverter))]` 어트리뷰트를 추가합니다.

### Agents.OpenAI의 JsonConverter 예시

```csharp
public class KernelContentConverter : JsonConverter<KernelContent>
{
    public override KernelContent Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        using (var jsonDoc = JsonDocument.ParseValue(ref reader))
        {
            var root = jsonDoc.RootElement;
            var typeDiscriminator = root.GetProperty("TypeDiscriminator").GetString();
            switch (typeDiscriminator)
            {
                case nameof(AnnotationContent):
                    return JsonSerializer.Deserialize<AnnotationContent>(root.GetRawText(), options);
                case nameof(FileReferenceContent):
                    return JsonSerializer.Deserialize<FileReferenceContent>(root.GetRawText(), options);
                default:
                    throw new NotSupportedException($"Type discriminator '{typeDiscriminator}' is not supported.");
            }
        }
    }

    public override void Write(Utf8JsonWriter writer, KernelContent value, JsonSerializerOptions options)
    {
        JsonSerializer.Serialize(writer, value, value.GetType(), options);
    }
}

[JsonConverter(typeof(KernelContentConverter))]
public class FileReferenceContent : KernelContent
{
    public string FileId { get; init; } = string.Empty;
    ctor()
    ctor(string fileId, ...)
}

[JsonConverter(typeof(KernelContentConverter))]
public class AnnotationContent : KernelContent
{
    public string? FileId { get; init; }
    public string? Quote { get; init; }
    public int StartIndex { get; init; }
    public int EndIndex { get; init; }
    public ctor()
    public ctor(...)
}
```

## 결정 결과

- `BinaryContent`: 승인됨.
- `ImageContent`: `BinaryContent` 특수화를 사용한 호환성 깨짐 변경 승인됨. 현재 `ImageContent` 동작이 바람직하지 않으므로 하위 호환성 없음.
- `AudioContent`: `BinaryContent` 특수화를 사용한 실험적 호환성 깨짐 변경.
- `FunctionCallContent`: 현재 상태 그대로 졸업.
- `FunctionResultContent`: 함수 호출 Id인지 응답 id인지에 대한 혼란을 피하기 위해 `Id` 속성에서 `CallId`로의 실험적 호환성 깨짐 변경.
- `FileReferenceContent` 및 `AnnotationContent`: 변경 없음, 실험적으로 계속 유지.
