from mfire.settings import TEMPLATES_FILENAMES, get_logger
from mfire.text.base import BaseBuilder, BaseSelector
from mfire.text.template import TemplateRetriever, read_template
from mfire.utils.string_utils import clean_french_text

# Logging
LOGGER = get_logger(name="base_selector.mod", bind="base_selector")


class TemplateBuilder(BaseBuilder):
    """TemplateBuilder qui doit renvoyer une clé de template"""

    template_name: str = ""
    selector_class: BaseSelector = BaseSelector

    def find_template_key(self, selector: BaseSelector) -> str:
        return selector.compute(self.reduction)

    def retrieve_template(
        self, key: str, template_retriever: TemplateRetriever
    ) -> None:
        """retrieve_template: method that triggers the self.template_retriever
        according to the reducer features.
        """

        default = f"Echec dans la récupération du template (key={key})(error COM-001)."

        self._text = template_retriever.get(
            key=key,
            default=default,
        )

    def compute(self, reduction: dict) -> None:
        super().compute(reduction)
        key = self.find_template_key(self.selector_class())
        TEMPE_TPL_RETRIEVER = read_template(
            TEMPLATES_FILENAMES["fr"]["synthesis"][self.template_name]
        )
        self.retrieve_template(key, TEMPE_TPL_RETRIEVER)

        self._text = clean_french_text(self._text.format(**reduction))
        LOGGER.info(self._text)
