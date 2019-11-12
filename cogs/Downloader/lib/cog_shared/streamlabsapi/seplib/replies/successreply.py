from ..replies.embedreply import EmbedReply
from ..utils import HexColor


class SuccessReply(EmbedReply):
    """
    An EmbedReply which defaults to sending an error-styled message. Lots of red and X's.
    """

    def __init__(self, message: str):
        super(SuccessReply, self).__init__(
            message=message, color=HexColor.success(), emoji="\N{WHITE HEAVY CHECK MARK}"
        )
