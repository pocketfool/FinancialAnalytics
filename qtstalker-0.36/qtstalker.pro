TEMPLATE = subdirs

# compile TALIB
#SUBDIRS += TALIB

# compile qtstalker lib
SUBDIRS += lib

# compile app
SUBDIRS += src

# compile quote plugins
SUBDIRS += plugins/quote/CME
SUBDIRS += plugins/quote/CSV
SUBDIRS += plugins/quote/NYBOT
SUBDIRS += plugins/quote/Yahoo

# install docs and i18n
SUBDIRS += docs
