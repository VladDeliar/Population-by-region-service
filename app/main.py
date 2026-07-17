"""Command-line entrypoint: ``python -m app.main {get_data|print_data}``."""

import argparse
import asyncio

from app.config import Settings
from app.database import Database
from app.services import GetDataService, PrintDataService


class Application:
    _COMMANDS = {
        "get_data": GetDataService,
        "print_data": PrintDataService,
    }

    def __init__(self) -> None:
        self._settings = Settings()

    @classmethod
    def commands(cls) -> list[str]:
        return list(cls._COMMANDS)

    async def run(self, command: str) -> None:
        database = Database(self._settings.database_url)
        try:
            service = self._COMMANDS[command](database, self._settings)
            await service.run()
        finally:
            await database.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Countries population service")
    parser.add_argument("command", choices=Application.commands())
    arguments = parser.parse_args()
    asyncio.run(Application().run(arguments.command))


if __name__ == "__main__":
    main()
