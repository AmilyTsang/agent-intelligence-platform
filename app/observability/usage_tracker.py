from __future__ import annotations

from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class TokenUsageCallbackHandler(BaseCallbackHandler):
    """
    Collect token usage for one complete LangGraph research run.

    Supports common LangChain / OpenAI-compatible response formats:

    - AIMessage.usage_metadata
    - AIMessage.response_metadata["token_usage"]
    - LLMResult.llm_output["token_usage"]

    One instance should be created for each research request.
    """

    def __init__(self) -> None:
        super().__init__()

        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0
        self.llm_calls = 0

    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any,
    ) -> None:
        """
        Called whenever one LLM invocation finishes.
        """

        self.llm_calls += 1

        usage_found = False

        # ------------------------------------------------------
        # 1. Try AIMessage usage metadata first
        # ------------------------------------------------------

        generations = getattr(
            response,
            "generations",
            None,
        ) or []

        for generation_group in generations:
            for generation in generation_group:
                message = getattr(
                    generation,
                    "message",
                    None,
                )

                if message is None:
                    continue

                # ----------------------------------------------
                # LangChain standardized usage_metadata
                # ----------------------------------------------

                usage_metadata = getattr(
                    message,
                    "usage_metadata",
                    None,
                )

                parsed = self._parse_usage(
                    usage_metadata
                )

                if parsed is not None:
                    self._add_usage(
                        parsed
                    )

                    usage_found = True

                    continue

                # ----------------------------------------------
                # Provider response metadata
                # ----------------------------------------------

                response_metadata = getattr(
                    message,
                    "response_metadata",
                    None,
                ) or {}

                token_usage = (
                    response_metadata.get(
                        "token_usage"
                    )
                    or response_metadata.get(
                        "usage"
                    )
                )

                parsed = self._parse_usage(
                    token_usage
                )

                if parsed is not None:
                    self._add_usage(
                        parsed
                    )

                    usage_found = True

        # ------------------------------------------------------
        # 2. Fallback to LLMResult.llm_output
        # ------------------------------------------------------

        if usage_found:
            return

        llm_output = getattr(
            response,
            "llm_output",
            None,
        ) or {}

        token_usage = (
            llm_output.get(
                "token_usage"
            )
            or llm_output.get(
                "usage"
            )
        )

        parsed = self._parse_usage(
            token_usage
        )

        if parsed is not None:
            self._add_usage(
                parsed
            )

    @staticmethod
    def _parse_usage(
        usage: Any,
    ) -> dict[str, int] | None:
        if not usage:
            return None

        if not isinstance(
            usage,
            dict,
        ):
            try:
                usage = dict(
                    usage
                )
            except Exception:
                return None

        # LangChain standardized names
        input_tokens = usage.get(
            "input_tokens"
        )

        output_tokens = usage.get(
            "output_tokens"
        )

        total_tokens = usage.get(
            "total_tokens"
        )

        # OpenAI-compatible names
        if input_tokens is None:
            input_tokens = usage.get(
                "prompt_tokens",
                0,
            )

        if output_tokens is None:
            output_tokens = usage.get(
                "completion_tokens",
                0,
            )

        input_tokens = int(
            input_tokens or 0
        )

        output_tokens = int(
            output_tokens or 0
        )

        if total_tokens is None:
            total_tokens = (
                input_tokens
                + output_tokens
            )

        total_tokens = int(
            total_tokens or 0
        )

        if (
            input_tokens == 0
            and output_tokens == 0
            and total_tokens == 0
        ):
            return None

        return {
            "input_tokens":
                input_tokens,

            "output_tokens":
                output_tokens,

            "total_tokens":
                total_tokens,
        }

    def _add_usage(
        self,
        usage: dict[str, int],
    ) -> None:
        self.input_tokens += (
            usage.get(
                "input_tokens",
                0,
            )
        )

        self.output_tokens += (
            usage.get(
                "output_tokens",
                0,
            )
        )

        self.total_tokens += (
            usage.get(
                "total_tokens",
                0,
            )
        )

    def to_dict(
        self,
    ) -> dict[str, int]:
        return {
            "input_tokens":
                self.input_tokens,

            "output_tokens":
                self.output_tokens,

            "total_tokens":
                self.total_tokens,

            "llm_calls":
                self.llm_calls,
        }