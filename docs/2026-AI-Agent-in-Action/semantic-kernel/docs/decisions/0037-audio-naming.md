---
# 선택적 요소입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: proposed
contact: dmytrostruk
date: 2023-02-22
deciders: sergeymenshykh, markwallace, rbarreto, dmytrostruk
---

# 오디오 추상화 및 구현 명명

## 배경 및 문제 설명

### 추상화

현재 오디오 작업을 위한 다음 인터페이스가 있습니다:

- IAudioToTextService
- ITextToAudioService

`IAudioToTextService`는 오디오를 입력으로 받아 텍스트를 출력으로 반환하고, `ITextToAudioService`는 텍스트를 입력으로 받아 오디오를 출력으로 반환합니다.

이러한 추상화의 명명은 오디오 변환의 특성을 나타내지 않습니다. 예를 들어, `IAudioToTextService` 인터페이스는 오디오 전사인지 오디오 번역인지를 나타내지 않습니다. 이는 문제인 동시에 장점일 수 있습니다.

일반적인 텍스트-오디오 및 오디오-텍스트 인터페이스를 가짐으로써, 결국 텍스트-입력/오디오-출력 계약이고 그 반대도 마찬가지이므로 동일한 인터페이스를 사용하여 다양한 유형의 오디오 변환(전사, 번역, 음성 인식, 음악 인식 등)을 커버할 수 있습니다. 이 경우, 정확히 동일한 메서드 시그니처를 포함할 수 있는 여러 오디오 인터페이스 생성을 피할 수 있습니다.

반면에, 향후 사용자 애플리케이션이나 커널 자체에서 오디오 변환의 특정 추상화를 구분해야 하는 경우 문제가 될 수 있습니다.

### 구현

또 다른 문제는 OpenAI용 오디오 구현 명명입니다:

- AzureOpenAIAudioToTextService
- OpenAIAudioToTextService
- AzureOpenAITextToAudioService
- OpenAITextToAudioService

이 경우, OpenAI 문서의 공식 명명을 사용하지 않아 혼동을 줄 수 있으므로 명명이 올바르지 않습니다. 예를 들어, 오디오에서 텍스트로의 변환은 [Speech to text](https://platform.openai.com/docs/guides/speech-to-text)라고 합니다.

그러나 `OpenAIAudioToTextService`를 `OpenAISpeechToTextService`로 이름을 변경하는 것만으로는 충분하지 않을 수 있습니다. 음성-텍스트 API에는 `transcriptions`과 `translations` 두 가지 다른 엔드포인트가 있기 때문입니다. 현재 OpenAI 오디오 커넥터는 `transcriptions` 엔드포인트를 사용하지만, `OpenAISpeechToTextService`라는 이름은 이를 반영하지 않습니다. 가능한 이름은 `OpenAIAudioTranscriptionService`입니다.

## 검토된 옵션

### [추상화 - 옵션 #1]

현재 명명을 그대로 유지하고(`IAudioToTextService`, `ITextToAudioService`), 특정 오디오 변환이 기존 인터페이스 시그니처에 맞지 않는 것을 볼 때까지 모든 오디오 관련 커넥터에 이 인터페이스를 사용합니다.

이 옵션의 주요 질문은 - 비즈니스 로직 및/또는 커널 자체에서 오디오 변환 유형(전사, 번역 등)을 구분해야 할 가능성이 있을 수 있는가?

아마도 예, 애플리케이션이 로직에서 `transcription`과 `translation`을 모두 사용하려 할 때입니다. 구체적인 변환을 수행하기 위해 어떤 오디오 인터페이스를 주입해야 하는지 명확하지 않습니다.

이 경우에도 현재 인터페이스 이름을 유지할 수 있지만, 구체적인 오디오 변환 유형을 지정하기 위해 자식 인터페이스를 생성할 수 있습니다. 예를 들어:

```csharp
public interface IAudioTranscriptionService : IAudioToTextService {}
public interface IAudioTranslationService : IAudioToTextService {}
```

이것의 단점은 이러한 인터페이스가 대부분 비어 있을 것이라는 점입니다. 주요 목적은 둘 다 사용할 때 구분할 수 있는 능력입니다.

### [추상화 - 옵션 #2]

`IAudioToTextService`와 `ITextToAudioService`를 더 구체적인 변환 유형으로 이름 변경하고(예: `ITextToSpeechService`), 다른 유형의 오디오 변환에 대해서는 명명만 다른 정확히 동일한 인터페이스가 될 수 있는 별도의 인터페이스를 생성합니다.

이 접근 방식의 단점은 동일한 유형의 변환(예: 음성-텍스트)에 대해서도, 다른 AI 제공자에서 이 기능의 이름이 다르므로 좋은 이름을 고르기 어려워 불일치를 피하기 어렵다는 것입니다. 예를 들어, OpenAI에서는 [Audio transcription](https://platform.openai.com/docs/api-reference/audio/createTranscription)이고 Hugging Face에서는 [Automatic Speech Recognition](https://huggingface.co/models?pipeline_tag=automatic-speech-recognition)입니다.

현재 이름(`IAudioToTextService`)의 장점은 더 일반적이며 Hugging Face와 OpenAI 서비스를 모두 커버한다는 것입니다. AI 기능이 아닌 인터페이스 계약(오디오-입력/텍스트-출력)에 따라 명명되었습니다.

### [구현]

구현의 경우에도 두 가지 옵션이 있습니다 - 그대로 유지하거나 AI 제공자가 해당 기능을 부르는 방식에 따라 클래스 이름을 변경합니다. 사용자 관점에서 어떤 구체적인 OpenAI 기능이 사용되는지(예: `transcription` 또는 `translation`) 이해하기 쉬우므로, 이에 대한 관련 문서를 찾기 쉬워져 이름 변경이 최선의 선택입니다.

제안된 이름 변경:

- AzureOpenAIAudioToTextService -> AzureOpenAIAudioTranscriptionService
- OpenAIAudioToTextService -> OpenAIAudioTranscriptionService
- AzureOpenAITextToAudioService -> AzureOpenAITextToSpeechService
- OpenAITextToAudioService -> OpenAITextToSpeechService

## 명명 비교

| AI 제공자  | 오디오 변환    | 제안 인터페이스         | 제안 구현             |
| ------------ | ------------------- | -------------------------- | ----------------------------------- |
| Microsoft    | 음성-텍스트      | IAudioTranscriptionService | MicrosoftSpeechToTextService        |
| Hugging Face | 음성 인식  | IAudioTranscriptionService | HuggingFaceSpeechRecognitionService |
| AssemblyAI   | 전사       | IAudioTranscriptionService | AssemblyAIAudioTranscriptionService |
| OpenAI       | 오디오 전사 | IAudioTranscriptionService | OpenAIAudioTranscriptionService     |
| Google       | 음성-텍스트      | IAudioTranscriptionService | GoogleSpeechToTextService           |
| Amazon       | 전사       | IAudioTranscriptionService | AmazonAudioTranscriptionService     |
| Microsoft    | 음성 번역  | IAudioTranslationService   | MicrosoftSpeechTranslationService   |
| OpenAI       | 오디오 번역   | IAudioTranslationService   | OpenAIAudioTranslationService       |
| Meta         | 텍스트-음악       | ITextToMusicService        | MetaTextToMusicService              |
| Microsoft    | 텍스트-음성      | ITextToSpeechService       | MicrosoftTextToSpeechService        |
| OpenAI       | 텍스트-음성      | ITextToSpeechService       | OpenAITextToSpeechService           |
| Google       | 텍스트-음성      | ITextToSpeechService       | GoogleTextToSpeechService           |
| Amazon       | 텍스트-음성      | ITextToSpeechService       | AmazonTextToSpeechService           |
| Hugging Face | 텍스트-음성      | ITextToSpeechService       | HuggingFaceTextToSpeechService      |
| Meta         | 텍스트-사운드       | 미정                        | 미정                                 |
| Hugging Face | 텍스트-오디오       | 미정                        | 미정                                 |
| Hugging Face | 오디오-오디오      | 미정                        | 미정                                 |

## 결정 결과

기존 오디오 커넥터를 `명명 비교` 표에 제공된 명명에 따라 이름 변경하고, 향후 오디오 추상화 및 구현에 동일한 명명을 사용합니다.
