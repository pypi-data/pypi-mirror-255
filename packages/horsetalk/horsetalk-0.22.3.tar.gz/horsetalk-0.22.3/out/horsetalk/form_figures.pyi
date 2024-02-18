from horsetalk import Disaster as Disaster, FinishingPosition as FinishingPosition, FormBreak as FormBreak
from typing import List

class FormFigures:
    @staticmethod
    def parse(form_figures: str) -> List[FinishingPosition | FormBreak | Disaster]: ...
