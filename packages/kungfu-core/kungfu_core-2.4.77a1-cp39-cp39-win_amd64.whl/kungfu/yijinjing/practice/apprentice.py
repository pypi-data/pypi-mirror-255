#  SPDX-License-Identifier: Apache-2.0

import kungfu
import psutil
import signal
import kungfu.yijinjing.io as kfio
import kungfu.yijinjing.journal as kfj
from . import os_signal

yjj = kungfu.__binding__.yijinjing


class Apprentice(yjj.apprentice):
    def __init__(self, ctx):
        yjj.apprentice.__init__(
            self,
            yjj.location(
                kfj.MODES[ctx.mode],
                kfj.CATEGORIES[ctx.category],
                ctx.group,
                ctx.name,
                ctx.runtime_locator,
            ),
            low_latency=ctx.low_latency,
        )
        self.ctx = ctx
        self._process = psutil.Process()

        os_signal.handle_os_signals(self.exit_gracefully)

    def go(self):
        kfio.checkin(self.ctx, self.io_device)
        yjj.apprentice.go(self)

    def exit_gracefully(self, signum, frame):
        self.stop()
        if signum == signal.SIGTERM:
            self.logger.info("%s terminated", self.ctx.name)
