#!/usr/bin/env python
##~
##~ Copyright 2004 Troy Melhase <troy@gci.net>
##~ 
##~ This file is part of the ProfitPy package.
##~ 
##~ ProfitPy is free software; you can redistribute it and/or modify
##~ it under the terms of the GNU General Public License as published by
##~ the Free Software Foundation; either version 2 of the License, or
##~ (at your option) any later version.
##~ 
##~ ProfitPy is distributed in the hope that it will be useful,
##~ but WITHOUT ANY WARRANTY; without even the implied warranty of
##~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##~ GNU General Public License for more details.
##~ 
##~ You should have received a copy of the GNU General Public License
##~ along with ProfitPy; if not, write to the Free Software
##~ Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##~
""" The profit.examples initialization script

This module brings in symbols from the package for easier location.  This 
stands out against the normal import semantics in this package, and that's 
because these names are so often typed at the command prompt.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : '__init__.py,v 0.5 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.5',
}

from profit.examples.simple import connection_id_from_database
from profit.examples.simple import modified_account_object
from profit.examples.simple import small_tickers_listing

from profit.examples.braindeadness import braindead_strategy_factory
braindead_strategy = braindead_strategy_factory

from profit.examples.slightlybetter import slightly_better_factory
slightly_better = slightly_better_factory

