from horsetalk.quantity import HorsetalkQuantity


class RaceDistance(HorsetalkQuantity):
    """
    A convenience class for representing the distance over which a race is run.

    """

    REGEX = r"(?:(\d+)(?:m)\s*)?(?:(\d+)(?:f)\s*)?(?:(\d+)(?:y)\s*)?"

    def __str__(self) -> str:
        """
        Returns the distance as a string.
        """
        return " ".join([
            f"{int(x)}m" if (x := self.to("mile").magnitude // 1) else "",
            f"{int(x)}f" if (x := self.to("f").magnitude % 8) else "",
            f"{int(x)}y" if (x := self.to("y").magnitude % 220) else "",
        ]).strip()

    @classmethod
    def _string_arg_handler(cls, parts):
        m, f, y = parts

        if int(m or 0) > 10:
            args = (int(m or 0), "metre")
        else:
            yards = int(m or 0) * 1760 + int(f or 0) * 220 + int(y or 0)
            args = (yards, "yard")

        return args
