import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

import uvicorn

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "agent1c_metrics"
    _svc_display_name_ = "Agent 1C metrics service"
    _svc_port = 8144
    _svc_host = '0.0.0.0'
    _svc_reload = False

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        uvicorn.run("agent1c_metrics.viewer:app", port=self._svc_port, log_level="info", host=self._svc_host, reload=self._svc_reload)

def svc() -> None:
    """
    Manage windows service
    """
    AppServerSvc
    win32serviceutil.HandleCommandLine(AppServerSvc)

if __name__ == "__main__":
    svc()