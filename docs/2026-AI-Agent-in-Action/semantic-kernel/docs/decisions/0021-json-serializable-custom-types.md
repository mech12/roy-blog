---
status: proposed
contact: dehoward
date: 2023-11-06
deciders: alliscode, markwallace-microsoft
consulted:
informed:
---

# JSON 직렬화 가능한 사용자 정의 타입

## 맥락 및 문제 설명

이 ADR은 `System.Text.Json`을 사용하여 직렬화할 수 있는 모든 타입을 개발자가 사용할 수 있도록 하여 사용자 정의 타입의 사용을 단순화하는 것을 목표로 합니다.

JSON 직렬화 가능 타입으로 표준화하는 것은 플래너의 함수 매뉴얼 내에서 JSON 스키마를 사용하여 함수를 설명할 수 있도록 하기 위해 필요합니다. JSON 스키마를 사용하여 함수의 입력 및 출력 타입을 설명하면 플래너가 함수가 올바르게 사용되고 있는지 검증할 수 있습니다.

현재 Semantic Kernel 내에서 사용자 정의 타입을 사용하려면 개발자가 타입의 문자열 표현으로의 변환/역변환을 위한 사용자 정의 `TypeConverter`를 구현해야 합니다. 이는 아래와 같이 [Functions/MethodFunctions_Advanced]에서 시연됩니다:

```csharp
    [TypeConverter(typeof(MyCustomTypeConverter))]
    private sealed class MyCustomType
    {
        public int Number { get; set; }

        public string? Text { get; set; }
    }

    private sealed class MyCustomTypeConverter : TypeConverter
    {
        public override bool CanConvertFrom(ITypeDescriptorContext? context, Type sourceType) => true;

        public override object? ConvertFrom(ITypeDescriptorContext? context, CultureInfo? culture, object value)
        {
            return JsonSerializer.Deserialize<MyCustomType>((string)value);
        }

        public override object? ConvertTo(ITypeDescriptorContext? context, CultureInfo? culture, object? value, Type destinationType)
        {
            return JsonSerializer.Serialize(value);
        }
    }
```

위 접근 방식은 이제 사용자 정의 타입이 `System.Text.Json`을 사용하여 직렬화할 수 없는 경우에만 필요합니다.

## 검토한 옵션

**1. 주어진 타입에 대한 `TypeConverter`를 사용할 수 없는 경우 `System.Text.Json`을 사용한 직렬화로 폴백**

- 기본 타입은 네이티브 `TypeConverter`를 사용하여 처리됩니다
  - 손실 변환을 방지하기 위해 기본 타입에 대해서는 네이티브 `TypeConverter` 사용을 유지합니다.
- 복합 타입은 등록된 `TypeConverter`가 있는 경우 해당 `TypeConverter`로 처리됩니다.
- 복합 타입에 대해 `TypeConverter`가 등록되지 않은 경우, 자체 `JsonSerializationTypeConverter`가 `System.Text.Json`을 사용하여 JSON 직렬화/역직렬화를 시도합니다.
  - 타입을 직렬화/역직렬화할 수 없는 경우 상세한 오류 메시지가 발생합니다.

이렇게 하면 `NativeFunction.cs`의 `GetTypeConverter()` 메서드가 다음과 같이 변경됩니다. 이전에는 타입에 대한 `TypeConverter`를 찾지 못하면 `null`을 반환했습니다:

```csharp
private static TypeConverter GetTypeConverter(Type targetType)
    {
        if (targetType == typeof(byte)) { return new ByteConverter(); }
        if (targetType == typeof(sbyte)) { return new SByteConverter(); }
        if (targetType == typeof(bool)) { return new BooleanConverter(); }
        if (targetType == typeof(ushort)) { return new UInt16Converter(); }
        if (targetType == typeof(short)) { return new Int16Converter(); }
        if (targetType == typeof(char)) { return new CharConverter(); }
        if (targetType == typeof(uint)) { return new UInt32Converter(); }
        if (targetType == typeof(int)) { return new Int32Converter(); }
        if (targetType == typeof(ulong)) { return new UInt64Converter(); }
        if (targetType == typeof(long)) { return new Int64Converter(); }
        if (targetType == typeof(float)) { return new SingleConverter(); }
        if (targetType == typeof(double)) { return new DoubleConverter(); }
        if (targetType == typeof(decimal)) { return new DecimalConverter(); }
        if (targetType == typeof(TimeSpan)) { return new TimeSpanConverter(); }
        if (targetType == typeof(DateTime)) { return new DateTimeConverter(); }
        if (targetType == typeof(DateTimeOffset)) { return new DateTimeOffsetConverter(); }
        if (targetType == typeof(Uri)) { return new UriTypeConverter(); }
        if (targetType == typeof(Guid)) { return new GuidConverter(); }

        if (targetType.GetCustomAttribute<TypeConverterAttribute>() is TypeConverterAttribute tca &&
            Type.GetType(tca.ConverterTypeName, throwOnError: false) is Type converterType &&
            Activator.CreateInstance(converterType) is TypeConverter converter)
        {
            return converter;
        }

        // 이제 null 대신 기본적으로 JSON 직렬화 TypeConverter를 반환합니다
        return new JsonSerializationTypeConverter();
    }

    private sealed class JsonSerializationTypeConverter : TypeConverter
    {
        public override bool CanConvertFrom(ITypeDescriptorContext? context, Type sourceType) => true;

        public override object? ConvertFrom(ITypeDescriptorContext? context, CultureInfo? culture, object value)
        {
            return JsonSerializer.Deserialize<object>((string)value);
        }

        public override object? ConvertTo(ITypeDescriptorContext? context, CultureInfo? culture, object? value, Type destinationType)
        {
            return JsonSerializer.Serialize(value);
        }
    }

```

_직렬화/역직렬화가 필요한 경우는?_

필요함

- **Native에서 Semantic으로:** Native에서 Semantic으로 변수를 전달하면 Native Function의 출력을 복합 타입에서 문자열로 직렬화하여 LLM에 전달할 수 있도록 **해야 합니다**.
- **Semantic에서 Native로:** Semantic에서 Native로 변수를 전달하면 Semantic Function의 출력을 문자열에서 Native Function이 기대하는 복합 타입 형식으로 역직렬화**해야 합니다**.

필요하지 않음

- **Native에서 Native로:** Native에서 Native로 변수를 전달하면 복합 타입을 그대로 전달할 수 있으므로 직렬화나 역직렬화가 **필요하지 않습니다**.
- **Semantic에서 Semantic으로:** Semantic에서 Semantic으로 변수를 전달하면 복합 타입이 문자열 표현으로 전달되므로 직렬화나 역직렬화가 **필요하지 않습니다**.

**2. 네이티브 직렬화 메서드만 사용**
이 옵션은 원래 고려되었으며, `TypeConverter` 사용을 효과적으로 제거하고 간단한 `JsonConverter`로 대체하는 것이었지만, 기본 타입 간 손실 변환이 발생할 수 있다는 지적이 있었습니다. 예를 들어 `float`에서 `int`로 변환할 때, 네이티브 직렬화 메서드에 의해 정확한 결과를 제공하지 않는 방식으로 기본 값이 잘릴 수 있습니다.

## 결정 결과
