from datetime import datetime as dt

# from app.database.models.Log import Log


class console:

    def __init__(self, content: any = "") -> None:

        self.content = content

    @staticmethod
    def blankrow():
        print("\n")

    def withTime(self):
        self.content = (
            str(dt.strftime(dt.now(), "%Y-%m-%d %H:%M:%S")) + " | " + self.content
        )
        return self

    def list(self, items: list[str]):
        self.info()
        for item in items:
            self.content = "  \u2022" + item
            self.log()

    def log(self):
        print(self.__color(), self.content, self.__color())
        return self

    def info(self):
        print(self.__color("cyan"), self.content, self.__color())
        return self

    def success(self):
        print(self.__color("green"), self.content, self.__color())
        return self

    def danger(self):
        print(self.__color("red"), self.content, self.__color())
        return self

    def warn(self):
        print(self.__color("yellow"), self.content, self.__color())
        return self

    def __color(self, code: str = "") -> str:
        """Cores para usar no terminal"""

        if code == "green":
            return "\033[0;32m"

        elif code == "yellow":
            return "\033[0;33m"

        elif code == "red":
            return "\033[0;31m"

        elif code == "cyan":
            return "\033[0;36m"

        else:
            return "\033[m"

    def save(self, title: str):

        content = self.content.split("|")[1] if "|" in self.content else self.content

        # Log().insert({"title": title, "log": content})

    def discord(self):
        pass
