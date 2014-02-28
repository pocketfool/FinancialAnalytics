TEMPLATE = lib

CONFIG += thread

# install the html files
docs.path = /usr/local/share/doc/qtstalker/html
docs.files = *.html
INSTALLS += docs

# install the html pic files
pics.path = /usr/local/share/doc/qtstalker/html
pics.files = *.png
INSTALLS += pics

# install the example indicator html files and pics
idocs.path = /usr/local/share/doc/qtstalker/html/indicator
idocs.files = indicator/*.html
idocs.files += indicator/*.png
INSTALLS += idocs

# install the CHANGELOG files
cl.path = /usr/local/share/doc/qtstalker/html
cl.files = CHANGELOG*
INSTALLS += cl

# install the past CHANGELOG files
pcl.path = /usr/local/share/doc/qtstalker/html/pastchanges
pcl.files = pastchanges/*.html
pcl.files += pastchanges/CHANGELOG*
INSTALLS += pcl

# install the translation files
i18n.path = /usr/local/share/qtstalker/i18n
i18n.files = ../i18n/*.qm
INSTALLS += i18n

# install the indicator files
indicator.path = /usr/local/share/qtstalker/indicator
# only install some explicit examples
indicator.files = ../misc/CUS_examples/bar
indicator.files += ../misc/CUS_examples/cdl-rel
indicator.files += ../misc/CUS_examples/cdl-rel-ma
indicator.files += ../misc/CUS_examples/RSI
indicator.files += ../misc/CUS_examples/STOCH
indicator.files += ../misc/CUS_examples/VOL
INSTALLS += indicator


