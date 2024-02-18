# -*- coding: utf-8 -*-
"""
A QSetting Subclass with signals.

@author: kolja
"""

from PyQt5.QtCore import QSettings, pyqtSignal


class SettingsManager(QSettings):
    value_removed = pyqtSignal(str)
    value_changed = pyqtSignal(str, object)    
    synced = pyqtSignal()
    
    def remove(self, key):
        self.value_removed.emit(key)
        super().remove(key)
    
    def setValue(self, key, value):
        self.value_changed.emit(key, value)
        super().setValue(key, value)
        
    def sync(self):
        self.synced.emit()
        super().sync()
        

def show_signal(key, val):
    print("changed:", key, val)
def show_signal2(key):
    print("removed:", key)
def show_signal3():
    print("synced")
    
# p = QSettings("./test.ini", QSettings.IniFormat)
p = QSettings("k.wagner", "configwidgets")
p.clear()

q = SettingsManager("k.wagner", "configwidgets")
# q = SettingsManager("./test.ini", QSettings.IniFormat)
q.value_changed.connect(show_signal)
q.value_removed.connect(show_signal2)
q.synced.connect(show_signal3)

# p.sync()
q.setValue("test1",123)
q.setValue("test2",111)
q.remove("test2")

p.setValue("test3", 123)

print("final")
for x in (p, q):
    print(type(x))
    print(f'{x.value("test1")=}')
    print("all keys", x.allKeys())

p.fileName()