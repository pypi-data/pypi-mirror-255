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

from grscheller.circular_array import CircularArray

class TestCircularArray:
    def test_mutate_returns_none(self):
        ca1 = CircularArray()
        ca1.pushL(1)
        ca1.pushL(2)
        ret = ca1.pushL(3)
        assert ret is None
        ca1.pushR(1)
        ca1.pushR(2)
        ret = ca1.pushR(3)
        assert ret is None
        ret = ca1.mapSelf(lambda x: x+1)
        assert ret is None
        assert ca1.popL() == ca1.popR() == 4
        ca2 = ca1.map(lambda x: x+1)
        assert ca1 is not ca2
        assert ca1 != ca2
        assert len(ca1) == len(ca2)

    def test_push_then_pop(self):
        c = CircularArray()
        pushed = 42
        c.pushL(pushed)
        popped = c.popL()
        assert pushed == popped
        assert len(c) == 0
        assert c.popL() is None
        pushed = 0
        c.pushL(pushed)
        popped = c.popR()
        assert pushed == popped == 0
        assert not c
        pushed = 0
        c.pushR(pushed)
        popped = c.popL()
        assert popped is not None
        assert pushed == popped
        assert len(c) == 0
        pushed = ''
        c.pushR(pushed)
        popped = c.popR()
        assert pushed == popped
        assert len(c) == 0
        c.pushR('first')
        c.pushR('second')
        c.pushR('last')
        assert c.popL() == 'first'
        assert c.popR() == 'last'
        assert c
        c.popL()
        assert len(c) == 0

    def test_iterators(self):
        data = [*range(100)]
        c = CircularArray(*data)
        ii = 0
        for item in c:
            assert data[ii] == item
            ii += 1
        assert ii == 100

        data.append(100)
        c = CircularArray(*data)
        data.reverse()
        ii = 0
        for item in reversed(c):
            assert data[ii] == item
            ii += 1
        assert ii == 101

        c0 = CircularArray()
        for _ in c0:
            assert False
        for _ in reversed(c0):
            assert False

        data = ()
        c0 = CircularArray(*data)
        for _ in c0:
            assert False
        for _ in reversed(c0):
            assert False

    def test_capacity(self):
        c = CircularArray()
        assert c.capacity() == 2

        c = CircularArray(1, 2)
        assert c.fractionFilled() == 2/4

        c.pushL(0)
        assert c.fractionFilled() == 3/4

        c.pushR(3)
        assert c.fractionFilled() == 4/4

        c.pushR(4)
        c.pushL(5)
        assert c.fractionFilled() == 6/8

        assert len(c) == 6
        assert c.capacity() == 8

        c.resize()
        assert c.fractionFilled() == 6/6

        c.resize(30)
        assert c.fractionFilled() == 6/36

    def test_equality(self):
        c1 = CircularArray(1, 2, 3, 'Forty-Two', (7, 11, 'foobar'))
        c2 = CircularArray(2, 3, 'Forty-Two')
        c2.pushL(1)
        c2.pushR((7, 11, 'foobar'))
        assert c1 == c2

        tup2 = c2.popR()
        assert c1 != c2

        c2.pushR((42, 'foofoo'))
        assert c1 != c2

        c1.popR()
        c1.pushR((42, 'foofoo'))
        c1.pushR(tup2)
        c2.pushR(tup2)
        assert c1 == c2

        holdA = c1.popL()
        c1.resize(42)
        holdB = c1.popL()
        holdC = c1.popR()
        c1.pushL(holdB)
        c1.pushR(holdC)
        c1.pushL(holdA)
        c1.pushL(200)
        c2.pushL(200)
        assert c1 == c2

    def test_map(self):
        c0 = CircularArray(1,2,3,10)
        c1 = c0.copy()
        c2 = c1.map(lambda x: x*x-1)
        assert c2 == CircularArray(0,3,8,99)
        assert c1 != c2
        assert c1 == c0
        assert c1 is not c0
        assert len(c1) == len(c2) == 4

    def test_mapMutate(self):
        c1 = CircularArray(1,2,3,10)
        c1.mapSelf(lambda x: x*x-1)
        assert c1 == CircularArray(0,3,8,99)
        assert len(c1) == 4

    def test_get_set_items(self):
        c1 = CircularArray('a', 'b', 'c', 'd')
        c2 = c1.copy()
        assert c1 == c2
        c1[2] = 'cat'
        c1[-1] = 'dog'
        assert c2.popR() == 'd'
        assert c2.popR() == 'c'
        c2.pushR('cat')
        try:
            c2[3] = 'dog'       # no such index
        except IndexError:
            assert True
        else:
            assert False
        assert c1 != c2
        c2.pushR('dog')
        assert c1 == c2
        c2[1] = 'bob'
        assert c1 != c2
        assert c1.popL() == 'a'
        c1[0] = c2[1]
        assert c1 != c2
        assert c2.popL() == 'a'
        assert c1 == c2

    def test_foldL(self):
        c1 = CircularArray()
        assert c1.foldL(lambda x, y: x + y) == None
        assert c1.foldL(lambda x, y: x + y, initial=42) == 42

        c2 = CircularArray(*range(1, 11))
        assert c2.foldL(lambda x, y: x + y) == 55
        assert c2.foldL(lambda x, y: x + y, initial=10) == 65
        c3 = CircularArray(*range(5))

        def f(vs: list[int], v: int) -> list[int]:
            vs.append(v)
            return vs

        assert c3.foldL(f, initial=[]) == [0, 1, 2, 3, 4]

    def test_foldR(self):
        c1 = CircularArray()
        assert c1.foldR(lambda x, y: x * y) == None
        assert c1.foldR(lambda x, y: x * y, initial=42) == 42

        c2 = CircularArray(*range(1, 6))
        assert c2.foldR(lambda x, y: x * y) == 120
        assert c2.foldR(lambda x, y: x * y, initial=10) == 1200

        def f(v: int, vs: list[int]) -> list[int]:
            vs.append(v)
            return vs

        c3 = CircularArray(*range(5))
        assert c3.foldR(f, initial=[]) == [4, 3, 2, 1, 0]

