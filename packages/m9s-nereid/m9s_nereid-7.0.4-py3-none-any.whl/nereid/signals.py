# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from flask.signals import (  # noqa
    _signals, got_request_exception, request_finished, request_started,
    request_tearing_down, template_rendered)

#: Login signal
#:  - This signal is triggered when a succesful login takes place
login = _signals.signal('login')

#: Failed Login
#:  - This signal is raised when a login fails
failed_login = _signals.signal('failed-login')

#: Logout
#: Triggered when a logout occurs
logout = _signals.signal('logout')

#: Registration
#: Triggered when a user registers
registration = _signals.signal('registration')


transaction_start = _signals.signal('nereid.transaction.start')
transaction_stop = _signals.signal('nereid.transaction.stop')
# transaction_commit is triggered when transaction successfully ends
transaction_commit = _signals.signal('nereid.transaction.commit')
