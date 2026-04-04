---
# 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: proposed
contact: crickman, mabolan, semenshi
date: 2024-01-16
---

# 파일 서비스

## 배경 및 문제 설명
OpenAI는 *어시스턴트 검색* 또는 *모델 미세 조정*에 사용할 파일을 업로드하기 위한 파일 서비스를 제공합니다: `https://api.openai.com/v1/files`

다른 제공자들도 Gemini와 같이 일종의 파일 서비스를 제공할 수 있습니다.

> 참고: *Azure Open AI*는 현재 OpenAI 파일 서비스 API를 지원하지 않습니다.

## 검토된 옵션

1. `Microsoft.SemanticKernel.Experimental.Agents`에 OpenAI 파일 서비스 지원 추가
2. 파일 서비스 추상화를 추가하고 OpenAI 지원 구현
3. 추상화 없이 OpenAI 파일 서비스 지원 추가

## 결정 결과

> 옵션 3. **추상화 없이 OpenAI 파일 서비스 지원 추가**
> 실험적 레이블을 사용하여 코드를 표시: `SKEXP0010`

일반화된 파일 서비스 인터페이스를 정의하면 *OpenAI* 외에 다른 벤더를 위한 확장 포인트를 제공합니다.

## 옵션별 장단점

### 옵션 1. `Microsoft.SemanticKernel.Experimental.Agents`에 OpenAI 파일 서비스 지원 추가
**장점:**
1. 기존 AI 커넥터에 영향 없음.

**단점:**
1. AI 커넥터를 통한 재사용 불가.
1. 공통 추상화 없음.
1. OpenAI 어시스턴트 이외의 용도에 대해 부자연스러운 의존성 바인딩.

### 옵션 2. 파일 서비스 추상화를 추가하고 OpenAI 지원 구현
**장점:**
1. 파일 서비스 상호작용을 위한 공통 인터페이스 정의.
1. 벤더별 서비스에 대한 특수화 가능.

**단점:**
1. 다른 시스템이 기존 가정에서 벗어날 수 있음.


### 옵션 3. 추상화 없이 OpenAI 파일 서비스 지원 추가
**장점:**
1. OpenAI 파일 서비스 지원 제공.

**단점:**
1. 다른 벤더의 파일 서비스 제공은 공통성 없이 케이스별로 지원.


## 추가 정보

### BinaryContent 시그니처

> 참고: `BinaryContent` 객체는 어떤 생성자가 호출되었는지에 관계없이 `BinaryData` 또는 `Stream`을 제공할 수 있습니다.

#### `Microsoft.SemanticKernel.Abstractions`

```csharp
namespace Microsoft.SemanticKernel;

/// <summary>
/// 바이너리 콘텐츠를 나타냅니다.
/// </summary>
public sealed class BinaryContent : KernelContent
{
    public BinaryContent(
        BinaryData content,
        string? modelId = null,
        object? innerContent = null,
        IReadOnlyDictionary<string, object?>? metadata = null);

    public BinaryContent(
        Func<Stream> streamProvider,
        string? modelId = null,
        object? innerContent = null,
        IReadOnlyDictionary<string, object?>? metadata = null);

    public Task<BinaryData> GetContentAsync();

    public Task<Stream> GetStreamAsync();
}
```
### 옵션 3의 시그니처:

#### `Microsoft.SemanticKernel.Connectors.OpenAI`
```csharp
namespace Microsoft.SemanticKernel.Connectors.OpenAI;

public sealed class OpenAIFileService
{
    public async Task<OpenAIFileReference> GetFileAsync(
        string id,
        CancellationToken cancellationToken = default);

    public async Task<IEnumerable<OpenAIFileReference>> GetFilesAsync(CancellationToken cancellationToken = default);

    public async Task<BinaryContent> GetFileContentAsync(
        string id,
        CancellationToken cancellationToken = default);

    public async Task DeleteFileAsync(
        string id,
        CancellationToken cancellationToken = default);

    public async Task<OpenAIFileReference> UploadContentAsync(
        BinaryContent content,
        OpenAIFileUploadExecutionSettings settings,
        CancellationToken cancellationToken = default);
}

public sealed class OpenAIFileUploadExecutionSettings
{
    public string FileName { get; }
 
    public OpenAIFilePurpose Purpose { get; }
}

public sealed class OpenAIFileReference
{
    public string Id { get; set; }

    public DateTime CreatedTimestamp { get; set; }

    public string FileName { get; set; }
    
    public OpenAIFilePurpose Purpose { get; set; }

    public int SizeInBytes { get; set; }
}

public enum OpenAIFilePurpose
{
    Assistants,
    Finetuning,
}
```
