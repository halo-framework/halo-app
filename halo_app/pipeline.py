from __future__ import annotations

from abc import ABCMeta, abstractmethod

from halo_app.classes import AbsBaseClass



class IInput(AbsBaseClass,metaclass=ABCMeta):
    pass

class IOutput(AbsBaseClass,metaclass=ABCMeta):
    pass


class IHandler(AbsBaseClass,metaclass=ABCMeta):
    """The Interface for handling requests."""

    @abstractmethod
    def process(self,input:IInput)->IOutput:
        """Handle the event"""


class Pipeline(AbsBaseClass):

  currentHandler:IHandler = None

  def __init__(self,currentHandler:IHandler):
    self.currentHandler = currentHandler

  def __do_execute(self,input:IInput)->IOutput:
    return self.currentHandler.process(self.oldPipeline.execute(input))

  def addHandler(self,newHandler:IHandler)->Pipeline:
    p = Pipeline(newHandler)
    p.oldPipeline = self
    p.execute = p.__do_execute
    return  p

  def execute(self,input:IInput)->IOutput:
    return self.currentHandler.process(input)

def main():
    class Handler1(IHandler):
        def process(self, input: IInput) -> IOutput:
            print("H1")
            return True
    class Handler2(IHandler):
        def process(self, input: IInput) -> IOutput:
            print("H2")
            return True
    class Handler3(IHandler):
        def process(self, input: IInput) -> IOutput:
            print("H3")
            return True

    filters = Pipeline(Handler1()).addHandler(Handler2()).addHandler(Handler3())
    filters.execute("Go123!");

if __name__ == '__main__':
    main()