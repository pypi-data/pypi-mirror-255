# Copyright 2023-2024 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module implementing an indexable circlar array data structure

Module implementing a stateful circular array data structures with amortized O(1)
pushing and popping from either end and O(1) indexing. Implemented with a Python List,
this data structure will resize itself as needed.
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = ['CircularArray']
__author__ = "Geoffrey R. Scheller"
__copyright__ = "Copyright (c) 2023-2024 Geoffrey R. Scheller"
__license__ = "Apache License 2.0"

from typing import Any, Callable
from itertools import chain

class CircularArray:
    """An auto-resizing, indexable, double sided queue data structure. O(1) indexing,
    O(1) pushes and pops either end. Useful as an improved version of a Python list.
    Used in a has-a relationship by grscheller.datastructure when implementing other
    data structures where its functionality is more likely restricted than augmented.

    Note: Indexing, pushing & popping and size determination are all O(1) operations

    Note: Popping from an empty Circulararray returns None

    Note: Use in a boolean context to determine if empty

    Note: A Circulararray will resize itself as needed

    Note: For now, Circulararrays are not sliceable

    Raises: IndexError
    """
    __slots__ = '_count', '_capacity', '_front', '_rear', '_list'

    def __init__(self, *data):
        """Construct a double sided indexible queue."""
        size = len(data)
        capacity = size + 2
        self._count = size
        self._capacity = capacity
        self._front = 0
        self._rear = (size - 1) % capacity
        self._list = list(data)
        self._list.append(None)
        self._list.append(None)

    def __iter__(self):
        """Generator yielding the cached contents of the current state of
        the CircularArray.
        """
        if self._count > 0:
            cap, rear, pos, currList = \
                self._capacity, self._rear, self._front, self._list.copy()
            while pos != rear:
                yield currList[pos]
                pos = (pos + 1) % cap
            yield currList[pos]

    def __reversed__(self):
        """Generator yielding the cached contents of the current state of
        the CircularArray in reverse order.
        """
        if self._count > 0:
            cap, front, pos, currList = \
                self._capacity, self._front, self._rear, self._list.copy()
            while pos != front:
                yield currList[pos]
                pos = (pos - 1) % cap
            yield currList[pos]

    def __repr__(self):
        return f'{self.__class__.__name__}(' + ', '.join(map(repr, self)) + ')'

    def __str__(self):
        return "(|" + ", ".join(map(repr, self)) + "|)"

    def __bool__(self):
        """Returns true if the CircularArray is not empty."""
        return self._count > 0

    def __len__(self):
        """Returns current number of values in the CirclularArray."""
        return self._count

    def __getitem__(self, index: int) -> Any:
        """Get value at a valid index, otherwise raise IndexError."""
        cnt = self._count
        if 0 <= index < cnt:
            return self._list[(self._front + index) % self._capacity]
        elif -cnt <= index < 0:
            return self._list[(self._front + cnt + index) % self._capacity]
        else:
            low = -cnt
            high = cnt - 1
            msg = f'Out of bounds: index = {index} not between {low} and {high}'
            msg += ' while getting value.'
            msg0 = 'Trying to get value from an empty data structure.'
            if cnt > 0:
                raise IndexError(msg)
            else:
                raise IndexError(msg0)

    def __setitem__(self, index: int, value: Any) -> Any:
        """Set value at a valid index, otherwise raise IndexError."""
        cnt = self._count
        if 0 <= index < cnt:
            self._list[(self._front + index) % self._capacity] = value
        elif -cnt <= index < 0:
            self._list[(self._front + cnt + index) % self._capacity] = value
        else:
            low = -cnt
            high = cnt - 1
            msg = f'Out of bounds: index = {index} not between {low} and {high}'
            msg += 'while setting value.'
            msg0 = 'Trying to get value from an empty data structure.'
            if cnt > 0:
                raise IndexError(msg)
            else:
                raise IndexError(msg0)

    def __eq__(self, other):
        """Returns True if all the data stored in both compare as equal.
        Worst case is O(n) behavior for the true case.
        """
        if not isinstance(other, type(self)):
            return False

        if self._count != other._count:
            return False

        left, frontL, capL, cnt = self, self._front, self._capacity, self._count
        right, frontR, capR = other, other._front, other._capacity

        nn = 0
        while nn < cnt:
            if left._list[(frontL+nn)%capL] != right._list[(frontR+nn)%capR]:
                return False
            nn += 1
        return True

    def _double(self) -> None:
        """Double the capacity of the CircularArray."""
        if self._front > self._rear:
            data  = self._list[self._front:]
            data += self._list[:self._rear+1]
            data += [None]*(self._capacity)
        else:
            data  = self._list
            data += [None]*(self._capacity)

        self._list, self._capacity,     self._front, self._rear = \
        data,       2 * self._capacity, 0,           self._count - 1

    def copy(self) -> CircularArray:
        """Return a shallow copy of the CircularArray."""
        return CircularArray(*self)

    def reverse(self) -> CircularArray:
        return CircularArray(*reversed(self))

    def pushR(self, d: Any) -> None:
        """Push data onto the rear of the CircularArray."""
        if self._count == self._capacity:
            self._double()
        self._rear = (self._rear + 1) % self._capacity
        self._list[self._rear] = d
        self._count += 1

    def pushL(self, d: Any) -> None:
        """Push data onto the front of the CircularArray."""
        if self._count == self._capacity:
            self._double()
        self._front = (self._front - 1) % self._capacity
        self._list[self._front] = d
        self._count += 1

    def popR(self) -> Any:
        """Pop data off the rear of the CirclularArray, returns None if empty."""
        if self._count == 0:
            return None
        else:
            d = self._list[self._rear]

            self._count, self._list[self._rear], self._rear = \
                self._count-1, None, (self._rear - 1) % self._capacity

            return d

    def popL(self) -> Any:
        """Pop data off the front of the CirclularArray, returns None if empty."""
        if self._count == 0:
            return None
        else:
            d = self._list[self._front]

            self._count, self._list[self._front], self._front = \
                self._count-1, None, (self._front+1) % self._capacity

            return d

    def map(self, f: Callable[[Any], Any]) -> CircularArray:
        """Apply function f over the CircularArray's contents and return
        the results in a new CircularArray.
        """
        return CircularArray(*map(f, self))

    def mapSelf(self, f: Callable[[Any], Any]) -> None:
        """Apply function f over the CircularArray's contents mutating the
        CircularArray, don't return anything.
        """
        ca  = CircularArray(*map(f, self))
        self._count, self._capacity, self._front, self._rear, self._list = \
            ca._count, ca._capacity, ca._front, ca._rear, ca._list

    def foldL(self, f: Callable[[Any, Any], Any], initial: Any=None) -> Any:
        """Fold left with an optional initial value. The first argument of f
        is the accumulated value. If CircularArray is empty and no initial value
        given, return None.
        """
        if self._count == 0:
            return initial
        
        if initial is None:
            vs = iter(self)
        else:
            vs = chain((initial,), self)

        value = next(vs)
        for v in vs:
            value = f(value, v)

        return value

    def foldR(self, f: Callable[[Any, Any], Any], initial: Any=None) -> Any:
        """Fold right with an optional initial value. The second argument of f
        is the accumulated value. If CircularArray is empty and no initial
        value given, return None.
        """
        if self._count == 0:
            return initial
        
        if initial is None:
            vs = reversed(self)
        else:
            vs = chain((initial,), reversed(self))

        value = next(vs)
        for v in vs:
            value = f(v, value)

        return value

    # House keeping methods

    def compact(self) -> None:
        """Compact the CircularArray as much as possible."""
        match self._count:
            case 0:
                self._list, self._capacity, self._front, self._rear = [None]*2, 2, 0, 1
            case 1:
                data = [self._list[self._front], None]
                self._list, self._capacity, self._front, self._rear = data, 2, 0, 0
            case _:
                if self._front > self._rear:
                    data  = self._list[self._front:]
                    data += self._list[:self._rear+1]
                else:
                    data  = self._list[self._front:self._rear+1]
                self._list, self._capacity, self._front, self._rear = data, self._count, 0, self._capacity - 1

    def empty(self) -> None:
        """Empty the CircularArray, keep current capacity."""
        self._list, self._front, self._rear = \
            [None]*self._capacity, 0, self._capacity-1

    def capacity(self) -> int:
        """Returns current capacity of the CircularArray."""
        return self._capacity

    def fractionFilled(self) -> float:
        """Returns fractional capacity of the CircularArray."""
        return self._count/self._capacity

    def resize(self, addCapacity = 0) -> None:
        """Compact the CircularArray and add extra capacity."""
        self.compact()
        if addCapacity > 0:
            self._list = self._list + [None]*addCapacity
            self._capacity += addCapacity
            if self._count == 0:
                self._rear = self._capacity - 1

if __name__ == "__main__":
    pass
