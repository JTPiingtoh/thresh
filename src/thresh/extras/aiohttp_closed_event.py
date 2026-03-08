import asyncio
import functools


def create_aiohttp_closed_event(session) -> asyncio.Event:
    """Work around aiohttp issuethat doesn't properly close transports on exit.

    See https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-592596034

    Returns:
       An event that will be set once all transports have been properly closed.
    """

    transports = 0
    all_is_lost = asyncio.Event()


    if len(session.connector._conns) == 0:
        all_is_lost.set()
        return all_is_lost

    def connection_lost(exc, orig_lost):
        nonlocal transports

        try:
            orig_lost(exc)
        finally:
            transports -= 1
            if transports == 0:
                all_is_lost.set()

    def eof_received(orig_eof_received):
        try:
            orig_eof_received()
        except AttributeError:
            # It may happen that eof_received() is called after
            # _app_protocol and _transport are set to None.
            pass

    for conn in session.connector._conns.values():
        for handler, _ in conn:
            proto = getattr(handler.transport, "_ssl_protocol", None)
            if proto is None:
                continue

            transports += 1
            orig_lost = proto.connection_lost
            orig_eof_received = proto.eof_received

            proto.connection_lost = functools.partial(connection_lost, orig_lost=orig_lost)
            proto.eof_received = functools.partial(eof_received, orig_eof_received=orig_eof_received)

    return all_is_lost

