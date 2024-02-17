from abc import abstractmethod
import os
import threading
from icetcore.quote import QuoteClass,QuoteEventMeta
from icetcore.trade import TradeClass,TradeEventMeta
from icetcore.constant import BarType,GreeksType,OrderStruct
from datetime import datetime,timedelta
import time
import json
import logging
from ctypes import windll
from comtypes.messageloop import run

class QuoteEvent(QuoteEventMeta):
    def __init__(self) -> None:
        super().__init__()
    @abstractmethod
    def onconnected(self,apitype:str):
        pass
    @abstractmethod
    def ondisconnected(self,apitype:str):
        pass

    def onsystemmessage(self,MsgType, MsgCode, MsgString):
        pass
    def onbar(self,datatype,interval,symbol,data:list,isreal:bool):
        pass
    def ongreeksreal(self,datatype,symbol,data:dict):
        pass
    def ongreeksline(self,datatype,interval,symbol,data,isreal):
        pass
    def onquote(self,data):
        pass
    def onATM(self,datatype,symbol,data:dict):
        pass
    def onservertime(self, serverdt):
        pass
    def getATM(self,symbol:str,atmindex:int):
        if "TC.O" in symbol:
            _symbl=symbol.split(".")
        else:
            print("合约代码格式错误:必须是TC.O.交易所.合约.月份，例如:TC.O.SSE.510050.202211")
        atmkey="TC.O."+_symbl[2]+"."+ _symbl[3]+"."+ _symbl[4]+".GET.ATM"
        if atmkey in self._tcoreapi.quoteobj.eventobj.atm.keys():
            atmdata=self._tcoreapi.quoteobj.eventobj.atm[atmkey]
            if not atmdata:
                return
            result=""
            atmsymbol=""
            _callsymbol=atmdata["OPTLIST"]
            _putsymbol=[i.replace(".C.",".P.") for i in atmdata["OPTLIST"]]

            cidx=_callsymbol.index(atmdata["OTM-1C"])
            pidx=_putsymbol.index(atmdata["OTM-1P"])
            if atmindex==0:
                atmsymbol=atmdata["OTM-1C"] if atmdata["ATM"] in atmdata["OTM-1C"] else atmdata["OTM-1P"]
                if ".P" in symbol and ".P" not in atmsymbol:
                    result=atmsymbol.replace(".C.",".P.")
                else:
                    result=atmsymbol
            else:
                if ".P" in symbol:
                    result=_putsymbol[pidx-atmindex+1]
                else:
                    result=_callsymbol[cidx+atmindex-1]
            
            return result
        else:
            self._tcoreapi.subATM(symbol)
            return

class TradeEvent(TradeEventMeta):
    def __init__(self) -> None:
        super().__init__()
    @abstractmethod
    def onconnected(self, strapi):
        pass
    @abstractmethod
    def ondisconnected(self, strapi):
        pass
    def onsystemmessage(self,MsgType, MsgCode, MsgString):
        pass
    def onaccountlist(self,data,count):
        pass
    def onordereportreal(self,data):
        pass
    def onfilledreportreal(self,data):
        pass
    def onorderreportreset(self):
        pass
    def onpositionmoniter(self,data):
        pass
    def onmargin(self,accmask,data):
        pass
    def onposition(self,accmask,data):
        pass
    def oncombposition(self,accmask,data):
        pass
    def oncombinationorder(self,accmask,data):
        pass
class TCoreAPI():
    def __init__(self,apppath,eventclass=None,logpath="") -> None:
        self.__currpath=os.getcwd()
        self.win32event=windll.kernel32
        self.subquotetopic=[]
        self.subgreekstopic=[]
        self.tradeobj=None
        self.quoteobj=None
        if eventclass:
            if isinstance(eventclass,type):
                self.eventcls=eventclass()
            else:
                self.eventcls=eventclass
        else:
            self.eventcls=None
        apppath.rstrip("\\")
        apppath.rstrip("/")

        if issubclass(type(self.eventcls),TradeEvent):
            self.tradeobj=TradeClass(self.eventcls,apppath)
        else:
            self.tradeobj=TradeClass(None,apppath)
        if issubclass(type(self.eventcls),QuoteEvent):
            self.quoteobj=QuoteClass(self.eventcls,apppath)
        else:
            self.quoteobj=QuoteClass(None,apppath)
        self.apipath=apppath
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level = logging.INFO)
        if logpath:
            handler = logging.FileHandler(logpath)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log(self,message):
        if self.logger:
            self.logger.info(message)

    #连线
    def connect(self,appid="",servicekey="8076c9867a372d2a9a814ae710c256e2"):
        path=self.apipath+"/TCoreRelease/ComShared/SystemSettings.ini"
        with open(path,encoding="utf-8") as file:
            for line in file.readlines():
                if "SystemName=" in line:
                    appid=line.replace("SystemName=","").strip()
                    break
        threading.Thread(target=self.quoteobj.connect,args=(appid,servicekey,)).start()
        threading.Thread(target=self.tradeobj.connect,args=(appid,servicekey,)).start()
        time.sleep(1)
        os.chdir(self.__currpath)
        if self.eventcls:
            self.eventcls._tcoreapi=self
        tre=self.win32event.WaitForSingleObject(self.tradeobj.eventobj.cmsgevent, 2000)
        qre=self.win32event.WaitForSingleObject(self.quoteobj.eventobj.cmsgevent, 2000)
        if 0!=tre:
            print("交易接口认证失败")
            self.tradeobj=None
        if 0!=qre:
            print("行情接口认证失败")
            self.quoteobj=None

    #断开连线
    def disconnect(self):
        if self.tradeobj:
            self.tradeobj.disconnect()
        if self.quoteobj:
            self.quoteobj.disconnect()

    #下单
    def neworder(self,ordarg:OrderStruct):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        ordkey,msg=self.tradeobj.neworder(ordarg)
        return ordkey,msg
    #获取新增委托单最新信息和状态
    def getorderinfo(self,ordkey:str):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.getorderinfo(ordkey)
    #改单
    def replaceorder(self,reportid:str,orderqty=None,price=None,stopprice=None):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.replaceorder(reportid,orderqty,price,stopprice)
    #取消委托单
    def cancelorder(self, reportid:str,strkey=""):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.cancelorder(reportid,strkey)
    #取消价差单
    def cancelspreadorder(self,  reportid:str):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.cancelspreadorder(reportid)
    #修改委托单状态
    def changeorderaction(self,  reportid:str, laction):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.changeorderaction(reportid, laction)
    #新增Vanna策略委托
    def newstrategyorder(self,newstrategyorder:dict):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.newstrategyorder(newstrategyorder)
    #期权持仓组合
    def optcomb(self,strAcctMask,SymbolA,SymbolB,Volume:int,CombinationType:int,CombID=""):#strParam &SIDEA=2&SIDEB=2
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.optcomb(strAcctMask,SymbolA,SymbolB,Volume,CombinationType,CombID)
    #期权组合持仓拆分
    def optcombsplit(self,strAcctMask,Symbol:str,Volume:int,CombinationType:int,CombID=""):#strParam &SIDEA=2&SIDEB=2
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.optcombsplit(strAcctMask,Symbol,Volume,CombinationType,CombID)
    #获取已登入账户列表
    def getaccountlist(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        temp=[]
        for i in range(self.tradeobj.eventobj.accountcout):
            temp.append(self.tradeobj.getaccoutlist(i))
        return temp

    #获取指定账户的资金信息
    def getaccmargin(self,accmask:str,basecurrency=True):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        temp=[]
        if accmask in self.tradeobj.eventobj.margincout:
            for i in range(self.tradeobj.eventobj.margincout[accmask]):
                    margin=self.tradeobj.getaccmargin(i,accmask)
                    if basecurrency:
                        if margin['CurrencyToClient']=='BaseCurrency':
                            temp.append(margin)
                    else:
                        temp.append(margin)
        return temp
    #订阅资金信息更新
    def submargin(self,basecurrency=True):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        self.tradeobj.eventobj.isbasecurrency=basecurrency
        self.tradeobj.eventobj.issubmargin=True
    #解订资金信息更新
    def unsubmargin(self):
        self.tradeobj.eventobj.issubmargin=False
    #获取指定子账户的持仓信息
    def getposition(self,accmask:str):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        temp=[]
        if accmask in self.tradeobj.eventobj.positioncout:
            for i in range(self.tradeobj.eventobj.positioncout[accmask]):
                temp.append(self.tradeobj.getposition(i,accmask))
        return temp
    #订阅持仓信息更新
    def subposition(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        self.tradeobj.eventobj.issubposition=True
        
    #解订持仓信息更新
    def unsubposition(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        self.tradeobj.eventobj.issubposition=False
    #获取指定账户的组合持仓
    def getcombposition(self,accmask:str):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        temp=[]
        if accmask in self.tradeobj.eventobj.combpositioncout:
            for i in range(self.tradeobj.eventobj.combpositioncout[accmask]):
                combp=self.tradeobj.getcombposition(i,accmask)
                if combp:
                    temp.append(combp)
        return temp
    #订阅组合持仓信息更新
    def subcombposition(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        self.tradeobj.eventobj.issubcombposition=True
    #解订组合持仓信息更新
    def unsubcombposition(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        self.tradeobj.eventobj.issubcombposition=False
    #获取指定账户的组合报单记录
    def getcombinationorder(self,accmask:str):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        temp=[]
        if accmask in self.tradeobj.eventobj.combordercout:
            for i in range(self.tradeobj.eventobj.combordercout[accmask]):
                self.tradeobj.getcombinationorder(i,accmask)
        return temp
    #订阅期权持仓监控
    def subpositionmoniter(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        self.tradeobj.eventobj.issubpositionmoniter=True
    #解订期权持仓监控
    def unsubpositionmoniter(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        self.tradeobj.eventobj.issubpositionmoniter=False
    #获取期权持仓监控
    def getpositionmoniter(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.getpositionmoniter()
    #获取当前未成交委托
    def getactiveorder(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.getactiveorder()
    #获取当日所有委托单
    def getorderreport(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.getorderreport()
    #获取当日所有成交委托
    def getfilledreport(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.getfilledreport()
    #获取当日所有成交委托明细
    def getdetailfilledreport(self):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return
        return self.tradeobj.getdetailfilledreport()
    #根据内部报单编号获取对应的委托单信息
    def getreportbyid(self,reportid:str):
        if not self.tradeobj:
            print("请交易接口认证成功后，再使用该功能")
            return 
        return self.tradeobj.getreportbyid(reportid)
    #订阅动态K线数据
    def subbar(self,btype:BarType,interval:int,symbol:str,starttime:str,isinterval=True):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        try:
            datetime.strptime(starttime,'%Y%m%d%H')
            #datetime.strptime(endtime,'%Y%m%d%H')
        except:
            print("日期时间格式错误，请输入格式为‘yyyyMMddHH’")
            return
        endtime=datetime.strftime(datetime.now()+timedelta(days=4),'%Y%m%d%H')
        if btype==5:
            endtime=datetime.strftime(datetime.now()+timedelta(days=4),'%Y%m%d%H')
        else:
            endtime=datetime.strftime(datetime.now()-timedelta(hours=7),'%Y%m%d%H')
        self.quoteobj.eventobj.update_asinterval[symbol+"-"+str(btype)+"-"+str(interval)]=isinterval
        self.quoteobj.eventobj.bardatatopic.append(symbol)
        self.quoteobj.eventobj.bardata[symbol+"-"+str(btype)+"-"+str(interval)]=None
        #if symbol+"-"+str(btype) not in self.quoteobj.eventobj.barinterval.keys():
        if  symbol not in self.subquotetopic:
            self.quoteobj.subquote(1,symbol,0,0)
            self.subquotetopic.append(symbol)
        threading.Thread(target=self.quoteobj.subquote,args=(btype,symbol,int(starttime),int(endtime),)).start()
        if symbol+"-"+str(btype) in self.quoteobj.eventobj.barinterval.keys():
            self.quoteobj.eventobj.barinterval[symbol+"-"+str(btype)].add(interval)
        else:
            self.quoteobj.eventobj.barinterval[symbol+"-"+str(btype)]={interval}
        return self.quoteobj.eventobj.barinterval[symbol+"-"+str(btype)]

    #解订K线数据
    def unsubbar(self,btype:BarType,interval:int,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        del self.quoteobj.eventobj.bardata[symbol+"-"+str(btype)+"-"+str(interval)]
        self.quoteobj.unsubquote(1,symbol,0,0)
        self.subquotetopic.remove(symbol)
    #订阅实时行情
    def subquote(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if  symbol in self.subquotetopic:
            return
        self.subquotetopic.append(symbol)
        return self.quoteobj.subquote(1,symbol,0,0)
    #解订实时行情
    def unsubquote(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        self.subquotetopic.remove(symbol)
        return self.quoteobj.unsubquote(1,symbol,0,0)
    #获取历史行情数据    
    def getquotehistory(self,btype:BarType,interval:int,symbol:str,starttime:str,endtime=datetime.strftime(datetime.now()-timedelta(hours=7),'%Y%m%d%H')):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        try:
            datetime.strptime(starttime,'%Y%m%d%H')
            datetime.strptime(endtime,'%Y%m%d%H')
        except:
            print("日期时间格式错误，请输入格式为‘yyyyMMddHH’")
            return
        if symbol+"-"+str(btype) in self.quoteobj.eventobj.barinterval.keys():
            self.quoteobj.eventobj.barinterval[symbol+"-"+str(btype)].add(interval)
        else:
            self.quoteobj.eventobj.barinterval[symbol+"-"+str(btype)]={interval}
        self.quoteobj.eventobj.quotehistory[symbol+"-"+str(btype)+str(interval)+":"+starttime+"~"+str(endtime)]=None
        threading.Thread(target=self.quoteobj.subquote,args=(btype,symbol,int(starttime),int(endtime),)).start()
        self.win32event.ResetEvent(self.quoteobj.eventobj.quotehistoryevent)
        qre=self.win32event.WaitForSingleObject(self.quoteobj.eventobj.quotehistoryevent, 50000)
        quotehistory=self.quoteobj.eventobj.quotehistory[symbol+"-"+str(btype)+str(interval)+":"+starttime+"~"+str(endtime)]
        #self.quoteobj.eventobj.barinterval[symbol+"-"+str(btype)].remove(interval)
        del self.quoteobj.eventobj.quotehistory[symbol+"-"+str(btype)+str(interval)+":"+starttime+"~"+str(endtime)]
        if 0==qre and quotehistory:
            return quotehistory
        else:
            return

    #订阅动态greekline数据
    def subgreeksline(self,linetype:GreeksType,interval:int,symbol:str,starttime:str,isinterval=True):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        try:
            datetime.strptime(starttime,'%Y%m%d%H')
        except:
            print("日期时间格式错误，请输入格式为‘yyyyMMddHH’")
            return
        endtime=datetime.strftime(datetime.now()+timedelta(days=4),'%Y%m%d%H')
        if linetype==19:
            endtime=datetime.strftime(datetime.now()+timedelta(days=4),'%Y%m%d%H')
        else:
            endtime=datetime.strftime(datetime.now()-timedelta(hours=7),'%Y%m%d%H')
        self.quoteobj.eventobj.update_asinterval[symbol+"-"+str(linetype)+"-"+str(interval)]=isinterval
        self.quoteobj.eventobj.greekslinetopic.append(symbol)
        self.quoteobj.eventobj.linedata[symbol+"-"+str(linetype)+"-"+str(interval)]=None
        #if symbol+"-"+str(btype) not in self.quoteobj.eventobj.barinterval.keys():
        if "TC.O" in symbol:
            arrsymb=symbol.split(".")
            if "SSE" in symbol or "SZSE" in symbol:
                usymbol="TC.S."+arrsymb[2]+"."+arrsymb[3].strip("A")
                ufsymbol="TC.F.U_"+arrsymb[2]+"."+arrsymb[3].strip("A")+"."+arrsymb[4] 
            elif "IO" in symbol:
                usymbol="TC.S.SSE.000300"
                ufsymbol="TC.F.U_"+arrsymb[2]+"."+arrsymb[3]+"."+arrsymb[4]
            elif "HO" in symbol:
                usymbol="TC.S.SSE.000016"
                ufsymbol="TC.F.U_"+arrsymb[2]+"."+arrsymb[3]+"."+arrsymb[4]
            elif "MO" in symbol:
                usymbol="TC.S.SSE.000852"
                ufsymbol="TC.F.U_"+arrsymb[2]+"."+arrsymb[3]+"."+arrsymb[4]
            else:
                usymbol="TC.F."+arrsymb[2]+"."+arrsymb[3]+"."+arrsymb[4]
                ufsymbol="TC.F.U_"+arrsymb[2]+"."+arrsymb[3]+"."+arrsymb[4]
            if usymbol not in self.subquotetopic:
                self.quoteobj.subquote(1,usymbol,0,0)
                self.subquotetopic.append(usymbol)
            if ufsymbol not in self.subquotetopic:
                self.quoteobj.subquote(1,ufsymbol,0,0)
                self.subquotetopic.append(ufsymbol)
        if symbol not in self.subquotetopic:
            self.quoteobj.subquote(1,symbol,0,0)
            self.subquotetopic.append(symbol)
        if symbol not in self.subgreekstopic:
            self.quoteobj.subquote(6,symbol,0,0)
            self.subgreekstopic.append(symbol)
        threading.Thread(target=self.quoteobj.subquote,args=(linetype,symbol,int(starttime),int(endtime),)).start()
        if symbol+"-"+str(linetype) in self.quoteobj.eventobj.lineinterval.keys():
            self.quoteobj.eventobj.lineinterval[symbol+"-"+str(linetype)].add(interval)
        else:
            self.quoteobj.eventobj.lineinterval[symbol+"-"+str(linetype)]={interval}
        return self.quoteobj.eventobj.lineinterval[symbol+"-"+str(linetype)]
    #订阅实时greek
    def subgreeksreal(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if symbol in self.subgreekstopic:
            return
        self.subgreekstopic.append(symbol)
        return self.quoteobj.subquote(6,symbol,0,0)
    #解订实时greek
    def unsubgreeksreal(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        self.subgreekstopic.remove(symbol)
        return self.quoteobj.unsubquote(6,symbol,0,0)
    #获取历史greeks数据
    def getgreekshistory(self,datatype:GreeksType,interval:int,symbol:str,starttime:str,endtime=datetime.strftime(datetime.now()-timedelta(hours=7),'%Y%m%d%H')):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        try:
            datetime.strptime(starttime,'%Y%m%d%H')
            datetime.strptime(endtime,'%Y%m%d%H')
        except:
            print("日期时间格式错误，请输入格式为‘yyyyMMddHH’")
            return
        if symbol+"-"+str(datatype) in self.quoteobj.eventobj.lineinterval.keys():
            self.quoteobj.eventobj.lineinterval[symbol+"-"+str(datatype)].add(interval)
        else:
            self.quoteobj.eventobj.lineinterval[symbol+"-"+str(datatype)]={interval}
        self.quoteobj.eventobj.greekshistory[symbol+"-"+str(datatype)+str(interval)+":"+str(starttime)+"~"+str(endtime)]=None
        threading.Thread(target=self.quoteobj.subquote,args=(datatype,symbol,int(starttime),int(endtime),)).start()
        self.win32event.ResetEvent(self.quoteobj.eventobj.greekshistoryevent)
        qre=self.win32event.WaitForSingleObject(self.quoteobj.eventobj.greekshistoryevent, 50000)

        greekshistory=self.quoteobj.eventobj.greekshistory[symbol+"-"+str(datatype)+str(interval)+":"+str(starttime)+"~"+str(endtime)]
        #self.quoteobj.eventobj.lineinterval[symbol+"-"+str(datatype)].remove(interval)
        del self.quoteobj.eventobj.greekshistory[symbol+"-"+str(datatype)+str(interval)+":"+str(starttime)+"~"+str(endtime)]
        if 0==qre and greekshistory:
            return greekshistory
        else:
            return None
    #订阅ATM合约
    def subATM(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        #TC.O.SSE.510050.202211.GET.ATM
        if "TC.O" in symbol:
            _symbl=symbol.split(".")
        else:
            print("合约代码格式错误:必须是TC.O.交易所.合约.月份，例如:TC.O.SSE.510050.202211")
            return
        atmsymbol="TC.O."+_symbl[2]+"."+ _symbl[3]+"."+ _symbl[4]+".GET.ATM"
        self.quoteobj.eventobj.atm[atmsymbol]=None
        if  atmsymbol in self.subquotetopic:
            return
        self.subquotetopic.append(atmsymbol)
        self.quoteobj.subquote(1,atmsymbol,0,0)

    #解订ATM合约
    def unsubATM(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if "TC.O" in symbol:
            _symbl=symbol.split(".")
            atmsymbol="TC.O."+_symbl[2]+"."+ _symbl[3]+"."+ _symbl[4]+".GET.ATM"
            self.subquotetopic.remove(atmsymbol)
            self.quoteobj.unsubquote(1,atmsymbol,0,0)
        else:
            print("合约代码格式错误，‘TC.O.’开头的期权合约可用")
    #获取ATM
        # -2:实值两档期权合约
        # -1:实值一档期权合约
        #  0:平值期权合约
        #  1:虚值期权合约        
    def getATM(self,symbol:str,atmindex:int):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if "TC.O" in symbol:
            _symbl=symbol.split(".")
        else:
            print("合约代码格式错误:必须是TC.O.交易所.合约.月份，例如:TC.O.SSE.510050.202211")
        atmsymbol="TC.O."+_symbl[2]+"."+ _symbl[3]+"."+ _symbl[4]+".GET.ATM"
        self.quoteobj.eventobj.atm[atmsymbol]=None
        threading.Thread(target=self.quoteobj.subquote,args=(1,atmsymbol,0,0,)).start()
        self.win32event.ResetEvent(self.quoteobj.eventobj.greekshistoryevent)
        qre=self.win32event.WaitForSingleObject(self.quoteobj.eventobj.atmevent, 20000)
        atmdata=self.quoteobj.eventobj.atm[atmsymbol]
        if 0==qre and atmdata:
            del self.quoteobj.eventobj.atm[atmsymbol]
            self.quoteobj.unsubquote(1,atmsymbol,0,0)
            result=""
            atmsymbol=""
            _callsymbol=atmdata["OPTLIST"]
            _putsymbol=[i.replace(".C.",".P.") for i in atmdata["OPTLIST"]]

            cidx=_callsymbol.index(atmdata["OTM-1C"])
            pidx=_putsymbol.index(atmdata["OTM-1P"])
            if atmindex==0:
                atmsymbol=atmdata["OTM-1C"] if atmdata["ATM"] in atmdata["OTM-1C"] else atmdata["OTM-1P"]
                if ".P" in symbol and ".P" not in atmsymbol:
                    result=atmsymbol.replace(".C.",".P.")
                else:
                    result=atmsymbol
            else:
                if ".P" in symbol:
                    result=_putsymbol[pidx-atmindex+1]
                else:
                    result=_callsymbol[cidx+atmindex-1]
            
            return result
        else:
            del self.quoteobj.eventobj.atm[atmsymbol]
            self.quoteobj.unsubquote(1,atmsymbol,0,0)
            return
       
    #获取合约的到期日
    def getexpirationdate(self, symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        return self.quoteobj.getexpirationdate(symbol)
    #获取合约的剩余交易日
    def gettradeingdays(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        return self.quoteobj.gettradeingdays(symbol)
    #获取合约的指定日期段内的交易日列表
    def gettradeingdate(self,symbol:str,startDate,endDate)->list:
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        return json.loads(self.quoteobj.gettradeingdate(symbol,startDate,endDate))["TradingDate"]
    #获取热门月换月信息
    def gethotmonth(self, symbol:str, strdate="", strtime=""):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if self.quoteobj.eventobj.hotmonthready:
            return self.quoteobj.gethotmonth(symbol, strdate, strtime)
    #获取合约最小跳动
    def getsymbol_ticksize(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if self.quoteobj.eventobj.symbinfoready:
            return self.quoteobj.getsymbol_ticksize(symbol)
    #获取合约交易时段
    def getsymbol_session(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if self.quoteobj.eventobj.symbinfoready:
            return self.quoteobj.getsymbol_session(symbol)
    #获取合约乘数
    def getsymbolvolume_multiple(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if self.quoteobj.eventobj.symbinfoready:
            return self.quoteobj.getsymbolvolume_multiple(symbol)
    #获取合约的交易编码
    def getsymbol_id(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        return self.quoteobj.getsymbol_id(symbol)
    #获取合约所有信息
    def getsymbol_allinfo(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if self.quoteobj.eventobj.symbinfoready:
            return json.loads(self.quoteobj.getsymbol_allinfo(symbol))
    #获取合约名称描述
    def getsymbolname(self,symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        return self.quoteobj.getsymbolname(symbol)
    #获取当前最新所有合约，只包含合约，不包含合约信息
    ##当symboltype和exchange均不带入参数默认为空时，获取所有合约
    ##symboltype 指定合约类型:OPT/FUT/STK
    ##exchange   指定交易所
    def getallsymbol(self,symboltype="",exchange=""):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if self.quoteobj.eventobj.symbollistready:
            return self.quoteobj.getallsymbol(symboltype,exchange)
    #获取合成期货合约列表
    def get_u_futuresymbol(self):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if self.quoteobj.eventobj.symbollistready:
            return self.quoteobj.getsynu_futuresymbol()
    #获取历史合约和信息
    def getsymbolhistory(self,symboltype:str,dt:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        self.quoteobj.eventobj.symbolhistory[symboltype+"-"+dt]=None
        threading.Thread(target=self.quoteobj.subsymbolhistory,args=(symboltype,dt,)).start()
        self.win32event.ResetEvent(self.quoteobj.eventobj.symbolhistoryevent)
        qre=self.win32event.WaitForSingleObject(self.quoteobj.eventobj.symbolhistoryevent, 20000)
        symbolhistory=self.quoteobj.eventobj.symbolhistory[symboltype+"-"+dt]
        del self.quoteobj.eventobj.symbolhistory[symboltype+"-"+dt]
        if 0==qre:
            return symbolhistory
        else:
            return
    #模糊查找合约
    def symbollookup(self, findkey:str,symboltype=""):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        if self.quoteobj.eventobj.symblookready:
            symtype=0
            if symboltype=="":
                symtype=0
            elif symboltype=="STK":
                symtype=1
            elif symboltype=="FUT":
                symtype=2
            elif symboltype=="OPT":
                symtype=3
            strre=self.quoteobj.symbollookup(symtype, findkey).strip("|")
            searchresult=[]
            if strre:
                if "|" in strre:
                    for  symb in strre.split("|"):
                        if symb:
                            searchresult.append({symb.split(",")[0]:symb.split(",")[1]})
                    return searchresult
                elif "|" not in strre and "," in strre:
                    return [{strre.split(",")[0]:strre.split(",")[1]}]
            else:
                return None

    #指定时间，对应合约是否为假日
    def isholiday(self, bstrDate, symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        return self.quoteobj.isholiday(bstrDate,symbol)
    #指定合约是否为标的合约
    def isunderlying(self, symbol:str):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        return self.quoteobj.isunderlying(symbol)

    def join(self):
        run()
        #self.tradeobj.join()
    #设定使用自定义Greeks
    ##参数customtype:
    ###1:期权IV
    ###11:期权和期货IV
    ###10:期货IV
    def activecustomgreeks(self,customtype):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        self.quoteobj.topicpublish("GREEKSBYUSER", 0, "{\"Active\":\""+str(customtype)+"\"}", None)
    #停用自定义Greeks
    def unactivecustomgreeks(self):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        self.quoteobj.topicpublish("GREEKSBYUSER", 0, "{\"Active\":\"0\"}", None)
    #发送自定义iv
    def sendcustomIV(self,symbol,iv):
        if not self.quoteobj:
            print("请行情接口认证成功后，再使用该功能")
            return
        self.quoteobj.topicpublish("GREEKSBYUSER", 0, "{\"Data\":{\"s\":\""+symbol+"\",\"iv\":\""+"{:.4f}".format(iv)+"\"}}", None)