from collections.abc import Iterator
from typing import Callable, Iterable, TypeVar, Any
from itertools import islice

_T = TypeVar('_T')
_K = TypeVar('_K')

class LINQ(Iterator[_T]):
    """
    A LINQ-inspired wrapper class for Python iterators.
    This class provides LINQ-like functionality for iterating over collections in a concise and expressive manner.
    """
    def __init__(self, iterable: Iterable[_T]):
        """ :param iterable: The iterable to be wrapped. """
        self._collection = iterable #the collection that is an iterable
        self._iterator = iter(self._collection) #iterator/generator
    
    def Select(self, selector: Callable[[_T], _K]):
        """
        Transforms each element of an iterable into a new form with the return values of selector.
        
        :param selector: The function to apply to each item in the collection.
        """
        return LINQ(map(selector, self))
   
    def Where(self, predicate: Callable[[_T], bool]):
        """
        Returns an iterable containing only items that satisfy the given predicate.

        :param predicate: The predicate function used to filter the items.
        """
        return LINQ(filter(predicate, self))
   
    def First(self, predicate: Callable[[_T], bool] = None) -> _T:
        """
        Returns the first item in the iterable that satisfies the given predicate.
        If no predicate is provided, returns the first item in the iterable.
        """
        if(predicate is None):
            return next(iter(self))
        for item in self:
            if predicate(item):
                return item
        raise ValueError("No item satisfies the given predicate")
    
    def FirstOrDefault(self, predicate: Callable[[_T], bool] = None) -> _T:
        try:
            return self.First(predicate=predicate)
        except (ValueError, StopIteration):
            return None
   
    def Last(self, predicate: Callable[[_T], bool] = None) -> _T:
        """
        Returns the last item in the iterable that satisfies the given predicate.
        If no predicate is provided, returns the last item in the iterable.
        """
        if hasattr(self._collection, "__reversed__"):
            # If the iterable supports __reversed__(), use reversed()
            for item in reversed(self._collection):
                if predicate is None or predicate(item):
                    return item
            raise ValueError("No item satisfies the given predicate.")
        
        # If the iterable does not support __reversed__(), iterate over all items
        # in forward order and keep track of the last item that satisfies the predicate
        last_item = None
        for item in self:
            if predicate is None or predicate(item):
                last_item = item
        if last_item is not None:
            return last_item
        # Raise an exception if no item satisfies the predicate
        raise ValueError("No item satisfies the given predicate.")
   
    def LastOrDefault(self, predicate: Callable[[_T], bool] = None) -> _T:
        try:
            return self.Last(predicate=predicate)
        except (ValueError, StopIteration):
            return None

    def ElementAt(self, index:int) -> _T:
        return next(islice(self._collection, index, index + 1))

    def ElementAtOrDefault(self, index:int) -> _T:
        try:
            return self.ElementAt(index)
        except (ValueError, StopIteration):
            return None
    
    def IsEmpty(self):
        """
        Determines if the iterable is empty.

        :return: True if the iterable is empty, False otherwise.
        """
        try:
            # Try to advance the iterator and check if it raises a StopIteration exception
            next(self._iterator)
            return False
        except StopIteration:
            return True
   
    def Skip(self, count: int):
        """
        Bypasses a specified number of elements in the iterable and returns the remaining elements.

        :param count: The number of elements to skip.
        """
        return LINQ(islice(self, count, None))
   
    def Take(self, count: int):
        """
        Returns a specified number of contiguous elements from the iterable.

        :param count: The number of elements to take.
        """
        return LINQ(islice(self, count))
   
    def All(self, predicate: Callable[[_T], bool]|_T) -> bool:
        """    
        Determines whether all elements of the iterable satisfy a given condition.

        :param predicate: A condition function or a value to compare the elements against
        """
        if(not callable(predicate)):
            value = predicate
            predicate = lambda x: x == value
        
        return all(predicate(item) for item in self)
   
    def Any(self, predicate: Callable[[_T], bool]|_T = None) -> bool:
        """    
        Determines whether any element of iterable satisfies a given condition.

        :param predicate: A condition function or a value to compare the elements against
        """
        if(predicate is None):
            return (self.IsEmpty() == False)
        if(not callable(predicate)):
            value = predicate
            predicate = lambda x: x == value

        return any(predicate(item) for item in self)
   
    def Distinct(self, predicate: Callable[[_T], Any]=None):
        """
        Returns an iterable of distinct elements based on the given condition.

        :param predicate: A function to extract a key from each element for comparison.
                        If not provided, the default is to use the elements themselves.
        """
        if(predicate is None):
            return LINQ(set(self))
        seen = set()
        result = []
        for item in self:
            key = predicate(item)
            if key not in seen:
                seen.add(key)
                result.append(item)
        return LINQ(result)
   
    def OrderBy(self, predicate: Callable[[_T], Any], descending: bool = False):
        """
        Returns a new iterable sorted by the given key function.

        :param predicate: A function to extract a key from each element for sorting.
        :param descending: If True, sorts the elements in descending order. Default is False.
        """
        return LINQ(sorted(self, key=predicate, reverse=descending))
   
    def GroupBy(self, key_selector: Callable[[_T], _K]) -> dict[_K, list[_T]]:
        """
        Groups the elements of the iterable based on the given key selector function.

        :param key_selector: A function to extract a key from each element for grouping.
        :return: A dictionary where the keys are the group keys and the values are lists of elements in each group.
        """

        from collections import defaultdict

        groups = defaultdict(list)
        for item in self:
            key = key_selector(item)
            groups[key].append(item)
        return dict(groups)
   
    def Aggregate(self, func: Callable[[_T, _T], _T], seed: _T = None) -> _T:
        """
        Applies an accumulator function to the iterable and returns the final result.
        :param func: The accumulator function to apply to the iterable.
        :param seed: The optional seed value for the accumulator. If not provided, the first element of the iterable is used as the seed.
        :return: The final result of the aggregation.
        """
        
        # Iterate over the iterable and apply the accumulator function to each element
        for i, item in enumerate(self):
            # If seed is not provided, use the first element of the iterable as the initial accumulator value
            if(i == 0 and seed is None): 
                seed = item
                continue
            seed = func(seed, item)

        # Return the final accumulator value
        return seed
   
    def Intersect(self, other: Iterable[_T]):
        """
        Returns an iterable containing elements that are present in both the current iterable and the other iterable.

        :param other: The other iterable to intersect with.

        Example Usage:
        
        >>> LINQ([1,2,3]).Intersect([2,3,4]).ToList()
        [2, 3]
        """

        other_set = set(item for item in other)
        return LINQ(item for item in self if item in other_set)

    def Union(self, other: Iterable[_T]):
        """
        Returns an iterable containing the elements that appear in either this iterable or another iterable,
        excluding duplicates.

        :param other: The other iterable to combine with this iterable.

        Example Usage:
        
        >>> LINQ([1,2,3]).Union([2,3,4]).ToList()
        [1,2,3,4]
        """
        return LINQ(set().union(self, other))
    
    def Except(self, other: Iterable[_T]):
        """
        Returns an iterable containing the elements from the current iterable
        that do not appear in the other iterable.

        :param other: The other iterable to compare with.

        Example Usage:

        >>> LINQ([1, 2, 3, 4, 5]).Except([3, 4]).ToList()
        [1, 2, 5]
        """
        other_set = set(item for item in other)
        return LINQ(item for item in self if item not in other_set)

    def Min(self, predicate: Callable[[_T], Any] = None):
        return min(self, key=predicate)
   
    def Max(self, predicate: Callable[[_T], Any] = None):
        return max(self, key=predicate)

    def Sum(self, selector: Callable[[_T], float] = None) -> float:
        """
        Computes the sum of the items in the collection.
        If a selector function is provided, it is used to select a numeric value for each item before summing.

        :param selector: An optional selector function to select a numeric value for each item
        :return: The sum of the items in the collection.

        Example usage:

        >>> LINQ([1,2,3]).Sum()
        6.0
        """
    
        if selector is None:
            return sum(self)
        return sum(selector(item) for item in self._collection)
    
    def Average(self, selector: Callable[[_T], float] = None) -> float:
        """
        Computes the average of the items in the collection.
        If a selector function is provided, it is used to select a numeric value for each item before averaging.

        :param selector: An optional selector function to select a numeric value for each item
        :return: The average of the items in the collection.

        Example usage:

        >>> LINQ([1,2,3]).Sum()
        2.0
        """

        return self.Sum(selector=selector) / self.Count()
    
    def Count(self, predicate: Callable[[_T], bool] = None) -> int:
        """
        Returns the number of elements in the iterable that satisfy the given predicate.
        If no predicate is provided, returns the total number of elements in the iterable.

        :param predicate: The predicate function used to filter the items.
        :return: The number of elements that satisfy the given predicate.
        """
        
        if predicate is None:
            if hasattr(self._collection, "__len__"):
                return len(self._collection)
            # If the iterable does not support __len__(), iterate over all items counting them
            return sum(1 for _ in self)

        return sum(1 for item in self if predicate(item))
   
    def Sorted(self, descending: bool = False):
        return LINQ(sorted(self, reverse=descending))
   
    def Batch(self, chunkSize: int = None, totalChunks:int = None):
        """
        Batches the elements of the iterable into chunks of the specified size. 
        
        Two variant of batching are supported, only one can be choosen (PS. desired chunk dimensions might be smaller if the iterable has fewer items)
        * predetermined chunkSize
        * predetermined totalChunks

        :param chunkSize: The size of each chunk (Batches the elements of the iterable into chunks of a specified size)
        :param totalChunks: The total number of chunks to create (Batches the elements of the iterable evenly into a fixed number of chunks)
        
        Example usage for chunkSize variant:
        >>> LINQ([1, 2, 3, 4, 5]).Batch(chunkSize=2).ToList()
        [[1,2], [3,4], [5]]

        Example usage for totalChunks variant:
        >>> LINQ([1, 2, 3, 4, 5]).BatchEvenly(totalChunks=2).ToList()
        [[1,3,5], [2,4]]
        """

        if(chunkSize is None and totalChunks is None) or (chunkSize is not None and totalChunks is not None):
            raise ValueError("Must provide one and only one of chunkSize or totalChunks.")

        if(chunkSize is not None):
            def batched(iterable, n):
                """Batch data into lists of length *n*. The last batch may be shorter.

                >>> list(batched('ABCDEFG', 3))
                [('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]
                """
                if n < 1:
                    raise ValueError('n must be at least one')
                it = iter(iterable)
                while True:
                    batch = list(islice(it, n))
                    if not batch:
                        break
                    yield batch
            return LINQ(batched(self, chunkSize))
        
        #totalchunks variant below

        evenlyBatchedList = [[] for _ in range(totalChunks)]
        for i, item in enumerate(self):
            evenlyBatchedList[i % totalChunks].append(item)
        
        collLength = i + 1 # enumerate index gives the actual index of element, so +1 for length of collection
        if(collLength < totalChunks):
            evenlyBatchedList = evenlyBatchedList[0:collLength]
        return LINQ(evenlyBatchedList)


    def OfType(self, targetType: type):
        """
        Filters the elements of the iterable based on the specified type.

        :param targetType: The type to filter by.   
        """
        if not isinstance(targetType, type):
            raise TypeError('The argument must be a type')
        
        return LINQ(item for item in self if isinstance(item, targetType))

    def ToList(self):
        return list(self)


    def __iter__(self):
        return self._iterator
   
    def __next__(self) -> _T:
        # Delegating the iteration to the wrapped iterator
        return next(self._iterator)

