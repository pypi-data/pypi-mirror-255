from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from jinja2 import Template

from mfire.settings import get_logger
from mfire.text.wind.base.reducers import BaseReducer
from mfire.text.wind.base.selectors import BaseSelector
from mfire.utils.jinja_template import JinjaTemplateCreator
from mfire.utils.string_utils import clean_french_text

# Logging
LOGGER = get_logger(name="base_builder.mod", bind="base_builder")


def add_extra_content_to_summary(summary: dict, extra_content: Any):
    """Add an extra content in a dict summary."""
    summary[BaseParamBuilder.EXTRA_KEY] = extra_content


class BaseBuilder(ABC):
    """BaseBuilder class."""

    def __init__(self):
        self.status: bool = False  # True if compute succeeded

    def _reset(self):
        self.status = False

    @abstractmethod
    def compute(
        self, summary: dict, with_extra: bool = False
    ) -> tuple[str, Optional[str]]:
        pass


class BaseParamBuilder(BaseBuilder):
    """BaseParamBuilder class.

    This class allows to build a synthesis text from a dict summary for a particular
    parameter (for example the temperature, the wind or the gust).
    """

    PARAM_NAME: str
    EXTRA_KEY: str = "extra"
    DEFAULT_OUTPUT: str = "RAS"  # Nothing to report
    ERROR_CASE: str = "error"
    SELECTOR_KEY: str = BaseSelector.KEY
    TEMPLATES_DICT: dict

    @property
    def error_template(self) -> str:
        return self.TEMPLATES_DICT[self.ERROR_CASE]

    def _get_template_key_from_selector(self, summary: dict) -> Optional[str]:
        """Get the template key from the selector key."""
        try:
            return summary.get(self.SELECTOR_KEY)
        except KeyError:
            LOGGER.error(
                f"Selector '{self.SELECTOR_KEY}' not found for "
                f"param '{self.PARAM_NAME}' !"
            )
            return None

    def _get_template_str(self, template_key: Optional[str]) -> str:
        """Get the template string from the template key."""
        try:
            template: str = self.TEMPLATES_DICT[template_key]
            self.status = True
            return template
        except KeyError:
            LOGGER.error(
                f"Template '{template_key}' not found for param '{self.PARAM_NAME}' !"
            )
            return self.error_template

    def _get_jinja_template(self, summary: dict) -> Template:
        """Get the jinja Template object from the summary by using the selector key."""
        template_key: Optional[str] = self._get_template_key_from_selector(summary)

        template_str: str
        if template_key is None:
            template_str = self.error_template
        else:
            template_str: str = self._get_template_str(template_key)

        return JinjaTemplateCreator().run(template_str)

    def compute(
        self, summary: dict, with_extra: bool = False
    ) -> tuple[str, Optional[str]]:
        """Compute the synthesis text from a dict summary."""
        self._reset()

        template: Template = self._get_jinja_template(summary)
        text: str = template.render(summary)

        # Get extra content in the text
        extra_content: Any = None
        if with_extra is True:
            if self.EXTRA_KEY not in summary:
                LOGGER.warning(f"'{self.EXTRA_KEY}' EXTRA_KEY not found in summary")
            else:
                extra_content: Any = summary.get(self.EXTRA_KEY)
                if extra_content:
                    extra_content = f"[{self.PARAM_NAME}: {extra_content}]"

        return clean_french_text(text) if text else self.DEFAULT_OUTPUT, extra_content


class BaseMultiParamsBuilder(BaseBuilder):
    """BaseMultiParamsBuilder class.

    This class allows to build a synthesis text from a dict summary for many
    parameters (for example for wind and gust). The generated text is the concatenation
    of all the param synthesis. The concatenation order is related to the order in the
    PARAM_BUILDER_CLASSES attribute list.
    """

    DEFAULT_OUTPUT: Optional[str] = None  # Set during the initialization
    ERROR_CASE: Optional[str] = None  # Set during the initialization
    PARAMS_SUMMARY_PATH: str = BaseReducer.PARAM_SUMMARIES_KEY
    PARAM_BUILDER_CLASSES: list[BaseParamBuilder] = []

    def __init__(self) -> None:
        """Initialize a BaseMultiParamsBuilder instance."""
        self.use_error_template: bool = False
        self.extra_content_list: list = []
        self.texts_list: list = []

        if self._update_builder_classes_attrs() is False:
            self.use_error_template = True

        super().__init__()

    def _add_text(self, text: str) -> None:
        """Add a text int the texts_list attribute."""
        if not text or text == self.DEFAULT_OUTPUT:
            return
        self.texts_list.append(text)

    def _reset_texts_list(self) -> None:
        """Reset the texts_list attribute."""
        self.texts_list = []

    def _reset_extra_content_list(self) -> None:
        """Reset the extra_content_list attribute."""
        self.extra_content_list = []

    def _reset(self) -> None:
        """Reset the BaseMultiParamsBuilder instance."""
        self.use_error_template = False
        self._reset_texts_list()
        self._reset_extra_content_list()

        super()._reset()

    def _set_error_template(self) -> None:
        """Set the error template in the texts_list attribute."""
        self._reset_texts_list()
        self._add_text(self.PARAM_BUILDER_CLASSES[0]().error_template)

    def _add_extra_content(self, extra_content: Optional[str]):
        """Add extra content in the extra_content_list attribute."""
        if extra_content is None:
            return
        self.extra_content_list.append(extra_content)

    def _get_param_summary(self, summary: dict, param_name: str) -> Optional[dict]:
        """Get the summary of a parameter from its name in a bigger dict summary."""
        try:
            return summary[self.PARAMS_SUMMARY_PATH][param_name]
        except KeyError:
            LOGGER.error(f"Param summary of '{param_name}' not found !")
            return None

    def _preprocessing(self, summary: dict):
        """Preprocess."""

    def _update_builder_classes_attrs(self) -> bool:
        """Get DEFAULT_OUTPUT and ERROR_CASE from PARAM_BUILDER_CLASSES."""
        for builder_class in self.PARAM_BUILDER_CLASSES:
            # Set DEFAULT_OUTPUT
            if not self.DEFAULT_OUTPUT:
                self.DEFAULT_OUTPUT = builder_class.DEFAULT_OUTPUT
            elif self.DEFAULT_OUTPUT != builder_class.DEFAULT_OUTPUT:
                LOGGER.error(
                    f"{builder_class.__class__.__name__}.DEFAULT_OUTPUT is variable: "
                    f"'{self.DEFAULT_OUTPUT}' != {builder_class.DEFAULT_OUTPUT}' !"
                )
                return False

            # Set ERROR_CASE
            if not self.ERROR_CASE:
                self.ERROR_CASE = builder_class.ERROR_CASE
            elif self.ERROR_CASE != builder_class.ERROR_CASE:
                LOGGER.error(
                    f"{builder_class.__class__.__name__}.ERROR_CASE is "
                    f"variable: '{self.ERROR_CASE}' != "
                    f"{builder_class.ERROR_CASE}' !"
                )
                return False
        return True

    def _build_synthesis_elements(self) -> tuple[str, Optional[str]]:
        """Build synthesis elements from texts_list and extra_content_list."""
        text: Optional[str] = (
            " ".join(self.texts_list) if self.texts_list else self.DEFAULT_OUTPUT
        )
        extra_content: str = (
            " ".join(self.extra_content_list) if self.extra_content_list else None
        )
        return text, extra_content

    def _build_error_synthesis(self) -> tuple[str, Optional[str]]:
        """Build synthesis with the error template and extra_content_list."""
        self._set_error_template()
        return self._build_synthesis_elements()

    def compute(
        self, summary: dict, with_extra: bool = False
    ) -> tuple[str, Optional[str]]:
        """Compute the synthesis elements from a dict summary."""
        # Reset
        self._reset()

        # Preprocess summary
        self._preprocessing(summary)

        if self.use_error_template is True:
            return self._build_error_synthesis()

        # Build synthesis text from summary
        for builder_class in self.PARAM_BUILDER_CLASSES:

            # Get parameter summary
            param_summary: Optional[dict] = self._get_param_summary(
                summary, builder_class.PARAM_NAME
            )
            if param_summary is None:
                return self._build_error_synthesis()

            # If error case, return error_synthesis
            case_value: str = param_summary.get(
                builder_class.SELECTOR_KEY, self.ERROR_CASE
            )
            if case_value == self.ERROR_CASE:
                return self._build_error_synthesis()

            builder = builder_class()
            text, extra_content = builder.compute(param_summary, with_extra)

            if builder.status is False:
                return self._build_error_synthesis()

            self._add_text(text)
            self._add_extra_content(extra_content)

        self.status = True

        return self._build_synthesis_elements()
