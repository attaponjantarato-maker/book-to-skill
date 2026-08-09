from enum import Enum


class PolicyMode(str, Enum):
    """How strongly medical use-policy findings affect agent execution.

    ADVISORY is intended for personal research, learning, and experimentation.
    Policy findings are returned as warnings but do not block use.

    STRICT is available for workflows that want operational guardrails.
    The same findings are promoted to errors and can block a decision.
    """

    ADVISORY = "advisory"
    STRICT = "strict"
