from __future__ import annotations

from typing import List, Optional, TypedDict

from langchain_core.language_models import BaseLLM
from nemoguardrails import RailsConfig
from nemoguardrails.actions.actions import ActionResult, action
from nemoguardrails.actions.llm.utils import llm_call
from nemoguardrails.context import llm_call_info_var
from nemoguardrails.llm.taskmanager import LLMTaskManager
from nemoguardrails.llm.types import Task
from nemoguardrails.logging.explain import LLMCallInfo
from nemoguardrails.utils import new_event_dict


class KeywordDetectionResult(TypedDict):
    is_match: bool
    text: str
    detections: List[str]


@action(is_system_action=True)
async def self_check_input(
    llm_task_manager: LLMTaskManager,
    context: Optional[dict] = None,
    llm: Optional[BaseLLM] = None,
    config: Optional[RailsConfig] = None,
    **kwargs,
):
    """Run the self check prompt without forcing max_tokens.

    Some OpenAI-compatible backends used for moderation return an empty message
    when max_tokens is constrained too aggressively, which NeMo then treats as unsafe.
    """

    user_input = (context or {}).get("user_message")
    task = Task.SELF_CHECK_INPUT

    if not user_input:
        return True

    prompt = llm_task_manager.render_task_prompt(
        task=task,
        context={"user_input": user_input},
    )
    stop = llm_task_manager.get_stop_tokens(task=task)

    llm_call_info_var.set(LLMCallInfo(task=task.value))

    response = await llm_call(
        llm,
        prompt,
        stop=stop,
        llm_params={
            "temperature": config.lowest_temperature if config else 0,
        },
    )

    if llm_task_manager.has_output_parser(task):
        result = llm_task_manager.parse_task_output(task, output=response)
    else:
        result = llm_task_manager.parse_task_output(
            task,
            output=response,
            forced_output_parser="is_content_safe",
        )

    is_safe = result[0]

    if not is_safe:
        return ActionResult(
            return_value=False,
            events=[new_event_dict("mask_prev_user_message", intent="unanswerable message")],
        )

    return True


@action(is_system_action=True)
async def detect_keywords(
    source: str,
    text: str,
    config: RailsConfig,
) -> KeywordDetectionResult:
    if source not in ("input", "output", "retrieval"):
        raise ValueError("source must be one of 'input', 'output', or 'retrieval'")

    keyword_config = getattr(config.rails.config, "keyword_detection", None)
    if keyword_config is None:
        return KeywordDetectionResult(is_match=False, text=text, detections=[])

    options = getattr(keyword_config, source, None)
    if options is None or not text:
        return KeywordDetectionResult(is_match=False, text=text, detections=[])

    keywords = getattr(options, "keywords", None) or []
    if not keywords:
        return KeywordDetectionResult(is_match=False, text=text, detections=[])

    haystack = text.lower() if getattr(options, "case_insensitive", True) else text

    matched = []
    for keyword in keywords:
        needle = keyword.lower() if getattr(options, "case_insensitive", True) else keyword
        if needle and needle in haystack:
            matched.append(keyword)

    return KeywordDetectionResult(
        is_match=bool(matched),
        text=text,
        detections=matched,
    )
