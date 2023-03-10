import inspect
import importlib.util

module_spec = importlib.util.spec_from_file_location("inspect_test_target", "../DiagramChaseDatabase/BSSToDjango/DjangoBoilerplates/inspect_test_target.py")
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)

members = inspect.getmembers(module, inspect.isroutine)

print(members)

