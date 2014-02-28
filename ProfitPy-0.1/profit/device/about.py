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
"""

This module defines information about the Profit Device application.

"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:25',
    'file' : 'about.py,v 0.3 2004/09/11 09:20:25 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.3',
}

import kdecore


appName = 'profitdevice'
progName = 'Profit Device'
authorName = 'Troy Melhase'
authorEmail = bugsEmailAddress = 'troy@gci.net'
version = '0.1'
shortDescription = 'The Profit Device Application'
licenseType = kdecore.KAboutData.License_GPL_V2
copyrightStatement = '(c) 2004, ' + authorName
homePageAddress = 'http://sourceforge.net/projects/profitpy'
aboutText = """
Implement your own trading system with the ProfitPy toolkit and the execute it
with the Profit Device.
"""


aboutData = kdecore.KAboutData(
    appName,
    progName,
    version,
    shortDescription,
    licenseType,
    copyrightStatement,
    aboutText,
    homePageAddress,
    bugsEmailAddress,
)
aboutData.addAuthor(authorName, '', authorEmail)
