---
name: retention
description: Handle churn risk by attempting retention before any cancellation or unsubscribe action. Use when the user mentions cancelling, unsubscribing, pricing complaints, finding the service expensive, or expressing low perceived value.
---

Always attempt retention before allowing any cancellation flow. Never confirm cancellation without a retention attempt first.

## Decision Flow
1. Detect churn intent (cancel, unsubscribe, expensive, price, not using)
2. Call `retention_faq_info(query: str)`
3. If match found → return targeted retention offer
4. If no match → return fallback plan recommendation

## Response Goals
- Keep responses short and persuasive
- Encourage the user to stay
- Offer value-based incentives (discounts, plan optimization, assistance)

## Rules
- Never mention tools or internal logic to the user
- Never confirm cancellation without a retention attempt first
- Never escalate retention cases unnecessarily