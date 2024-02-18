from abc import ABC as _ABC
from typing import \
    TypeVar as _TypeVar, Generic as _Generic, Callable as _Callable, \
    MutableSequence as _MutableSequence, Iterable as _Iterable, \
    MutableMapping as _MutableMapping

_T = _TypeVar('_T')

class _IObserver(_ABC):
    pass
class _IObservable(_ABC):
    def __init__(self) -> None:
        self._observers: list[_IObserver] = []
        
    def Subscribe(self, *args, **kwargs): ...
    def Unsubscribe(self, *args, **kwargs): ...
    def UnsubscribeAll(self, *args, **kwargs): ...


class Subject(_IObservable, _Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        self._observers: list[Subject._Observer[_T]]

    class _Observer(_IObserver,_Generic[_T]):
        def __init__(
            self,
            next: _Callable[[_T], None] = None,
            error: _Callable[[Exception], None] = None,
            complete: _Callable = None,
        ):
            self.next = next
            self.error = error
            self.complete = complete


    def Subscribe(self,
            next: _Callable[[_T], None] = None,
            error: _Callable[[Exception], None] = None,
            complete: _Callable = None
        ) -> _Observer[_T]:
        """
        Subscribes to observable events in subject

        :param next: Callback on next event
            >>> lambda value: ...
        :param error: Callback on exception event
            >>> lambda exception: ...
        :param complete: Callback on complete event
            >>> lambda: ...

        :return: the subscribed observer, keep a reference to it if you wish to unsubscribe it later
        """

        observer = self._Observer(next, error, complete)
        self._observers.append(observer)
        return observer

    def Unsubscribe(self, observer: _Observer[_T]):
        self._observers.remove(observer)

    def UnsubscribeAll(self):
        self._observers.clear()

    def Next(self, value:_T):
        for observer in self._observers:
            if(observer.next is None):
                continue
            observer.next(value)

    def Error(self, ex:Exception):
        for observer in self._observers:
            if(observer.error is None):
                continue
            observer.error(ex)

    def Complete(self):
        for observer in self._observers:
            if(observer.complete is None):
                continue
            observer.complete()

class ObservableList(_IObservable, _MutableSequence[_T], _Generic[_T]):
    def __init__(self, iterable: _Iterable[_T] = []):
        super().__init__()
        self._list = list(iterable)
        self._observers: list[ObservableList._Observer[_T]]

    class _Observer(_IObserver, _Generic[_T]):
        def __init__(self,
            update: _Callable[[int, _T], None] = None,
            delete: _Callable[[int]    , None] = None,
            get   : _Callable[[int]    , None] = None,
        ):
            self.update = update
            '''
            Callback on update or insert item in collection
            >>> lambda index, newValue: ...
            '''
            self.delete = delete
            '''
            Callback on removal of item in collection
            >>> lambda index: ...
            '''
            self.get = get
            '''
            Callback on accessing of an item in collection
            >>> lambda index: ...
            '''

    def Subscribe(self,
            update: _Callable[[int, _T], None] = None,
            delete: _Callable[[int]    , None] = None,
            get   : _Callable[[int]    , None] = None,
        ) -> _Observer[_T]:
        """
        Subscribes to observable events in current collection

        :param update: Callback on update or insert item in collection
            >>> lambda index, newValue: ...
        :param delete: Callback on removal of item in collection
            >>> lambda index: ...
        :param get: Callback on accessing of an item in collection
            >>> lambda index: ...

        :return: the subscribed observer, keep a reference to it if you wish to unsubscribe it later
        """

        observer = self._Observer(update, delete, get)
        self._observers.append(observer)
        return observer
    
    def Unsubscribe(self, observer: _Observer[_T]):
        self._observers.remove(observer)

    def UnsubscribeAll(self):
        self._observers.clear()

    def __getitem__(self, index: int) -> _T:
        for observer in self._observers:
            observer.get(index)
        return self._list[index]

    def __setitem__(self, index: int, value: _T) -> None:
        for observer in self._observers:
            observer.update(index, value)
        self._list[index] = value

    def __delitem__(self, index: int) -> None:
        for observer in self._observers:
            observer.delete(index)
        del self._list[index]

    def insert(self, index: int, value: _T) -> None:
        for observer in self._observers:
            observer.update(index, value)
        self._list.insert(index, value)

    def __len__(self) -> int:
        return len(self._list)

    def __repr__(self):
        return self._list.__repr__()
    
    def __eq__(self, other):
        if isinstance(other, ObservableList):
            return self._list == other._list
        if isinstance(other, list):
            return self._list == other
        return False
    
_K = _TypeVar('_K')
_V = _TypeVar('_V')
class ObservableDict(_IObservable, _MutableMapping[_K, _V], _Generic[_K, _V]):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._dict = dict(*args, **kwargs)
        self._observers: list[ObservableDict._Observer[_K, _V]]

    class _Observer(_IObserver, _Generic[_K, _V]):
        def __init__(self,
                     update: _Callable[[_K, _V], None] = None,
                     delete: _Callable[[_K], None] = None,
                     get: _Callable[[_K], None] = None,
                     ):
            self.update = update
            '''
            Callback on update of existing item in dictionary
            >>> lambda key, newValue: ...
            '''
            self.delete = delete
            '''
            Callback on removal of item in dictionary
            >>> lambda key: ...
            '''
            self.get = get
            '''
            Callback on accessing of an item in dictionary
            >>> lambda key: ...
            '''

    def Subscribe(self,
                  update: _Callable[[_K, _V], None] = None,
                  delete: _Callable[[_K], None] = None,
                  get: _Callable[[_K], None] = None,
                  ) -> _Observer[_K, _V]:
        """
        Subscribes to observable events in the current dictionary

        :param update: Callback on update or insert item in the dictionary
            >>> lambda key, newValue: ...
        :param delete: Callback on removal of an item in the dictionary
            >>> lambda key: ...
        :param get: Callback on accessing of an item in the dictionary
            >>> lambda key: ...

        :return: the subscribed observer, keep a reference to it if you wish to unsubscribe it later
        """

        observer = self._Observer(update, delete, get)
        self._observers.append(observer)
        return observer

    def Unsubscribe(self, observer: _Observer[_K, _V]):
        self._observers.remove(observer)

    def UnsubscribeAll(self):
        self._observers.clear()

    def __getitem__(self, key: _K) -> _V:
        for observer in self._observers:
            observer.get(key)
        return self._dict[key]

    def __setitem__(self, key: _K, value: _V) -> None:
        for observer in self._observers:
            observer.update(key, value)
        self._dict[key] = value

    def __delitem__(self, key: _K) -> None:
        for observer in self._observers:
            observer.delete(key)
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return repr(self._dict)

    def __eq__(self, other):
        if isinstance(other, ObservableDict):
            return self._dict == other._dict
        if isinstance(other, dict):
            return self._dict == other
        return False