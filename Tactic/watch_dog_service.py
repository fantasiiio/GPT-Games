import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import psutil
import time
import sys

class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'MyService'
    _svc_display_name_ = 'My Service to Monitor Python Script'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        
        while True:
            script_running = False
            for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Check if 'your_script.py' is in the cmdline
                    if "your_script.py" in ' '.join(process.info['cmdline']):
                        script_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if not script_running:
                # If script is not running, start it
                subprocess.Popen(["python", "path/to/your_script.py"])

            time.sleep(5)  # Wait for 5 seconds before checking again

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyService)
