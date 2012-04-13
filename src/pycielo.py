# -*- coding: utf-8 -*-

import urllib
import xml.dom.minidom

CIELO_ENDPOINT_TEST = 'https://qasecommerce.cielo.com.br/servicos/ecommwsec.do'
CIELO_ENDPOINT_PROD = 'https://ecommerce.cbmp.com.br/servicos/ecommwsec.do'

class Cielo(object):

    def __init__(self, vnum, vkey, cielo_endpoint=CIELO_ENDPOINT_PROD):
        ''' Initializes the transaction process. '''

        ## configures the webservice information
        self.cielo_endpoint = cielo_endpoint

        ## defines the initial data of the vendor
        self.data = {}
        self.data['vnum'] = vnum
        self.data['vkey'] = vkey
        self.data['ccbrand'] = 'visa'
        self.data['ccparts'] = '1'
        self.data['product'] = '1'

        ## starts the initial transaction
        self.get_transaction_id()

    def get_transaction_id(self, force_request=False):
        ''' Request a transaction ID. '''

        ## returns the current transaction if exists
        if not force_request and 'tid' in self.data:
            return self.data['tid']

        ## requests a new transaction id
        content  = '<?xml version="1.0" encoding="UTF-8"?>'
        content += '<requisicao-tid id="1" versao="1.1.0">'
        content += self.get_vendor_node()
        content += self.get_payment_node()
        content += '</requisicao-tid>'

        ## extract the desired information
        dom = xml.dom.minidom.parseString(self.fetch_response(content))
        self.data['tid'] = dom.getElementsByTagName("tid")[0]
        return self.data['tid']

    def get_vendor_node(self):
        ''' Returns the XML node with vendor data. '''

        content  = '<dados-ec>'
        content += '<numero>%s</numero>' % self.data['vnum']
        content += '<chave>%s</chave>' % self.data['vkey']
        content += '</dados-ec>'
        return content

    def get_payment_node(self):
        ''' Returns the XML node with payment data. '''

        content  = '<forma-pagamento>'
        content += '<bandeira>%s</bandeira>' % self.data['ccbrand']
        content += '<produto>%s</produto>' % self.data['product']
        content += '<parcelas>%s</parcelas>' % self.data['ccparts']
        content += '</forma-pagamento>'
        return content

    def fetch_response(self, content):
        ''' Consumes the webservice and fetches its response. '''

        query = urllib.urlencode({ 'mensagem':content })
        return urllib.urlopen(self.cielo_endpoint, query).read()


if __name__ == '__main__':

    ## cielo testing keys
    TESTING_VENDOR_NUM = '1006993069'
    TESTING_VENDOR_KEY = '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3'

    ## consumes the webservice
    c = Cielo(TESTING_VENDOR_NUM, TESTING_VENDOR_KEY, cielo_endpoint=CIELO_ENDPOINT_TEST)
    print c.data['tid']
