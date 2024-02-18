##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.806113                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing

class MulticoreException(Exception, metaclass=type):
    ...

def parallel_imap_unordered(func: typing.Callable[[typing.Any], typing.Any], iterable: typing.Iterable[typing.Any], max_parallel: typing.Optional[int] = None, dir: typing.Optional[str] = None) -> typing.Iterator[typing.Any]:
    """
    Parallelizes execution of a function using multiprocessing. The result
    order is not guaranteed.
    
    Parameters
    ----------
    func : Callable[[Any], Any]
        Function taking a single argument and returning a result
    iterable : Iterable[Any]
        Iterable over arguments to pass to fun
    max_parallel int, optional, default None
        Maximum parallelism. If not specified, uses the number of CPUs
    dir : str, optional, default None
        If specified, directory where temporary files are created
    
    Yields
    ------
    Any
        One result from calling func on one argument
    """
    ...

def parallel_map(func: typing.Callable[[typing.Any], typing.Any], iterable: typing.Iterable[typing.Any], max_parallel: typing.Optional[int] = None, dir: typing.Optional[str] = None) -> typing.List[typing.Any]:
    """
    Parallelizes execution of a function using multiprocessing. The result
    order is that of the arguments in `iterable`
    
    Parameters
    ----------
    func : Callable[[Any], Any]
        Function taking a single argument and returning a result
    iterable : Iterable[Any]
        Iterable over arguments to pass to fun
    max_parallel int, optional, default None
        Maximum parallelism. If not specified, uses the number of CPUs
    dir : str, optional, default None
        If specified, directory where temporary files are created
    
    Returns
    -------
    List[Any]
        Results. The items in the list are in the same order as the items
        in `iterable`.
    """
    ...

