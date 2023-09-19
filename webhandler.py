import requests
import logging
import sys
from datetime import datetime, timedelta

class WebsiteHandler():
    def __init__(self,url,fc,active,ver):
        self.url = url
        self.myFC = fc
        self.active = active
        self.ver = ver
        self.ErrorCount = 0
        self.TotalErrors = 0
        
    def IsConnected(self):
        return self.ErrorCount == 0

    def SetActive(self,active):
        self.active = active
    def _ServerError(self):
        self.ErrorCount += 1
        self.TotalErrors += 1
    def _ServerSuccess(self):
        self.ErrorCount=0

    def BottersOnlineCount(self):
        # movableq does not have a botters online count at this time
        return 1
        # try:
        #     botter_list = requests.get(self.url+"/botters.php")
        #     if botter_list.status_code == 200:
        #         self._ServerSuccess
        #         try:
        #             return int(botter_list.text.split("\n")[0])
        #         except ValueError:
        #             return 0
        #     else:
        #         logging.warning("Server responded with HTTP code %s",botter_list.status_code)
        # except Exception as e:
        #     logging.error("Exception found: %s\n%s\n%s\n%s",e,sys.exc_info()[0].__name__, sys.exc_info()[2].tb_frame.f_code.co_filename, sys.exc_info()[2].tb_lineno)
        # self._ServerError()
        # return 0


    # def getClaimedList(self):
    #     try:
    #         fc_req = requests.get(self.url+"/request_job", params={'name': self.myFC, 'version': self.ver, 'types': ['fc']})
    #         if fc_req.status_code == 200:
    #             if not fc_req.text.startswith('error') and not fc_req.text.startswith('nothing'):
    #                 fc_list = [x for x in fc_req.text.split("\n") if len(x)==12]
    #                 return fc_list
    #             else:
    #                 return []
    #         else:
    #             logging.warning("Server responded with HTTP code %s",fc_req.status_code)
    #     except:
    #         self._ServerError()
    #     return []

    def getNewList(self):
        try:
            fc_req = requests.get(self.url+"/api/request_job", params={'name': self.myFC, 'active': self.active,
                                                                       'version': self.ver, "types": "fc"})
            if fc_req.status_code == 200:
                self._ServerSuccess()
                req_data = fc_req.json()["data"]
                if req_data:
                    fc_list = [req_data["friend_code"]]
                    return fc_list
            else:
                logging.warning("Server responded with HTTP code %s",fc_req.status_code)
                print("[",datetime.now(),"] WebHandler: Generic Connection error",fc_req.status_code)
                self._ServerError()
        except:
            self._ServerError()
        return []

    def UpdateLFCS(self,fc, lfcs: bytes):
        try:
            lfcs_req = requests.post(self.url+f"/api/complete_job/{fc}", json={"format": "hex", "result": lfcs.hex()})
            if lfcs_req.status_code == 200:
                self._ServerSuccess()
                return True
            elif lfcs_req.status_code == 500:
                if "KeyError" in lfcs_req.json()["message"]:
                    logging.warning("WebHandler: KeyError on LFCS upload, assuming already %s uploaded", fc)
                    print("[",datetime.now(),"] WebHandler: KeyError on LFCS upload, assuming already uploaded")
                    self._ServerSuccess()
                    return True
                # intentional fall-through for other error 500s
            logging.warning("Server responded with HTTP code %s",lfcs_req.status_code)
            logging.warning("Server response: %s",lfcs_req.text)
            print("[",datetime.now(),"] WebHandler: Generic Connection error",lfcs_req.status_code)
            print("[",datetime.now(),"] Server response:",lfcs_req.text)
            self._ServerError()
        except Exception as e:
            print("[",datetime.now(),"] Got exception!!", e,"\n",sys.exc_info()[0].__name__, sys.exc_info()[2].tb_frame.f_code.co_filename, sys.exc_info()[2].tb_lineno)
            logging.error("Exception found: %s\n%s\n%s\n%s",e,sys.exc_info()[0].__name__, sys.exc_info()[2].tb_frame.f_code.co_filename, sys.exc_info()[2].tb_lineno)
            self._ServerError()
        return False

    def TimeoutFC(self,fc):
        timeout_req = requests.get(self.url+f"/fail_job/{fc}", json={"name": self.myFC, "note": "Failed to add friendbot within timeout period"})
        if timeout_req.status_code == 200:
            self._ServerSuccess()
            return True
        else:
            logging.warning("Server responded with HTTP code %s",timeout_req.status_code)
            print("[",datetime.now(),"] WebHandler: Generic Connection error",timeout_req.status_code)
            self._ServerError()
        return False

    # not necessary as requesting a job claims it automatically
    # def ClaimFC(self,fc):
    #     resp = requests.get(self.url+"/claimfc.php",params={'fc':fc,'me':self.myFC})
    #     if resp.status_code == 200:
    #         self._ServerSuccess()
    #         if resp.text.startswith('success'):
    #             return True
    #     else:
    #         logging.warning("Server responded with HTTP code %s",resp.status_code)
    #         print("[",datetime.now(),"] Generic Connection issue:",resp.status_code)
    #         self._ServerError()
    #     return False

    def CancelFC(self, fc):
        reset_req = requests.get(self.url + f"/api/cancel_job/{fc}", params={'name': self.myFC})
        if reset_req.status_code == 200:
            self._ServerSuccess()
            return True
        else:
            logging.warning("Server responded with HTTP code %s", reset_req.status_code)
            print("[", datetime.now(), "] WebHandler: Generic Connection error", reset_req.status_code)
            self._ServerError()
        return False
    def ResetFC(self, fc):
        if not self.CancelFC(fc):
            return False
        reset_req = requests.get(self.url+f"/api/reset_job/{fc}", params={'name': self.myFC})
        if reset_req.status_code == 200:
            self._ServerSuccess()
            return True
        else:
            logging.warning("Server responded with HTTP code %s",reset_req.status_code)
            print("[",datetime.now(),"] WebHandler: Generic Connection error",reset_req.status_code)
            self._ServerError()
        return False
    def GetBotSettings(self):
        return False,True
    def ResetBotSettings(self):
        return True
