# -*- coding: utf-8 -*-

import urllib
from xml.dom import minidom as dom
from datetime import datetime

CIELO_ENDPOINT_TEST = 'https://qasecommerce.cielo.com.br/servicos/ecommwsec.do'
CIELO_ENDPOINT_PROD = 'https://ecommerce.cbmp.com.br/servicos/ecommwsec.do'

class Cielo(object):

    version = '1.1.0'

    def __init__(self, vnum, vkey, cielo_endpoint=CIELO_ENDPOINT_PROD):
        ''' Initializes the transaction process. '''

        ## configures the webservice information
        self.cielo_endpoint = cielo_endpoint

        ## defines the initial data of the vendor
        self.data = {}
        self.data['vnum'] = vnum
        self.data['vkey'] = vkey

    def set_customer(self, number, expiration, security, indicator='1'):
        ''' Save the customer's credit card information. '''

        self.data['number'] = number
        self.data['expiration'] = expiration
        self.data['security'] = security
        self.data['indicator'] = indicator

    def set_demand(self, demand, value, currency='986', language='PT'):
        ''' Save the customer's credit card information. '''

        self.data['demand'] = demand
        self.data['value'] = value
        self.data['currency'] = currency
        self.data['language'] = language

    def render_header(self, encoding='UTF-8'):
        ''' Returns the XML node with header data. '''

        return '<?xml version="1.0" encoding="%s"?>' % encoding

    def render_transaction(self):
        ''' Returns the XML node with transaction data. '''

        self.create_transaction()
        return '<tid>%s</tid>' % self.data['tid']

    def render_vendor(self):
        ''' Returns the XML node with vendor data. '''

        content  = '<dados-ec>'
        content += '<numero>%s</numero>' % self.data['vnum']
        content += '<chave>%s</chave>' % self.data['vkey']
        content += '</dados-ec>'
        return content

    def render_payment(self):
        ''' Returns the XML node with payment data. '''

        content  = '<forma-pagamento>'
        content += '<bandeira>%s</bandeira>' % self.data['brand']
        content += '<produto>%s</produto>' % self.data['product']
        content += '<parcelas>%s</parcelas>' % self.data['parts']
        content += '</forma-pagamento>'
        return content

    def render_demand(self):
        ''' Returns the XML node with demand data. '''

        content  = '<dados-pedido>'
        content += '<numero>%s</numero>' % self.data['demand']
        content += '<valor>%s</valor>' % self.data['value']
        content += '<moeda>%s</moeda>' % self.data['currency']
        content += '<data-hora>%s</data-hora>' % datetime.now().strftime('%Y-%m-%dT%T')
        content += '<idioma>PT</idioma>'
        content += '</dados-pedido>'
        return content

    def render_customer(self):
        ''' Request a transaction ID. '''

        content  = '<dados-cartao>'
        content += '<numero>%s</numero>' % self.data['demand']
        content += '<validade>%s</validade>' % self.data['expiration']
        content += '<indicador>%s</indicador>' % self.data['indicator']
        content += '<codigo-seguranca>%s</codigo-seguranca>' % self.data['security']
        content += '</dados-cartao>'
        return content

    def create_transaction(self, force_request=False):
        ''' Request a transaction ID. '''

        ## returns the current transaction if exists
        if not force_request and 'tid' in self.data:
            return self.data['tid']

        ## requests a new transaction id
        content  = self.render_header()
        content += '<requisicao-tid id="1" versao="%s">' % self.version
        content += self.render_vendor()
        content += self.render_payment()
        content += '</requisicao-tid>'

        ## extract the desired information
        xml = self._fetch_response(content)
        self.data['tid'] = '1' #xml.getElementsByTagName("tid")[0]
        return self.data['tid']

    def get_authorization(self, brand, parts='1', product='1'):
        ''' Returns the XML node with payment data. '''

        ## sets the payment information
        self.data['brand'] = brand
        self.data['parts'] = parts
        self.data['product'] = product

        content  = self.render_header()
        content += '<requisicao-autorizacao-portador id="7" versao="%s">' % self.version
        content += self.render_transaction()
        content += self.render_vendor()
        content += self.render_demand()
        content += self.render_customer()
        content += self.render_payment()
        content += '<capturar-automaticamente>false</capturar-automaticamente>'
        content += '</requisicao-autorizacao-portador>'
        return content

    def _fetch_response(self, content):
        ''' Consumes the webservice and fetches its response. '''
        
        args = urllib.urlencode({ 'mensagem':content })
        code = urllib.urlopen(self.cielo_endpoint, args).read()
        return dom.parseString(code)


if __name__ == '__main__':

    ## cielo testing keys
    TEST_VENDOR_NUM = '1006993069'
    TEST_VENDOR_KEY = '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3'

    ## consumes the webservice
    c = Cielo(TEST_VENDOR_NUM, TEST_VENDOR_KEY, cielo_endpoint=CIELO_ENDPOINT_TEST)
    c.set_customer('', '', '')
    c.set_demand('1', '100.00')
    r = c.get_authorization('visa')
    print dom.parseString(r).toprettyxml()
