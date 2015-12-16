#!/usr/bin/env python

def cp1252 (value):
    if type(value) == type([]):
        for elm in value:
            elm = cp1252(elm)
        return value

    if type(value) == type({}):
        for key, val in value.iteritems():
          value[key] = cp1252(val)
        return value

    if str(type(value)) == "<class 'bs4.element.NavigableString'>": return value.encode('cp1252')
    if str(type(value)) == "<type 'unicode'>": return value.encode('cp1252')
    return value.decode('cp1252')


