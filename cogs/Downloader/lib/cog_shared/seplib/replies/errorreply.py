from ..replies.embedreply import EmbedReply
from ..utils import HexColor


class ErrorReply(EmbedReply):
    """
    An EmbedReply which defaults to sending an error-styled message. Lots of red and X's.
    """

    def __init__(self, message: str):
        super(ErrorReply, self).__init__(message=message, color=HexColor.error(), emoji="\N{CROSS MARK}")
