"""Module that holds the parsing functionality."""
from itertools import product

from pydantic_core._pydantic_core import ValidationError

from janus.exceptions.exceptions import ParseJSONError
from janus.models.multiqc.models import (
    PicardInsertSize,
    SamtoolsStats,
    PicardHsMetrics,
    PicardAlignmentSummary,
    SomalierIndividual,
    SomalierComparison,
    PeddyCheck,
    PicardRNASeqMetrics,
    STARAlignment,
)

models: list = [
    PicardInsertSize,
    SamtoolsStats,
    PicardHsMetrics,
    PicardAlignmentSummary,
    SomalierIndividual,
    SomalierComparison,
    PeddyCheck,
    PicardRNASeqMetrics,
    STARAlignment,
]


def parse_json(content: list | dict):
    """
    Parse the json content into multiqc models.
         Raises: ParseJSONError in case the content cannot be parsed into a model.
    """
    parsed_content = []
    for entry, model in product(content, models):
        entry_content = content[entry]
        try:
            parsed_content.append(model.model_validate(entry_content))
        except ValidationError:
            pass
    if not parsed_content:
        raise ParseJSONError(f"Failed to parse JSON file.")
    return parsed_content
