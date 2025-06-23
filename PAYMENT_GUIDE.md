# 💳 AnyAgent Payment System Guide

## 🎯 How Payments Work

AnyAgent uses a **pay-per-use** model where agents request payment for specific operations.

### Key Concepts

1. **Payment Key** - Identifier for the operation type (e.g., "audio_transcription", "text_analysis")
2. **Quantity** - Number of operation units to charge for
3. **Pricing** - Cost per unit, configured in the web console

## 🔧 Configuration

### Web Console Setup
```sql
-- Example: Audio transcription costs 2 credits per minute
INSERT INTO agent_pricing (agent_name, key, credits_per_unit, description) 
VALUES ('my_agent', 'audio_transcription', 2, 'Audio transcription per minute');
```

### Agent Implementation
```python
async def execute(self, request):
    if request.telegram_message.audio:
        audio_duration_minutes = estimate_audio_duration(request.telegram_message.audio.audio_data)
        
        if not request.paid:
            yield AgentResponse(
                payment_request=UsagePaymentRequest(
                    key="audio_transcription",  # Matches web console key
                    quantity=audio_duration_minutes  # e.g., 60 for 1 hour
                )
            )
        
        # Process audio (flow continues regardless)
        result = transcribe_audio(request.telegram_message.audio)
        yield AgentResponse(telegram_message=TelegramMessage(text=TextContent(text=result)))
```

## 💰 Billing Calculation

**Total Cost = Credits Per Unit × Quantity**

### Examples

| Operation | Key | Credits/Unit | Quantity | Total Cost |
|-----------|-----|--------------|----------|------------|
| Text analysis | `text` | 5 | 1 | 5 credits |
| Audio transcription | `audio` | 2 | 60 min | 120 credits |
| Image processing | `image` | 10 | 3 images | 30 credits |
| Video analysis | `video` | 50 | 1 | 50 credits |

## 🏗️ Implementation Patterns

### Single Operation
```python
# Simple text processing - charge for 1 operation
if not request.paid:
    yield AgentResponse(
        payment_request=UsagePaymentRequest(
            key="text_analysis",
            quantity=1
        )
    )
```

### Variable Quantity
```python
# Audio processing - charge per minute
audio_minutes = calculate_duration_minutes(audio_data)
if not request.paid:
    yield AgentResponse(
        payment_request=UsagePaymentRequest(
            key="audio_transcription", 
            quantity=audio_minutes  # e.g., 45 for 45 minutes
        )
    )
```

### Batch Processing
```python
# Image batch processing - charge per image
image_count = len(request.telegram_message.images)
if not request.paid:
    yield AgentResponse(
        payment_request=UsagePaymentRequest(
            key="image_processing",
            quantity=image_count  # e.g., 10 for 10 images
        )
    )
```

## ⚡ Best Practices

1. **Always continue processing** after payment request - no `return` statements
2. **Calculate quantity accurately** - estimate before requesting payment
3. **Use descriptive keys** - make payment types clear in web console
4. **Handle edge cases** - minimum charges, free tiers, etc.

## 🔍 Common Patterns

### Free Tier with Paid Features
```python
if is_premium_feature(request) and not request.paid:
    yield AgentResponse(
        payment_request=UsagePaymentRequest(
            key="premium_analysis",
            quantity=1
        )
    )

# Basic processing is always free
result = process_request(request)
yield AgentResponse(telegram_message=TelegramMessage(text=TextContent(text=result)))
```

### Progressive Billing
```python
# Charge based on complexity
complexity = analyze_complexity(request.telegram_message.text.text)
if complexity > 1000 and not request.paid:
    yield AgentResponse(
        payment_request=UsagePaymentRequest(
            key="complex_analysis",
            quantity=math.ceil(complexity / 1000)  # Round up
        )
    )
```

This system provides flexible, transparent pricing that scales with actual usage! 🚀