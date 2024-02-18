import traceback
from importlib import import_module

from kassautomate.app.Console import console


class Job:

    def __init__(self, controller, *args, **kwarg) -> None:

        module = import_module(f"app.controllers.{controller}")
        controllerName = (
            controller if "." not in controller else controller.rsplit(".", 1)[-1]
        )
        self.controller = getattr(module, controllerName)

    def run(self, *args, **kwarg):
        try:
            return self.controller().run(*args, **kwarg)
        except Exception as err:
            error_type = type(err).__name__
            error_traceback = traceback.format_exc()

            console().blankrow()
            console(f"[Controller: {self.controller}]").info()
            console(f"[{error_type}: {str(err)}]").warn()
            console(f"Traceback:\n {error_traceback}").danger().save(
                title="Class Job() Error"
            )
            console().blankrow()
            return
