from decimal import Decimal


class User:
    def __init__(
            self,
            uid: int,
            chat_id: int,
            action: str | None = None,
            active: int | None = None
    ):
        self.uid = uid
        self.chat_id = chat_id
        self.action = action
        self.active = active
