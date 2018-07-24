#!/usr/bin/env python3
lst = []
def func1(lst2,i):
    lst.append(lambda: i)
    print("%s %s %s" % (i, lst[i], lst[i]()))


func1(lst,0)
func1(lst,1)
func1(lst,2)
func1(lst,3)
func1(lst,4)
print(lst[0])
for f in lst:
    print(f())
    print(f)

t = []
t.append({'one': 'onezer','two': 'twozer', 'four': 'fourzer'})
print(t[0]['one'])
print(t[0]['two'])
print(t[0]['four'])
print(t[0])
for thing in t:
    print(thing)
    print(thing['one'])
