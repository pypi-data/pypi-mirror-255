import urllib3
import urllib3.contrib.socks

URL_ORIGIN = "/https://www.youtube.com"


class TorManager:
    MAX_TRIES = 3
    # Remember the 7-sec wait times, so make cooldown be two of those
    # (otherwise it will retry forever if 429s never end)
    COOLDOWN_TIME = 14
    def __init__(self):
        self.old_tor_connection_pool = None
        self.tor_connection_pool = urllib3.contrib.socks.SOCKSProxyManager(
            'socks5h://127.0.0.1:' + str(settings.tor_port) + '/',
            cert_reqs = 'CERT_REQUIRED')
        self.tor_pool_refresh_time = time.monotonic()
        settings.add_setting_changed_hook(
            'tor_port',
            lambda old_val, new_val: self.refresh_tor_connection_pool(),
        )

        self.new_identity_lock = gevent.lock.BoundedSemaphore(1)
        self.last_new_identity_time = time.monotonic() - 20
        self.try_num = 1

    def refresh_tor_connection_pool(self):
        self.tor_connection_pool.clear()

        # Keep a reference for 5 min to avoid it getting garbage collected
        # while sockets still in use
        self.old_tor_connection_pool = self.tor_connection_pool

        self.tor_connection_pool = urllib3.contrib.socks.SOCKSProxyManager(
            'socks5h://127.0.0.1:' + str(settings.tor_port) + '/',
            cert_reqs = 'CERT_REQUIRED')
        self.tor_pool_refresh_time = time.monotonic()

    def get_tor_connection_pool(self):
        # Tor changes circuits after 10 minutes:
        # https://tor.stackexchange.com/questions/262/for-how-long-does-a-circuit-stay-alive
        current_time = time.monotonic()

        # close pool after 5 minutes
        if current_time - self.tor_pool_refresh_time > 300:
            self.refresh_tor_connection_pool()

        return self.tor_connection_pool

    def new_identity(self, time_failed_request_started):
        '''return error, or None if no error and the identity is fresh'''

        # The overall pattern at maximum (always returning 429) will be
        # R N (0) R N (6) R N (6) R | (12) R N (0) R N (6) ...
        # where R is a request, N is a new identity, (x) is a wait time of
        # x sec, and | is where we give up and display an error to the user.

        print('new_identity: new_identity called')
        # blocks if another greenlet currently has the lock
        self.new_identity_lock.acquire()
        print('new_identity: New identity lock acquired')

        try:
            # This was caused by a request that failed within a previous,
            # stale identity
            if time_failed_request_started <= self.last_new_identity_time:
                print('new_identity: Cancelling; request was from stale identity')
                return None

            delta = time.monotonic() - self.last_new_identity_time
            if delta < self.COOLDOWN_TIME and self.try_num == 1:
                err = ('Retried with new circuit %d times (max) within last '
                       '%d seconds.' % (self.MAX_TRIES, self.COOLDOWN_TIME))
                print('new_identity:', err)
                return err
            elif delta >= self.COOLDOWN_TIME:
                self.try_num = 1

            try:
                port = settings.tor_control_port
                with stem.control.Controller.from_port(port=port) as controller:
                    controller.authenticate('')
                    print('new_identity: Getting new identity')
                    controller.signal(stem.Signal.NEWNYM)
                    print('new_identity: NEWNYM signal sent')
                    self.last_new_identity_time = time.monotonic()
                self.refresh_tor_connection_pool()
            except stem.SocketError:
                traceback.print_exc()
                return 'Failed to connect to Tor control port.'
            finally:
                original_try_num = self.try_num
                self.try_num += 1
                if self.try_num > self.MAX_TRIES:
                    self.try_num = 1

            # If we do the request right after second new identity it won't
            # be a new IP, based on experiments.
            # Not necessary after first new identity
            if original_try_num > 1:
                print('Sleeping for 7 seconds before retrying request')
                time.sleep(7)   # experimentally determined minimum

            return None
        finally:
            self.new_identity_lock.release()