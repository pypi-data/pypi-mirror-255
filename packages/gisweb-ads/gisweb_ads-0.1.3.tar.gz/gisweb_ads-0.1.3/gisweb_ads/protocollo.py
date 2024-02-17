
from ast import Dict
from typing import Any
from gisweb_ads.schema import IDocumento, IConfig, ILoginRet, IResult, IProtocollo
from gisweb_ads.soap_attachments import with_soap_attachment
from suds.client import Client
import logging
import os, base64, uuid
import json
from datetime import datetime
from pydantic import BaseModel
from jinja2 import Environment, PackageLoader, select_autoescape
import time

_logger = logging.getLogger('gisweb-ads')


env = Environment(
    loader=PackageLoader("gisweb_ads"),
    autoescape=select_autoescape()
)

class Protocollo:
    
    config:IConfig
    data:IProtocollo
    wsClient:Any
    DST:str | None
    wsError: IResult
  
    def __init__(self, config:IConfig, data:IProtocollo) -> None:
        self.data = data
        self.config = config
        self.DST = ''
        if self.config.FAKE:
            return
        
        try:
            self.wsClient = Client(config.wsUrl)
            result:ILoginRet = self.wsClient.service.login(config.wsEnte, config.wsUser, config.wsPassword)
            if result.lngErrNumber==0:
                self.DST=result.strDST
            else:
                self.wsError = IResult(strErrString=result.strErrString,lngErrNumber=result.lngErrNumber)

        except Exception as error:
            self.wsError = IResult(strErrString="ERRORE NELLA CONNESSIONE A WS",lngErrNumber=999)


    def __inserisciDocumento(self, documento:IDocumento) -> IDocumento | None:
        
        fName = documento.nome.encode('ascii','ignore')
        mime = documento.mimetype.encode('ascii','ignore')
        content = documento.content.read()
        result = with_soap_attachment(self.wsClient.service.inserimento, [content,fName,mime], self.config.wsUser, self.DST)

        try:
            fName = documento.nome.encode('ascii','ignore')
            mime = documento.mimetype.encode('ascii','ignore')
            content = documento.content.read()
            result = with_soap_attachment(self.wsClient.service.inserimento, [content,fName,mime], self.config.wsUser, self.DST)
        except Exception as error:
            _logger.info(error)
            return 

        if result.lngErrNumber != 0:
            _logger.info(result.strErrString)
            return
        
        dd = documento.dict()
        dd["id"] = result.lngDocID
        return IDocumento(**dd)
        

    def __getSegnatura(self):
        
        #inserisco allegato principale
        newDoc = self.__inserisciDocumento(self.data.Principale)
        if newDoc:
            self.data.Principale = newDoc
            
        #inserisco altri allegati
        allegati = []
        for documento in self.data.Allegati:
            newDoc = self.__inserisciDocumento(documento)
            if newDoc:
                allegati.append(newDoc)

        self.data.Allegati = allegati
            
        template = env.get_template("segnatura_e.xml")
        return template.render(self.data)


    def protocollaDocumento(self, messageData=None, testXml=False) -> IResult:
        
        if self.config.FAKE:
            time.sleep(15)
            return IResult(lngNumPG=444,lngAnnoPG=2023, strDataPG='01/01/2222',lngErrNumber=0,strErrString= '') 
        if self.config.FAKE_ERROR:
            time.sleep(15)
            return IResult(lngNumPG=0,lngAnnoPG=0, strDataPG='',lngErrNumber=9999,strErrString=self.config.FAKE_ERROR) 
        

        if not self.DST:
            return self.wsError
        

        if messageData:
            
            principale=messageData.get("principale")
            allegati=messageData.get("allegati")
            oggetto=messageData.get("protocollo_oggetto")
            destinatari_a=messageData.get('destinatari_a',[])
            destinatari_aoo=messageData.get('destinatari_aoo',[])
            destinatari_cc=messageData.get('destinatari_cc',[])
            flusso='U'

            # se il flusso è in uscita i destinatari sono obbligatori
            if not destinatari_a:
                message = u"Mancano i destinatari per la protocollazione"
                return IResult(lngErrNumber=999, strErrString="Mancano i destinatari per la protocollazione")
            
            ## ci vanno anche quelli in cc?
            self.Destinatari = destinatari_a + destinatari_cc
            self.DestinatariAOO = destinatari_aoo
            self.DestinatariA=destinatari_a
            self.DestinatariCC=destinatari_cc

        else:
            ### prot in entrata
            pippo=1
            

        xmlSegnatura = self.__getSegnatura()
        
        if testXml:       
            return IResult(strErrString=xmlSegnatura)

        #Protocollazione Documento
        try:
            result = with_soap_attachment(self.wsClient.service.protocollazione,
                                          [xmlSegnatura, 'profilazione', 'text/xml'], self.config.wsUser, self.DST)  
            return result
            
        except Exception as e:
            return IResult(lngErrNumber=999, strErrString= str(e))
        



        # se protocollazione in uscita aggiungo la segnatura e oggetto
        ''''
        if flusso=='U':
            self.numero_protocollo="%07d" %result['lngNumPG']
            self.data_protocollo=datetime.today().strftime("%d/%m/%Y")
            # Segnatura di protocollazione
            tplSegnatura = ViewPageTemplateFile("templates/segnatura_pec.pt")
            xmlSegnatura = tplSegnatura(self)
        '''

