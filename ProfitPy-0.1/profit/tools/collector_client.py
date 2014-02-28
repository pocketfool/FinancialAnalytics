#!/usr/bin/env python
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
"""collector_client.py -> IB TWS data collection sub-app

This script connects to IB TWS after an initial delay.  Once connected, it
requests ticker data and saves that data on the specified interval.

The collector is implemented as a thread, but it does not run as a thread unless
the 'background_thread' option is set (it's not set by default).  This means
that the main interpreter thread executes the collector thread 'run' method
directly and not as a background thread.
"""
__about__ = {
    'author' : 'Troy Melhase, troy@gci.net',
    'date' : '2004/09/11 09:20:26',
    'file' : 'collector_client.py,v 0.3 2004/09/11 09:20:26 troy Exp',
    'tag' : 'profitpy-0_1',
    'revision' : '0.3',
}

import atexit
import cPickle
import optparse
import os
import threading
import time
import traceback

import profit.lib.session


class CollectorThread(threading.Thread):
    """ CollectorThread(...) -> saves an item to disk at regular intervals

    """
    closers = []

    def __init__(self, item, filename, snooze, stop_event):
        threading.Thread.__init__(self)
        self.closers.append(self)

        self.item = item
        self.filename = filename
        self.snooze = snooze
        self.stop_event = stop_event

        self.session_start = time.time()
        atexit.register(self.close)
        self.setDaemon(1)

    def run(self):
        """ run() -> main collection loop

            The loop executes every 'snooze' seconds while the 'stop_event'
            is not set.
        """
        print 'started'
        while not self.stop_event.isSet():
            time.sleep(self.snooze)
            self.flush()
            print 'save point'
        print 'done'

    def flush(self):
        """ flush() -> write the item to the file specified by 'filename'

        """
        filehandle = file(self.filename, 'wb')
        cPickle.dump(self.item, filehandle, -1)
        filehandle.close()

    def close(self):
        """ close() -> ho hum

        """
        try:
            self.flush()
        except (Exception, ):
            traceback.print_exc()
        print 'closed'

def tickers_shadow(tickers):
    """ tickers_shadow(tickers) -> make a shadow ticker supervisor

    """
    shadow = {}
    for key, ticker in tickers.items():
        shadow[key] = mapping = {}
        for skey, serseq in ticker.series.items():
            mapping[skey] = serseq
    return shadow


def session_builder():
    """ session_builder() -> new appropriate for collecting data

    """
    assm = profit.lib.session.Session(client_id=234)
    #for tickobj in assm.tickers.values():
    #    for series in tickobj.series.values():
    #        series.indexes = []
    #        try:
    #            delattr(series, 'strategy')
    #       except (AttributeError, ):
    #            pass
    return assm


def connect_broker(session, dsn):
    """ connect_broker(...) -> connect an session per the dsn

    """
    host, port = dsn.split(':')
    broker = session.broker
    broker.connect((host, int(port)))
    broker.request_external()


def collection_fullname(outdir, key):
    """ collection_fullname(...) -> name of the next collection data file

    """
    files = [name for name in os.listdir(outdir) if name.startswith(key + '.')]
    index = 1 + max([int(ext) for name, ext in 
                        [name.split('.') for name in files]])
    return os.path.join(outdir, '%s.%s' % (key, index, ))


def get_options():
    """ get_options() -> options for this script

    """
    default_life_span = (60 * 60 * 6) + (60 * 15)

    ## wait this long before attempting to connect to IB TWS
    default_init_delay = 60

    ## wait this long between saves
    default_save_interval = 60 * 5

    default_output_dir = './'
    default_dsn = 'localhost:7496'

    parser = optparse.OptionParser()
    parser.add_option('-I', '--init-delay', dest='init_delay',
                      help='initial delay in seconds',
                      action='store', type='int', default=default_init_delay)
    parser.add_option('-T', '--save-interval', dest='save_interval',
                      help='collection save interval',
                      action='store', type='int', default=default_save_interval)
    parser.add_option('-L', '--life-span', dest='life_span',
                      help='script life span in seconds',
                      action='store', type='int', default=default_life_span)
    parser.add_option('-O', '--output-dir', dest='output_directory',
                      help='data output directory',
                      action='store', type='string', default=default_output_dir)
    parser.add_option('-D', '--connect-dsn', dest='connection_dsn',
                      help='broker connection data source name',
                      action='store', type='string', default=default_dsn)
    parser.add_option('-B', '--background-thread', dest='background_thread',
                      action='store_true', default=False)

    return parser.parse_args()[0]


def main():
    """ main() -> main execution

    """
    options = get_options()
    session = session_builder()
    filename = collection_fullname(options.output_directory, 'tickers')
    shutdown_event = threading.Event()

    try:
        print 'pausing for %s seconds' % (options.init_delay, )
        time.sleep(options.init_delay)
        print 'connecting to %s' % (options.connection_dsn, )
        connect_broker(session, options.connection_dsn)
        print 'connected'
    except (Exception, ):
        traceback.print_exc()
        return

    shutdown_handler = lambda event: event.set()

    collector = CollectorThread(session.tickers, filename,
                                options.save_interval, shutdown_event)

    shutdown_timer = threading.Timer(options.life_span, shutdown_handler,
                                     [shutdown_event, ])

    shutdown_timer.start()

    if options.background_thread:
        collector.start()
    else:
        collector.run()
    collector.session = session
    return collector

if __name__ == '__main__':
    col = main()
