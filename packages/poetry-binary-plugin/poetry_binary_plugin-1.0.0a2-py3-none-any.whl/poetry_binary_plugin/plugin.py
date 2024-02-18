from cleo.events.console_events import COMMAND
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.event_dispatcher import EventDispatcher
from poetry.console.application import Application
from poetry.console.commands.env_command import EnvCommand
from poetry.console.commands.build import BuildCommand
from poetry.plugins.application_plugin import ApplicationPlugin


class MyApplicationPlugin(ApplicationPlugin):
    def activate(self, application: Application):
        application.event_dispatcher.add_listener(
            COMMAND, self.handler
        )

    def handler(
        self,
        event: ConsoleCommandEvent,
        event_name: str,
        dispatcher: EventDispatcher
    ) -> None:
        command = event.command
        if not isinstance(command, BuildCommand):
            return

        io = event.io

        if io.is_debug():
            io.write_line(
                "<debug>Loading environment variables.</debug>"
            )

        io.write_line('ATTACH TO BUILD')
