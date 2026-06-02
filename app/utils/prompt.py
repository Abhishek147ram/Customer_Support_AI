from typing import Optional

PROMPT_TEMPLATE = """You are an AI customer support assistant. Use the ticket data to generate a helpful response.

Ticket details:
- Customer name: {customer_name}
- Subject: {subject}
- Description: {description}
- Predicted category: {category}
- Priority: {priority}
- Priority score: {priority_score}

Return a JSON object only, with the following keys:
1. recommended_reply: A clear and empathetic reply tailored to the customer.
2. confidence_score: A float between 0.0 and 1.0 indicating how confident you are in the suggested response.
3. escalation_recommendation: "yes" or "no".
4. escalation_reason: A brief reason if escalation is recommended, otherwise an empty string.
5. follow_up_actions: A short list of actionable next steps.

Do not include any additional commentary outside the JSON object. Ensure the JSON is valid.
"""


def build_ticket_reply_prompt(
    customer_name: str,
    subject: str,
    description: str,
    category: str,
    priority: str,
    priority_score: float,
    escalation_threshold: Optional[float] = None,
) -> str:
    prompt = PROMPT_TEMPLATE.format(
        customer_name=customer_name,
        subject=subject,
        description=description,
        category=category,
        priority=priority,
        priority_score=round(priority_score, 2),
    )

    if escalation_threshold is not None:
        prompt += (
            f"\n\nIf the ticket priority score is above {escalation_threshold}, recommend escalation with a clear reason."
        )

    return prompt
