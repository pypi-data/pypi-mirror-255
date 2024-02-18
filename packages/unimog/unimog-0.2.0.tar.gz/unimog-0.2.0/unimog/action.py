from abc import abstractmethod

from typing import Generic, NoReturn, TypeVar, Type
from unimog.context import Context

In = TypeVar("In", bound=Context)
Out = TypeVar("Out", bound=Context)


class Action(Generic[In, Out]):
    def __init__(self,
                 input_type: Type[In] = Context,
                 output_type: Type[Out] = Context):
        self.input = None
        self.input_type = input_type

        self.output = None
        self.output_type = output_type

    def __call__(self, **kwargs) -> Out:
        self.input = self.input_type(**kwargs)
        self.output = self.output_type(**kwargs)

        try:
            self.perform()
            return self.output.success()  # noqa
        except Exception as e:
            return self.output.failure(str(e))

    @abstractmethod
    def perform(self) -> NoReturn:
        pass
