#!/usr/bin/python

#
#   www.combinatorialdesign.com
#
#   Copyright 2013 Pawel Wodnicki
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/
 
import sys
import os
import json

from collections import OrderedDict, Callable

# serialize scan settings to json file

# dictionary

# http://stackoverflow.com/questions/6190331/can-i-do-an-ordered-default-dict-in-python/
# http://code.activestate.com/recipes/523034-emulate-collectionsdefaultdict/
# https://gist.github.com/dsc/1512055

class OrderedJSONDecoder(json.JSONDecoder):
    """ As `JSONDecoder`, but passing `collections.OrderedDict`
    for `object_pairs_hook` by default.
    """
    def __init__(self,
        encoding=None,
        object_hook=None,
        parse_float=None,
        parse_int=None,
        parse_constant=None,
        strict=True,
        object_pairs_hook=OrderedDict
    ):
        super(OrderedJSONDecoder, self).__init__(
           encoding=encoding,
           object_hook=object_hook,
           parse_float=parse_float,
           parse_int=parse_int,
           parse_constant=parse_constant,
           strict=strict,
           object_pairs_hook=object_pairs_hook
        )

class Settings(OrderedDict):
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
            not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def init(self):
        self['laser']={}
        self['laser']['x']=0
        self['laser']['y']=0

    def load(self, filename):
        try:
          with open(filename+'.json', 'r') as infile:
            self = OrderedDict(json.load(infile))
        except:
          print("failed loading settings file!");
          return False
        print("loaded");
        print(str(self))
        return True

    def store(self, filename):
       try:
         with open(filename+'.json', 'w') as outfile:
           json.dump(self, outfile)
       except:
         print("failed storing settings file!");
         return False
       return True


def load(filename):
   settings={}
   try:
       with open(filename+'.json', 'r') as infile:
           settings = Settings(None,json.load(infile))
   except:
       print("failed loading settings file!");
       return None
   print(str(settings))
   return settings

def store(filename, settings):
   try:
       with open(filename+'.json', 'w') as outfile:
           json.dump(settings, outfile)
   except:
       print("failed storing settings file!");
       return False
   return True



def load_settings(filename):
   try:
       with open(filename+'.json', 'r') as infile:
           scan_settings = json.load(infile)
   except:
       print("failed loading settings file!");
       return False
   print(str(scan_settings))
   return True

def store_settings(filename):
   try:
       with open(filename+'.json', 'w') as outfile:
           json.dump(scan_settings, outfile)
   except:
       print("failed storing settings file!");
       return False
   return True

def init_settings():
   scan_settings.laser={}
   scan_settings.laser['x']=0
   scan_settings.laser['y']=0
   print(str(scan_settings))

def get_settings():
   print(str(scan_settings))
   return scan_settings


if __name__ == "__main__":
    filename=''
    scan_settings = Settings()

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("need some file!");
        sys.exit(-1);

    if not scan_settings.load(filename) : 
        print("settings not found so we make them");
        scan_settings.init()
        scan_settings.store(filename)
    else: 
        pass

    print("done from main");
    #sys.exit();

