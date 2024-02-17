"""
Convenience decorators for use in fabfiles.
"""

from fabric.api import runs_once as _runs_once

from burlap.tasks import WrappedCallableTask


def task_or_dryrun(*args, **kwargs):
    """
    Decorator declaring the wrapped function to be a new-style task.

    May be invoked as a simple, argument-less decorator (i.e. ``@task``) or
    with arguments customizing its behavior (e.g. ``@task(alias='myalias')``).

    Please see the :ref:`new-style task <task-decorator>` documentation for
    details on how to use this decorator.

    .. versionchanged:: 1.2
        Added the ``alias``, ``aliases``, ``task_class`` and ``default``
        keyword arguments. See :ref:`task-decorator-arguments` for details.
    .. versionchanged:: 1.5
        Added the ``name`` keyword argument.

    .. seealso:: `~fabric.docs.unwrap_tasks`, `~fabric.tasks.WrappedCallableTask`
    """
    invoked = bool(not args or kwargs)
    task_class = kwargs.pop("task_class", WrappedCallableTask)
    func, args = args[0], ()

    def wrapper(func):
        return task_class(func, *args, **kwargs)

    wrapper.is_task_or_dryrun = True
    wrapper.wrapped = func

    return wrapper if invoked else wrapper(func)


_METHOD_ATTRIBUTES = ['deploy_before', 'is_post_callback', 'is_task']


def kwargs_to_bool(kwargs, bools):
    """
    Converts all attributes beginning with "do_", or names in the bools list, to a boolean value.

    Note, assumes boolean values are 1|0, as entered from a console as flags. This is not a direct wrapper around bool().

    Arguments:

        kwargs := {name1:value1, ...}

        bools := {name1, name2, ...}
    """
    bools = bools or set()
    for k, v in kwargs.items():
        if k.startswith('do_') or k in bools:
            try:
                kwargs[k] = bool(int(v))
            except ValueError as exc:
                raise Exception(f'Unable to convert argument {k} with value "{v}" to a boolean.') from exc
    return kwargs


def _task(meth, bools):
    meth.is_task = True

    def wrapper(self, *args, **kwargs):
        kwargs_to_bool(kwargs, bools)
        ret = meth(self, *args, **kwargs)

        # Ensure each satchels local variable scope is cleared after every server execution.
        if hasattr(meth, 'is_deployer') or meth.__name__ == 'configure':
            self.clear_local_renderer()

        return ret

    # Auto-collect booleans from optional type annotations.
    if meth.__annotations__:
        bools.update({k for k, v in meth.__annotations__.items() if v is bool})

    # Copy the wrapped method's attributes to the wrapper so it's accessible from Fabric the same as the original method.
    wrapper.__name__ = meth.__name__
    for attr in _METHOD_ATTRIBUTES:
        if hasattr(meth, attr):
            setattr(wrapper, attr, getattr(meth, attr))

    return wrapper


def task(*args, **kwargs):
    """
    Decorator for registering a satchel method as a Fabric task.

    Can be used like:

        @task
        def my_method(self):
            ...

        @task(precursors=['other_satchel'])
        def my_method(self):
            ...

    Arguments:

        precursors :=  List of other tasks to run before this one.

        post_callback := True|False, If true, marks this as a function
            to always be called during Burlap initialization.

        bools := List of boolean argument names to auto-convert to boolean.
            Will be auto-detected from type hints.

    """
    precursors = kwargs.pop('precursors', None)
    post_callback = kwargs.pop('post_callback', False)
    bools = set(kwargs.pop('bools', []))
    if args and callable(args[0]):
        # direct decoration, @task
        return _task(*args, bools)

    deploy_before = list(precursors or [])

    # callable decoration, @task(precursors=['satchel'])
    def wrapper(meth):
        if precursors:
            meth.deploy_before = deploy_before
        if post_callback:
            meth.is_post_callback = True
        return _task(meth, bools)

    wrapper.deploy_before = deploy_before
    return wrapper


def runs_once(meth):
    """
    A wrapper around Fabric's runs_once() to support our dryrun feature.
    """
    from burlap.common import get_dryrun, runs_once_methods
    if get_dryrun():
        pass
    else:
        runs_once_methods.append(meth)
        _runs_once(meth)
    return meth
