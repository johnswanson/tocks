import dialog
import argparse
import os
import sys
import subprocess
import time
from tocks.beeminder import Beeminder


class App:
    IN_PROGRESS = 1
    NO_TOCK = 2
    name_file = os.path.expanduser('~/.current_pomodoro')
    touch_file = os.path.expanduser('~/.pomodoro_session')
    beeminder_auth_token_file = os.path.expanduser('~/.beeminder-auth')

    def __init__(self, args):
        self.args = args
        self.d = dialog.Dialog(dialog="dialog")
        with open(self.beeminder_auth_token_file) as f:
            self.beeminder_token = f.read()
        self.beeminder = Beeminder(auth_token=self.beeminder_token, username='jds02006')

    def _state(self):
        try:
            with open(self.name_file, 'r') as f:
                return (App.IN_PROGRESS, f.read())
        except Exception:
            return (App.NO_TOCK, None)

    def _abort(self):
        try:
            os.remove(self.name_file)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.touch_file)
        except FileNotFoundError:
            pass

    def abort(self, args):
        (state, name) = self._state()
        if state == App.IN_PROGRESS and self.d.yesno("Abort tock:\n\t{}".format(name), keep_tite=True) == self.d.DIALOG_OK:
            self._abort()
            return True
        else:
            return False

    def _done(self):
        r = self.beeminder.post_datapoint('tocks', 45, name)
        if r.status_code == 200:
            os.remove(self.name_file)

    def done(self, args):
        (state, name) = self._state()
        if state == App.IN_PROGRESS:
            if self.d.yesno("Tock finished?\n\t{}".format(name), keep_tite=True) == self.d.DIALOG_OK:
                self._done()
            if self.d.yesno("Take a break?", keep_tite=True) == self.d.DIALOG_OK:
                self._break()
        else:
            exit("No tock in progress!")

    def start(self, args):
        (state, name) = self._state()
        if state != App.IN_PROGRESS:
            if args.name:
                tock_name = ' '.join(args.name)
            else:
                (code, tock_name) = self.d.inputbox("Name of the tock:", init="job: ", keep_tite=True)
                if code in (self.d.DIALOG_CANCEL, self.d.DIALOG_ESC):
                    exit("Cancel")
            with open(self.name_file, 'w') as f:
                f.write(tock_name)
            with open(self.touch_file, 'w') as f:
                f.write('45 15')

    def _break(self, minutes):
        get = subprocess.check_output(["xrandr"]).decode('utf-8').split()
        screens = [ get[i-1] for i in range(len(get)) if get[i] == 'connected']
        for scr in screens:
            subprocess.call(["xrandr", "--output", scr, "--brightness", "0.5"])
        time.sleep(60 * minutes)
        for scr in screens:
            subprocess.call(["xrandr", "--output", scr, "--brightness", "1"])

    def takebreak(self, args):
        self.abort(args)
        (state, name) = self._state()
        if state != App.IN_PROGRESS:
            (code, result) = self.d.inputbox("How many minutes should this break be?", init="15", keep_tite=True)
            if code == self.d.DIALOG_OK:
                try:
                    minutes = int(result)
                    self._break(minutes)
                except ValueError:
                    exit("Invalid number of minutes: {}".format(result))

def main():
    parser = argparse.ArgumentParser(description='Tock script')
    parser.add_argument('command', choices=['abort', 'done', 'start', 'takebreak'])
    parser.add_argument('name', nargs='*')
    args = parser.parse_args(sys.argv[1:])
    a = App(args)
    getattr(a, args.command)(args)
