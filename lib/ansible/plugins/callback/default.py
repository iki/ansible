# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'default'

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if 'exception' in result._result:
            if self._display.verbosity < 3:
                # extract just the actual error message from the exception text
                error = result._result['exception'].strip().split('\n')[-1]
                msg = "An exception occurred during task execution. To see the full traceback, use -vvv. The error was: %s" % error
            else:
                msg = "An exception occurred during task execution. The full traceback is:\n" + result._result['exception']

            self._display.display(msg, color='red')

            # finally, remove the exception from the result so it's not shown every time
            del result._result['exception']

        self._display.display("fatal: [%s]: FAILED! => %s" % (result._host.get_name(), self._dump_results(result._result)), color='red')

        if result._task.ignore_errors:
            self._display.display("...ignoring", color='cyan')

    def v2_runner_on_ok(self, result):

        if result._task.action == 'include':
            msg = 'included: %s for %s' % (result._task.args.get('_raw_params'), result._host.name)
            color = 'cyan'
        elif result._result.get('changed', False):
            msg = "changed: [%s]" % result._host.get_name()
            color = 'yellow'
        else:
            msg = "ok: [%s]" % result._host.get_name()
            color = 'green'

        if (self._display.verbosity > 0 or 'verbose_always' in result._result) and result._task.action not in ('setup', 'include'):
            indent = None
            if 'verbose_always' in result._result:
                indent = 4
                del result._result['verbose_always']
            msg += " => %s" % self._dump_results(result._result, indent=indent)
        self._display.display(msg, color=color)

    def v2_runner_on_skipped(self, result):
        msg = "skipping: [%s]" % result._host.get_name()
        if self._display.verbosity > 0 or 'verbose_always' in result._result:
            indent = None
            if 'verbose_always' in result._result:
                indent = 4
                del result._result['verbose_always']
            msg += " => %s" % self._dump_results(result._result, indent=indent)
        self._display.display(msg, color='cyan')

    def v2_runner_on_unreachable(self, result):
        self._display.display("fatal: [%s]: UNREACHABLE! => %s" % (result._host.get_name(), self._dump_results(result._result)), color='red')

    def v2_playbook_on_no_hosts_matched(self):
        self._display.display("skipping: no hosts matched", color='cyan')

    def v2_playbook_on_no_hosts_remaining(self):
        self._display.banner("NO MORE HOSTS LEFT")

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._display.banner("TASK [%s]" % task.get_name().strip())

    def v2_playbook_on_cleanup_task_start(self, task):
        self._display.banner("CLEANUP TASK [%s]" % task.get_name().strip())

    def v2_playbook_on_handler_task_start(self, task):
        self._display.banner("RUNNING HANDLER [%s]" % task.get_name().strip())

    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if not name:
            msg = "PLAY"
        else:
            msg = "PLAY [%s]" % name

        self._display.banner(name)
