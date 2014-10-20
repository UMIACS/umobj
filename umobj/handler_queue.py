#!/usr/bin/env python

import signal


class HandlerQueue:

    '''
    Only a single function can be registered with a signal, which is a problem
    if multiple functions need to be registered and run against a given signal.
    HandlerQueue lets multiple handlers be registered and called for a given
    signal.
    '''

    @staticmethod
    def init_handler_queue():
        '''Initiiate the initial queue for signal handlers.'''
        HandlerQueue._queue = {}

    @staticmethod
    def add_handler(sig, function, prepend=True):
        '''
        Add a handler to the queue of functions to run when a singnal is
        fired off.  Functions can be redefined, where a function's name is
        unique across the keyspace.
        '''
        # create the backing queue if it doesn't exist
        try:
            HandlerQueue._queue
        except AttributeError:
            HandlerQueue.init_handler_queue()

        # check if handlers have already been registered against this signal
        try:
            HandlerQueue._queue[sig]
        except KeyError:
            HandlerQueue._queue[sig] = []
            signal.signal(sig, HandlerQueue.call_handlers)

        # if a function is being inserted with the same name as an already
        # inserted function, remove the old one.  This is because usually when
        # a function is being redefined, its closure has changed.
        for fun in HandlerQueue._queue[sig]:
            if fun.__name__ == function.__name__:
                HandlerQueue._queue.pop(fun, None)

        if prepend:
            HandlerQueue._queue[sig].insert(0, function)
        else:
            HandlerQueue._queue[sig].append(function)

    @staticmethod
    def call_handlers(signal, frame):
        '''
        This is the function that is actually registered to handle the
        signal.  It in turn calls all of the functions registered for this
        signal.
        '''
        for handler in HandlerQueue._queue[signal]:
            handler(signal, frame)
