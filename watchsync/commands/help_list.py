from cleo.commands.list_command import ListCommand
from cleo.helpers import option


class HelpListCommand(ListCommand):
    name = "help-list"

    def configure(self) -> None:
        self._definition.add_option(
            option(
                "simple",
                "s",
                description="Show only a list with the commands",
                flag=True,
            )
        )
        super().configure()

    def handle(self):
        if self.option("simple"):
            for name in self._application.all().keys():
                self.line(name)
            return 0
        super().handle()
