## 제안

### IChatCompletion

이전:

```csharp
public interface IChatCompletion : IAIService
{
    ChatHistory CreateNewChat(string? instructions = null);

    Task<IReadOnlyList<IChatResult>> GetChatCompletionsAsync(ChatHistory chat, ...);

    Task<IReadOnlyList<IChatResult>> GetChatCompletionsAsync(string prompt, ...);

    IAsyncEnumerable<T> GetStreamingContentAsync<T>(ChatHistory chatHistory, ...);
}

public static class ChatCompletionExtensions
{
    public static async Task<string> GenerateMessageAsync(ChatHistory chat, ...);
}
```

이후:

```csharp
public interface IChatCompletion : IAIService
{
    Task<IReadOnlyList<ChatContent>> GetChatContentsAsync(ChatHistory chat, ..> tags)

    IAsyncEnumerable<StreamingChatContent> GetStreamingChatContentsAsync(ChatHistory chatHistory, ...);
}

public static class ChatCompletionExtensions
{
    //                       v 단일             vv 표준화된 프롬프트 (<message> 태그 파싱)
    public static async Task<ChatContent> GetChatContentAsync(string prompt, ...);

    //                       v 단일
    public static async Task<ChatContent> GetChatContentAsync(ChatHistory chatHistory, ...);

    public static IAsyncEnumerable<StreamingChatContent> GetStreamingChatContentsAsync(string prompt, ...);
}
```

### ITextCompletion

이전:

```csharp
public interface ITextCompletion : IAIService
{
    Task<IReadOnlyList<ITextResult>> GetCompletionsAsync(string prompt, ...);

    IAsyncEnumerable<T> GetStreamingContentAsync<T>(string prompt, ...);
}

public static class TextCompletionExtensions
{
    public static async Task<string> CompleteAsync(string text, ...);

    public static IAsyncEnumerable<StreamingContent> GetStreamingContentAsync(string input, ...);
}
```

이후:

```csharp
public interface ITextCompletion : IAIService
{
    Task<IReadOnlyList<TextContent>> GetTextContentsAsync(string prompt, ...);

    IAsyncEnumerable<StreamingTextContent> GetStreamingTextContentsAsync(string prompt, ...);
}

public static class TextCompletionExtensions
{
    public static async Task<TextContent> GetTextContentAsync(string prompt, ...);
}
```

## 콘텐츠 추상화

### 모델 비교

#### 현재 스트리밍 추상화

| 스트리밍 (현재)                              | 특수화된* 스트리밍 (현재)                                       |
| ------------------------------------------- | --------------------------------------------------------------- |
| `StreamingChatContent` : `StreamingContent` | `OpenAIStreamingChatContent`                                    |
| `StreamingTextContent` : `StreamingContent` | `OpenAIStreamingTextContent`, `HuggingFaceStreamingTextContent` |

#### 비스트리밍 추상화 (이전과 이후)

| 비스트리밍 (이전)             | 비스트리밍 (이후)              | 특수화된* 비스트리밍 (이후)                   |
| ----------------------------- | ------------------------------ | --------------------------------------------- |
| `IChatResult` : `IResultBase` | `ChatContent` : `ModelContent` | `OpenAIChatContent`                           |
| `ITextResult` : `IResultBase` | `TextContent` : `ModelContent` | `OpenAITextContent`, `HuggingFaceTextContent` |
| `ChatMessage`                 | `ChatContent` : `ModelContent` | `OpenAIChatContent`                           |

_\*특수화: 단일 AI 서비스에 특화된 커넥터 구현._

### 새로운 비스트리밍 추상화:

`ModelContent`는 `비스트리밍 콘텐츠` 최상위 추상화를 나타내도록 선택되었으며, 특수화가 가능하고 AI 서비스가 반환한 모든 정보를 포함합니다. (메타데이터, 원시 콘텐츠 등)

```csharp
/// <summary>
/// 모든 AI 비스트리밍 결과의 기본 클래스
/// </summary>
public abstract class ModelContent
{
    /// <summary>
    /// 원시 콘텐츠 객체 참조. (Breaking glass).
    /// </summary>
    public object? InnerContent { get; }

    /// <summary>
    /// 콘텐츠와 관련된 메타데이터.
    /// ⚠️ (토큰 사용량 + 추가 백엔드 API 메타데이터) 정보가 이 딕셔너리에 있습니다. 이전 IResult.ModelResult) ⚠️
    /// </summary>
    public Dictionary<string, object?>? Metadata { get; }

    /// <summary>
    /// <see cref="CompleteContent"/> 클래스의 새 인스턴스를 초기화합니다.
    /// </summary>
    /// <param name="rawContent">원시 콘텐츠 객체 참조</param>
    /// <param name="metadata">콘텐츠와 관련된 메타데이터</param>
    protected CompleteContent(object rawContent, Dictionary<string, object>? metadata = null)
    {
        this.InnerContent = rawContent;
        this.Metadata = metadata;
    }
}
```

```csharp
/// <summary>
/// 채팅 콘텐츠 추상화
/// </summary>
public class ChatContent : ModelContent
{
    /// <summary>
    /// 메시지 작성자의 역할
    /// </summary>
    public AuthorRole Role { get; set; }

    /// <summary>
    /// 메시지 내용
    /// </summary>
    public string Content { get; protected set; }

    /// <summary>
    /// <see cref="ChatContent"/> 클래스의 새 인스턴스를 생성합니다
    /// </summary>
    /// <param name="chatMessage"></param>
    /// <param name="metadata">추가 메타데이터를 위한 딕셔너리</param>
    public ChatContent(ChatMessage chatMessage, Dictionary<string, object>? metadata = null) : base(chatMessage, metadata)
    {
        this.Role = chatMessage.Role;
        this.Content = chatMessage.Content;
    }
}
```

```csharp
/// <summary>
/// 텍스트 콘텐츠 결과를 나타냅니다.
/// </summary>
public class TextContent : ModelContent
{
    /// <summary>
    /// 텍스트 콘텐츠.
    /// </summary>
    public string Text { get; set; }

    /// <summary>
    /// <see cref="TextContent"/> 클래스의 새 인스턴스를 초기화합니다.
    /// </summary>
    /// <param name="text">텍스트 콘텐츠</param>
    /// <param name="metadata">추가 메타데이터</param>
    public TextContent(string text, Dictionary<string, object>? metadata = null) : base(text, metadata)
    {
        this.Text = text;
    }
}
```

### 최종 사용자 경험

- `Function.InvokeAsync` 또는 `Kernel.InvokeAsync` 사용 시 최종 사용자 경험에 변경 없음
- 커넥터 API를 직접 사용할 때만 변경 사항

#### 예시 16 - 사용자 정의 LLM

이전

```csharp
await foreach (var message in textCompletion.GetStreamingContentAsync(prompt, executionSettings))
{
    Console.Write(message);
}
```

이후

```csharp
await foreach (var message in textCompletion.GetStreamingTextContentAsync(prompt, executionSettings))
{
    Console.Write(message);
}
```

#### 예시 17 - ChatGPT

이전

```csharp
string reply = await chatGPT.GenerateMessageAsync(chatHistory);
chatHistory.AddAssistantMessage(reply);
```

이후

```csharp
var reply = await chatGPT.GetChatContentAsync(chatHistory);
chatHistory.AddMessage(reply);

// 또는
chatHistory.AddAssistantMessage(reply.Content);
```

### 정리

모든 이전 인터페이스와 클래스는 새로운 것으로 대체되어 제거됩니다.
