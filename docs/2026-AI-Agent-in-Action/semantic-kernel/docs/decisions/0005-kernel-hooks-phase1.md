---
# 이 항목들은 선택 사항입니다. 필요 없는 항목은 자유롭게 제거하세요.
status: accepted
contact: rogerbarreto
date: 2023-05-29
deciders: rogerbarreto, shawncal, stephentoub
consulted:
informed:
---

# Kernel/Function 핸들러 - 1단계

## 배경 및 문제 상황

Kernel 함수 호출자는 Kernel에서 모든 함수 실행을 시도하기 전후에 처리/가로챌 수 있어야 합니다. 이를 통해 프롬프트 수정, 실행 중단, 출력 수정 등 다음과 같은 다양한 시나리오를 가능하게 합니다:

- 사전 실행 / 함수 호출 전

  - 가져오기: SKContext
  - 설정: 함수에 전달되는 입력 매개변수 수정
  - 설정: 파이프라인 실행 중단/취소
  - 설정: 함수 실행 건너뛰기

- 사후 실행 / 함수 호출 후

  - 가져오기: LLM 모델 결과 (토큰 사용량, 중지 시퀀스, ...)
  - 가져오기: SKContext
  - 가져오기: 출력 매개변수
  - 설정: 출력 매개변수 내용 수정 (출력 반환 전)
  - 설정: 파이프라인 실행 취소
  - 설정: 함수 실행 반복

## 범위 밖 (2단계에서 다룰 예정)

- 사전 실행 / 함수 호출 전

  - 가져오기: 렌더링된 프롬프트
  - 가져오기: 현재 사용된 설정
  - 설정: 렌더링된 프롬프트 수정

- 사후 실행 / 함수 호출 후
  - 가져오기: 렌더링된 프롬프트
  - 가져오기: 현재 사용된 설정

## 결정 동인

- 아키텍처 변경과 관련된 의사결정 과정은 커뮤니티에 투명하게 공개되어야 합니다.
- 결정 기록은 저장소에 저장되며, 다양한 언어 포팅에 참여하는 팀들이 쉽게 찾을 수 있어야 합니다.
- 단순하고, 확장 가능하며, 이해하기 쉬워야 합니다.

## 검토된 옵션

1. 콜백 등록 + 재귀
2. 단일 콜백
3. 이벤트 기반 등록
4. 미들웨어
5. ISKFunction 이벤트 지원 인터페이스

## 각 옵션의 장단점

### 1. 콜백 등록 재귀 델리게이트 (Kernel, Plan, Function)

- Plan 및 Function 수준에서 구성으로 지정하여 트리거될 콜백 핸들러를 지정할 수 있습니다.

장점:

- (Get/Set) 시나리오에서 델리게이트 시그니처에 매개변수로 노출된 데이터를 관찰하고 변경하는 일반적인 패턴
- 콜백을 등록하면 향후 함수 실행을 취소하는 데 사용할 수 있는 등록 객체가 반환됩니다.
- 재귀 접근 방식으로 동일한 이벤트에 여러 콜백을 등록할 수 있으며, 기존 콜백 위에 콜백을 등록할 수도 있습니다.

단점:

- 재귀 접근 방식에서 등록이 더 많은 메모리를 사용할 수 있으며, 함수나 Plan이 해제될 때만 가비지 수집될 수 있습니다.

### 2. 단일 콜백 델리게이트 (Kernel, Plan, Function)

- Kernel 수준에서 구성으로 지정하여 트리거될 콜백 핸들러를 지정할 수 있습니다.
  - 함수 생성 시 지정: 함수 생성자의 일부로 트리거될 콜백 핸들러를 지정할 수 있습니다.
  - 함수 호출 시 지정: 함수 호출의 일부로 트리거될 콜백 핸들러를 매개변수로 지정할 수 있습니다.

장점:

- (Get/Set) 시나리오에서 델리게이트 시그니처에 매개변수로 노출된 데이터를 관찰하고 변경하는 일반적인 패턴

단점:

- 특정 이벤트(Pre, Post, InExecution)를 관찰하는 메서드가 하나로 제한됩니다. - 매개변수로 사용될 때 함수에 세 개의 새로운 매개변수가 필요합니다. (함수 호출 시 지정) - 추가 단점

### 3. 이벤트 기반 등록 (Kernel 전용)

IKernel과 ISKFunction 모두에서 호출자가 상호작용하기 위해 관찰할 수 있는 이벤트를 노출합니다.

장점:

- 동일한 이벤트에 여러 리스너를 등록할 수 있습니다.
- 리스너를 자유롭게 등록하고 해제할 수 있습니다.
- (Get/Set) 시나리오에서 이벤트 시그니처에 매개변수로 노출된 데이터를 관찰하고 변경하는 일반적인 패턴 (EventArgs)

단점:

- 이벤트 핸들러는 void이므로 EventArgs를 참조로 전달하는 것이 데이터를 수정하는 유일한 방법입니다.
- 비동기 패턴/멀티스레딩에 대한 지원이 얼마나 되는지 불분명합니다.
- `ISKFunction.InvokeAsync`를 지원하지 않습니다.

### 4. 미들웨어 (Kernel 전용)

Kernel 수준에서 지정되며, IKernel.RunAsync 작업을 사용할 때만 사용됩니다. 이 패턴은 asp.net core 미들웨어와 유사하며, 컨텍스트와 requestdelegate next로 파이프라인을 실행하여 사전/사후 조건을 제어합니다.

장점:

- 사전/사후 데이터 설정/필터링을 처리하는 일반적인 패턴

단점:

- 함수는 자체 인스턴스에서 실행될 수 있으며, 미들웨어는 함수 호출을 가로채기/관찰하기 위한 외부 컨테이너/관리자(Kernel)의 존재와 더 많은 복잡성을 시사합니다.

### 5. ISKFunction 이벤트 지원 인터페이스

    ```csharp
    class Kernel : IKernel
    {
        RunAsync() {
            var functionInvokingArgs = await this.TriggerEvent<FunctionInvokingEventArgs>(this.FunctionInvoking, skFunction, context);

            var functionResult = await skFunction.InvokeAsync(context, cancellationToken: cancellationToken);

            var functionInvokedArgs = await this.TriggerEvent<FunctionInvokedEventArgs>(
                this.FunctionInvoked,
                skFunction,
                context);
        }

        private TEventArgs? TriggerEvent<TEventArgs>(EventHandler<TEventArgs>? eventHandler, ISKFunction function, SKContext context) where TEventArgs : SKEventArgs
        {
            if (eventHandler is null)
            {
                return null;
            }

            if (function is ISKFunctionEventSupport<TEventArgs> supportedFunction)
            {
                var eventArgs = await supportedFunction.PrepareEventArgsAsync(context);
                eventHandler.Invoke(this, eventArgs);
                return eventArgs;
            }

            // 추가 인터페이스로 데이터를 추가하는 것에 대해 고려합니다.

            // 함수가 특정 이벤트를 지원하지 않으면:
            return null; // 무시 또는 예외 발생.
            throw new NotSupportedException($"The provided function \"{function.Name}\" does not supports and implements ISKFunctionHandles<{typeof(TEventArgs).Name}>");
        }
    }

    public interface ISKFunctionEventSupport<TEventArgs> where TEventArgs : SKEventArgs
    {
        Task<TEventArgs> PrepareEventArgsAsync(SKContext context, TEventArgs? eventArgs = null);
    }

    class SemanticFunction : ISKFunction,
        ISKFunctionEventSupport<FunctionInvokingEventArgs>,
        ISKFunctionEventSupport<FunctionInvokedEventArgs>
    {

        public FunctionInvokingEventArgs PrepareEventArgsAsync(SKContext context, FunctionInvokingEventArgs? eventArgs = null)
        {
            var renderedPrompt = await this.RenderPromptTemplateAsync(context);
            context.Variables.Set(SemanticFunction.RenderedPromptKey, renderedPrompt);

            return new SemanticFunctionInvokingEventArgs(this.Describe(), context);
            // 또는                                                          메타데이터 Dictionary<string, object>
            return new FunctionInvokingEventArgs(this.Describe(), context, new Dictionary<string, object>() { { RenderedPrompt, renderedPrompt } });
        }

        public FunctionInvokedEventArgs PrepareEventArgsAsync(SKContext context, FunctionInvokedEventArgs? eventArgs = null)
        {
            return Task.FromResult<FunctionInvokedEventArgs>(new SemanticFunctionInvokedEventArgs(this.Describe(), context));
        }
    }

    public sealed class SemanticFunctionInvokedEventArgs : FunctionInvokedEventArgs
    {
        public SemanticFunctionInvokedEventArgs(FunctionDescription functionDescription, SKContext context)
            : base(functionDescription, context)
        {
            _context = context;
            Metadata[RenderedPromptKey] = this._context.Variables[RenderedPromptKey];
        }

        public string? RenderedPrompt => this.Metadata[RenderedPromptKey];

    }

    public sealed class SemanticFunctionInvokingEventArgs : FunctionInvokingEventArgs
    {
        public SemanticFunctionInvokingEventArgs(FunctionDescription functionDescription, SKContext context)
            : base(functionDescription, context)
        {
            _context = context;
        }
        public string? RenderedPrompt => this._context.Variables[RenderedPromptKey];
    }
    ```

### 장단점

장점:

- `Kernel`이 `SemanticFunction` 구현 세부 사항이나 다른 `ISKFunction` 구현을 인식하지 않습니다.
- 시맨틱 함수의 프롬프트를 포함하여 사용자 정의 `ISKFunctions` 구현별 전용 EventArgs를 표시하도록 확장 가능합니다.
- `ISKFunctionEventSupport<NewEvent>` 인터페이스를 통해 Kernel에서 향후 이벤트를 지원하도록 확장 가능합니다.
- 함수는 자체 EventArgs 특화를 가질 수 있습니다.
- 인터페이스는 선택 사항이므로 사용자 정의 `ISKFunctions`가 구현 여부를 선택할 수 있습니다.

단점:

- 모든 사용자 정의 함수는 이벤트를 지원하려면 `ISKFunctionEventSupport` 인터페이스를 구현할 책임이 있습니다.
- `Kernel`은 함수가 인터페이스를 구현하는지 확인해야 하며, 구현하지 않으면 예외를 던지거나 이벤트를 무시해야 합니다.
- 한때 InvokeAsync로 제한되었던 함수 구현이 이제 여러 곳에 분산되어야 하며, 호출 시작이나 끝에서 가져와야 하는 콘텐츠와 관련된 실행 상태를 처리해야 합니다.

## 주요 질문

- Q: 사후 실행 핸들러는 LLM 결과 직후에 실행되어야 하나요, 아니면 함수 실행 자체가 끝나기 전에 실행되어야 하나요?
  A: 현재 사후 실행 핸들러는 함수 실행 후에 실행됩니다.

- Q: 사전/사후 핸들러는 여러 개(pub/sub)여서 등록/해제를 허용해야 하나요?
  A: 표준 .NET 이벤트 구현을 사용하면 호출자가 관리하는 다중 등록과 해제가 이미 지원됩니다.

- Q: 기존 핸들러 위에 핸들러를 설정하는 것이 허용되어야 하나요, 아니면 오류를 던져야 하나요?
  A: 표준 .NET 이벤트 구현을 사용하면 표준 동작은 오류를 던지지 않고 등록된 모든 핸들러를 실행합니다.

- Q: Plan에 핸들러를 설정하면 모든 내부 단계에 이 핸들러를 자동으로 전파하고 기존 핸들러를 재정의해야 하나요?
  A: 핸들러는 Kernel RunAsync 파이프라인이 작동하는 것과 동일한 방식으로 각 단계가 실행되기 전후에 트리거됩니다.

- Q: 사전 함수 실행 핸들러가 실행을 취소하려고 할 때 체인의 후속 핸들러가 호출되어야 하나요, 아니면 호출되지 않아야 하나요?
  A: 현재 표준 .NET 동작은 등록된 모든 핸들러를 호출하는 것입니다. 이렇게 하면 함수 실행은 모든 핸들러가 호출된 후의 취소 요청 최종 상태에만 의존합니다.

## 결정 결과

선택된 옵션: **3. 이벤트 기반 등록 (Kernel 전용)**

이 접근 방식이 가장 단순하며 표준 .NET 이벤트 구현의 이점을 활용합니다.

2단계에서 모든 시나리오를 완전히 지원하기 위한 추가 변경이 구현될 예정입니다.
