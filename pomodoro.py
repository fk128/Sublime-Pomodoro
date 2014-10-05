import sublime
import sublime_plugin
import threading
import functools
import time

timeRecorder_thread = None

def settings():
  return sublime.load_settings('pomodoro.sublime-settings')

def drawProgressbar(totalSize, currPos, charStartBar, charEndBar, charBackground, charPos):
    s = charStartBar
    for c in range(1, currPos - 1):
        s = s + charBackground
    s = s + charPos
    for c in range(currPos, totalSize):
        s = s + charBackground
    s = s + charEndBar
    return s


def updateWorkingTimeStatus(totMins, leftMins):
    sublime.status_message('Pomodoro time remaining: ' + str(leftMins) + 'mins ' + drawProgressbar(totMins, totMins - leftMins + 1, '[', ']', '-', 'O'))


def updateRestingTimeStatus(totMins, leftMins):
    sublime.status_message('Break time remaining: ' + str(leftMins) + 'mins ' + drawProgressbar(totMins, totMins - leftMins + 1, '[', ']', '-', 'O'))


class TimeRecorder(threading.Thread):
    def __init__(self, view):
        super(TimeRecorder, self).__init__()
        self.view = view
        self.workingMins = (settings().get("pomodoro_mins"))
        self.shortBreakMins = (settings().get("shortbreak_mins"))
        self.longBreakMins = (settings().get("longbreak_mins"))
        self.numberPomodoro = (settings().get("number_pomodoro"))
        self.stopFlag = False
        self.pomodoroCounter = 0

    def recording(self, runningMins, displayCallback):
        leftMins = runningMins
        while leftMins > 1 and not self.stopped():
            for i in range(1, 60):
                sublime.set_timeout(functools.partial(displayCallback, runningMins, leftMins), 10)
                time.sleep(1)
                if self.stopped():
                    break           
            leftMins = leftMins - 1

        if leftMins <= 1 and not self.stopped():
            for i in range(1, 12):     
                sublime.set_timeout(functools.partial(displayCallback, runningMins, leftMins), 10)
                time.sleep(5)
                if self.stopped():
                    break
            leftMins = leftMins - 1

    def run(self):
        while 1:
            self.recording(self.workingMins, updateWorkingTimeStatus)
            self.pomodoroCounter = self.pomodoroCounter + 1

            if self.stopped(): 
                sublime.error_message('Pomodoro Cancelled')
                break

            breakType =  self.pomodoroCounter % (self.numberPomodoro)
            print(breakType)
            if breakType == 0:
                
                rest = sublime.ok_cancel_dialog('Time for a long break.', 'OK')
            else:
                rest = sublime.ok_cancel_dialog('Time for a short break.', 'OK')
            if rest:
                if breakType == 0:
                    self.recording(self.longBreakMins, updateRestingTimeStatus)
                else:
                    self.recording(self.shortBreakMins, updateRestingTimeStatus)
                work = sublime.ok_cancel_dialog("Break over. Start next pomodoro?", 'OK')
            if not work:
                self.stop()

        time.sleep(2)
        self.stop()

    def stop(self):
        self.stopFlag = True

    def stopped(self):
        return self.stopFlag



class PomodoroStartCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        self.window = sublime.active_window()
        self.view = self.window.active_view()
        global timeRecorder_thread
        if (timeRecorder_thread is None): 
            timeRecorder_thread = TimeRecorder(self.view)
            timeRecorder_thread.start()
        else:
            if (timeRecorder_thread.stopped()):
                timeRecorder_thread.join()
                timeRecorder_thread = TimeRecorder(self.view)
                timeRecorder_thread.start()

class PomodoroCancelCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        global timeRecorder_thread
        cancel = sublime.ok_cancel_dialog('Are you sure you want to cancel?', 'Yes')
        if cancel:
            timeRecorder_thread.stop()


