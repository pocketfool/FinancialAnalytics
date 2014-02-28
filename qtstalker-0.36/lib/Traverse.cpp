/*
 *  Qtstalker stock charter
 *
 *  Copyright (C) 2001-2007 Stefan S. Stratigakos
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
 *  USA.
 */

#include "Traverse.h"
#include <qdir.h>
#include <qfileinfo.h>

Traverse::Traverse (Traverse::Type t)
{
  type = t;
}

Traverse::~Traverse ()
{
}

void Traverse::traverse (QString dirname)
{
  QDir dir(dirname);
  dir.setFilter(QDir::Dirs|QDir::Files);

  const QFileInfoList *fileinfolist = dir.entryInfoList();
  QFileInfoListIterator it(*fileinfolist);
  QFileInfo *fi;
  while((fi = it.current()))
  {
    if(fi->fileName() == "." || fi->fileName() == "..")
    {
      ++it;
      continue;
    }

    if(fi->isDir() && fi->isReadable())
    {
      if (type == Dir)
        list.append(fi->absFilePath());
      traverse(fi->absFilePath());
    }
    else
    {
      if (type == File)
        list.append(fi->absFilePath());
    }

    ++it;
  }
}

void Traverse::getList (QStringList &l)
{
  l = list;
}

void Traverse::clear ()
{
  list.clear();
}


