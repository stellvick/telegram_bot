from classes.os import Os


class User:
    def __init__(
            self,
            uid: int,
            chat_id: int,
            action: str | None = None,
            active: int | None = None,
            os: Os | None = None,
    ):
        self.uid = uid
        self.chat_id = chat_id
        self.action = action
        self.active = active
        self.os = os
