#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""
psdhandlers.py:
"""

import ast

import pandas


class AbstractHandler(object):
    _fmts = []

    def __init__(self):
        self._kwargs = {}
        self._cols = None
        self._rows = None

    def parseAttrName(self, attr_name):
        """:return (DataFrame)"""
        if attr_name != '':
            args = ast.literal_eval(attr_name)

            if isinstance(args, dict):
                self.addKwargs(args)
            elif not isinstance(args, tuple):
                self.addArg(0, args)
            else:
                if isinstance(args[-1], dict):
                    self.addKwargs(args[-1])
                    self.addArgs(args[:-1])
                else:
                    self.addArgs(args)

        df = self.read()
        df = self.getColumns(df, self._cols)  # Cut columns
        df = self.getRows(df, self._rows)  # Cut rows

        return df

    @classmethod
    def canHandle(cls, ext):
        return ext in cls._fmts

    def setFilename(self, filename):
        self.filename = filename

    def read(self):
        raise NotImplementedError("read cannot be called"
                                  " for AbstractHandler")

    def addArg(self, pos, arg):
        raise NotImplementedError("addArg cannot be called"
                                  " for AbstractHandler")

    def addArgs(self, args):
        for pos, arg in enumerate(args):
            self.addArg(pos, arg)

    def addKwargs(self, args):
        for arg in args:
            self._kwargs[arg] = args[arg]

    @staticmethod
    def getColumns(df, columns):
        if columns:
            return df[columns]
        return df

    @staticmethod
    def getRows(df, rows):
        if rows:
            if len(rows) == 2:
                return df[rows[0]:rows[1]]
            return df[rows[0]:rows[0] + 1]
        return df


class CSVHandler(AbstractHandler):
    _fmts = ['.csv']

    def read(self):
        return pandas.read_csv(self.filename, **self._kwargs)

    def addArg(self, pos, arg):
        if pos == 0:
            self._cols = arg
        else:
            self._rows = arg


class XLSHandler(AbstractHandler):
    _fmts = ['.xls', '.xlsx']

    def read(self):
        return pandas.read_excel(self.filename, **self._kwargs)

    def addArg(self, pos, arg):
        if pos == 0 and arg != '':
            self._kwargs['sheetname'] = arg
        elif pos == 1:
            self._cols = arg
        else:
            self._rows = arg


schemesMap = {'pds': AbstractHandler,
              'pds-csv': CSVHandler,
              'pds-xls': XLSHandler
              }
