from dataclasses import asdict
from typing import TypeVar

from unimog import Context
from unimog.action import Action

In = TypeVar("In", bound=Context)
Out = TypeVar("Out", bound=Context)


class Organizer(Action[In, Out]):
    def __init__(self, *actions: Action[In, Out]):
        super().__init__(
            input_type=actions[0].input_type,
            output_type=actions[len(actions) - 1].output_type)
        self.actions = actions

    def perform(self):
        context = self.input

        for action in self.actions:
            if context.is_failure():
                raise Exception(context.error)

            context = action(**asdict(context))

        self.output = context
