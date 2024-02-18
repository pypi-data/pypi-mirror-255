from threading import Timer, Thread, Event

class AutoStartTimer(object):
  def __init__(self, spam, callback):
    self._spam = spam
    self._callback = callback
    self._thread = Timer(self._spam, self.callback)
    self._thread.start()

  def callback(self):
    self._callback()
    self._thread = Timer(self._spam, self.callback)
    self._thread.start()

  def start(self):
    self._thread.start()

  def cancel(self):
    self._thread.cancel()
