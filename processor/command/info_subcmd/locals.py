# -*- coding: utf-8 -*-
#
#   Copyright (C) 2008-2009, 2013, 2015, 2018, 2020, 2023 Rocky
#   Bernstein <rocky@gnu.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
import re
import traceback

from getopt import getopt, GetoptError

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import pp as Mpp
from trepan.lib import complete as Mcomplete

# when the "with" statement is used, there
# can be get variables having names
# _[1], _[2], etc.
_with_local_varname = re.compile(r"_\[[0-9+]\]")


class InfoLocals(Mbase_subcmd.DebuggerSubcommand):
    """**info locals** [-l | --list | | -h --help]

        **info locals** [*var1 ...*]

    **info locals** *

    With no arguments, show all of the local variables of the current stack
    frame. If a list of names is provide limit display to just those
    variables.

    If `*` is given, just show the variable names, not the values.

    See also:
    ---------
    `info globals`, `info args`, `info frame`"""

    min_abbrev = 2
    need_stack = True
    short_help = "Show the local variables of current stack frame"

    def complete(self, prefix):
        completions = sorted(["*"] + self.proc.curframe.f_locals.keys())
        return Mcomplete.complete_token(completions, prefix)

    def run_frame(self, args, frame):
        if not frame:
            self.errmsg("No frame selected")
            return False

        try:
            opts, args = getopt(
                args,
                "hl",
                ["help", "list"],
            )
        except GetoptError as err:
            # print help information and exit:
            self.errmsg(
                str(err)
            )  # will print something like "option -a not recognized"
            return

        list_only = False
        for o, a in opts:
            if o in ("-h", "--help"):
                self.proc.commands["help"].run(["help", "info", "locals"])
                return
            elif o in ("-l", "--list"):
                list_only = True
            else:
                self.errmsg("unhandled option '%s'" % o)
            pass
        pass

        # print(f"{names=}")
        # print(f"{args=}")
        # print(f"{frame=}")
        print(f"{frame.f_locals}")
        return
        names = list(frame.f_locals.keys())
        if list_only:
            for name in names:
                self.msg(name)
            return
        if len(args) > 0 and args[0] == "*":
            self.section("locals")
            self.msg(self.columnize_commands(names))
        elif len(args) == 0:
            for name in sorted(names):
                # ALB: a fix for a problem with the new 'with'
                # statement. It seems to work, but I don't know exactly
                # why... (the problem was in self.getval called by
                # info_locals)
                if _with_local_varname.match(name):
                    val = frame.f_locals[name]
                else:
                    err = False
                    try:
                        val = frame.f_locals[name]
                    except:
                        err = True
                    if err:
                        val = self.proc.getval(name)
                    pass
                Mpp.pp(
                    val,
                    self.settings["width"],
                    self.msg_nocr,
                    self.msg,
                    prefix="%s =" % name,
                )
                pass
            pass
        else:
            for name in args:
                # ALB: a fix for a problem with the new 'with'
                # statement. It seems to work, but I don't know exactly
                # why... (the problem was in self.getval called by
                # info_locals)
                if name in names:
                    if _with_local_varname.match(name):
                        val = frame.f_locals[name]
                    else:
                        val = self.proc.getval(name)
                        pass
                    Mpp.pp(
                        val,
                        self.settings["width"],
                        self.msg_nocr,
                        self.msg,
                        prefix="%s =" % name,
                    )
                else:
                    self.errmsg("%s is not a local variable" % name)
                    pass
        return False

    pass

    def print_locals_in_all_frames(self, args, curframe, limit=None):
        count = 0  # Initialize a counter to limit frames

        frame = curframe
        while frame is not None and (limit is None or count < limit):
            # Print the function name and locals for the current frame
            print('[[[FrameEntry]]]')
            print(f"[[[FrameIndex]]] {count} [[[/FrameIndex]]]")
            # print(f"[[[FrameId]]] {id(frame)} [[[/FrameId]]]")
            print('[[[Locals]]]')
            try:
                self.run_frame(args, frame)
            except Exception as e:
                pass
                # print('[[[Errror]]]')
                # print('[[[ExceptionMessage]]]')
                # print(f"Exception message: {e}")
                # print('[[[/ExceptionMessage]]]')
                # print('[[[ExceptionType]]]')
                # print(f"{type(e).__name__}")
                # print('[[[/ExceptionType]]]')
                # print('[[[Traceback]]]')
                # traceback.print_exc()  # This prints the full traceback
                # print('[[[/Traceback]]]')
                # print('[[[/Errror]]]')
            print('[[[/Locals]]]')
            print('[[[/FrameEntry]]]')

            # Move to the previous frame
            frame = frame.f_back
            count += 1

    def run(self, args, limit=0):
        self.print_locals_in_all_frames(args, self.proc.curframe, limit)


if __name__ == "__main__":
    from trepan.processor.command import mock, info as Minfo
    from trepan import debugger as Mdebugger

    d = Mdebugger.Trepan()
    d, cp = mock.dbg_setup(d)
    i = Minfo.InfoCommand(cp)
    sub = InfoLocals(i)
    import inspect

    cp.curframe = inspect.currentframe()
    sub.run([])
    sub.run(["*"])
    sub.run(["Minfo"])
    pass
