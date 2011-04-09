# -*- coding: utf-8 -*-
"""
Copyright (C) 2011 DokDok Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import time
import oauth2 as oauth
import httplib2

from contextIO.ContextIOResponse import ContextIOResponse


class ContextIORequester(httplib2.Http):

    def __init__(self, api_key, api_secret, api_url='https://api.context.io',
                 api_version=1.1, api_format='json', account=None,
                 cache=None, timeout=None, proxy_info=None):

        self.api_url = api_url
        self.api_version = api_version
        self.api_format = api_format
        self.params = {
            'oauth_version': "1.0",
        }

        self.consumer = oauth.Consumer(key=api_key, secret=api_secret)
        self.params['oauth_consumer_key'] = self.consumer.key
        if account:
            self.account = account
        else:
            self.account = None
            
        super(ContextIORequester,self).__init__(cache,timeout,proxy_info)

    def build_url_with_format(self,
                               action,
                               context,
                               account):
        action_with_format = '%s.%s' % (action, self.api_format)
        return self.build_url(action_with_format,
                               context,
                               account)

    def build_url(self,
                   action,
                   context,
                   account=None):
        url = '%s/%s/%s?' % (self.api_url, self.api_version, action)

        if account:
            context['account'] = account
        elif self.account:
            context['account'] = self.account

        for key in context:
            url += '%s=%s&' % (key, context[key])

        return url

    def get_response(self,
                      action,
                      context,
                      account):
        url = self.build_url_with_format(action, context, account)
        return self.get_response_for_url(url)

    def get_response_for_url(self, url):
        parameters = self.params
        parameters['oauth_nonce'] = oauth.generate_nonce()
        parameters['oauth_timestamp'] = '%s' % int(time.time())

        req = oauth.Request(method="GET", url=url, parameters=parameters)
        # Sign the request.
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, None)
        response, content = self.request(req.to_url(),
                                        method="GET",
                                        body='',
                                        headers={},
                                        redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                                        connection_type=None)
        if response['status'] != '200':
            raise Exception("Invalid response %s" % response['status'])
        return ContextIOResponse(response, content)


class ContextIO(object):
    """
       ContextIO's client implementation using oauth.

       Note: If you have only one account you can instantiate ContextIO with the account parameter.
             If you have more than one account, you need to specify it for each method call

    """
    def __init__(self,
                 api_key,
                 api_secret,
                 api_format='json',
                 api_url='https://api.context.io',
                 api_version=1.1,
                 account=None,
                 cache=None,
                 timeout=None,
                 proxy_info=None):

        self.requester = ContextIORequester(api_key=api_key,
                                            api_secret=api_secret,
                                            api_version=api_version,
                                            api_format=api_format,
                                            api_url=api_url,
                                            account=account,
                                            cache=cache,
                                            timeout=timeout,
                                            proxy_info=proxy_info)

    def addresses(self,account=None):
        return self._get_response(action='addresses',context={},account=account)


    def allfiles(self, since, limit=None, account=None):
        """
         see http://developer.context.io/page/allfiles
        """
        context = {'since': since}
        return self._get_response('allfiles',
                                  context,
                                  limit,
                                  account)

    def allmessages(self, since, limit=None, account=None):
        """
        see http://developer.context.io/page/allmessages
        """
        context= {'since': since}
        return self._get_response('allmessages',
                                  context,
                                  limit,
                                  account)

    def contactfiles(self, email, limit=None, account=None):
        """
        see http://developer.context.io/page/contactfiles
        """
        context={'email': email}
        return self._get_response('contactfiles',
                                   context,
                                   limit,
                                   account)

    def contactmessages(self, email='', to_address='', from_address='',
                        cc_address='', limit=None, account=None):
        """
        see http://developer.context.io/page/contactmessages
        """
        context = {}
        if email:
            context['email'] = email
        if to_address:
            context['to'] = to_address
        if from_address:
            context['from'] = from_address
        if cc_address:
            context['cc'] = cc_address
        return self._get_response('contactmessages',
                                  context,
                                  limit,
                                  account)

    def diffsummary(self, file_id1, file_id2, account):
        """
        see http://developer.context.io/page/diffsummmary
        """

        context = {
            'fileid1': file_id1,
            'fileid2': file_id2
        }
        return self._get_response('diffsummary',
                                  context,
                                  account)

    def diffsummary_with_comparaison(self, file_id1, file_id2, account):
        context = {
            'fileid1': file_id1,
            'fileid2': file_id2,
            'generate': '1'
        }
        return self._get_response('diffsummary',
                                  context,
                                  account)

    def downloadfile(self, file_id, account=None):
        context = {
            'fileid': file_id
        }
        url = self.requester.build_url('downloadfile',
                              context,
                              account)
        return self._get_response_for_url(url)

    def filerevisions(self, file_ids, limit=None, account=None):
        context = {
            'fileid': ','.join(file_ids)
            }

        return self._get_response('filerevisions',
                                  context,
                                  limit,
                                  account)

    def filerevisions_by_filename(self, filename, limit=None, account=None):
        context = {
            'filename': filename
        }

        return self._get_response('filerevisions',
                                  context,
                                  limit,
                                  account)

    def filesearch(self, filename, limit=None, account=None):
        context = {
            'filename': filename
        }
        return  self._get_response('filesearch',
                                   context,
                                   limit,
                                   account)

    def messageinfo(self, message_id, account=None):
        context = {
            'emailmessageid': message_id
        }
        return self._get_response('messageinfo',
                                  context,
                                  account=account)

    def messageinfo_from_address(self, date_sent, from_address, account=None):
        context = {
            'datesent': date_sent,
            'from': from_address
        }
        return self._get_response('messageinfo',
                                  context,
                                  account=account)

    def messagetext(self, message_id, type='all', account=None):
        context = {
            'emailmessageid': message_id
        }
        if type != 'all':
            context['type'] = type

        return self._get_response('messagetext',
                                  context,
                                  account=account)

    def messagetext_from_address(self, date_sent, from_address, type='all',
                                 account=None):
        context = {
            'datesent': date_sent,
            'from': from_address
        }
        if type != 'all':
            context['type'] = type
        return self._get_response('messagetext',
                                  context,
                                  account=account)

    def relatedfiles(self, file_id, limit=None, account=None):
        context = {
            'fileid': file_id,
        }

        return self._get_response('relatedfiles',
                                  context,
                                  limit,
                                  account)

    def search(self, subject, limit=None, account=None):
        context = {
            'subject': subject
        }

        return self._get_response('search',
                                  context,
                                  limit,
                                  account)

    def threadinfo(self, gmail_thread_id='',email_id='', account=None):
        context = {}

        if gmail_thread_id and email_id:
            raise Exception("You can't specify both parameter at the same time")

        if not (gmail_thread_id or email_id):
            raise Exception("You need to specify at least one parameter")

        if gmail_thread_id:
            context['gmailthreadid'] = gmail_thread_id

        if email_id:
            context['emailmessageid'] = email_id

        return self._get_response('threadinfo',
                                  context,
                                  account=account)

    def _get_response(self, action, context, limit=None, account=None):
        if limit:
            context['limit']= limit
        url = self.requester.build_url_with_format(action, context, account)
        return self.requester.get_response_for_url(url)

    def _get_response_for_url(self, url):
        return self.requester.get_response_for_url(url)


class IMAPAdmin(object):

    """
       Administrative IMAP functions
    """
    def __init__(self,
                 api_key,
                 api_secret,
                 api_version=1.1,
                 api_format='json',
                 api_url='https://api.context.io',
                 cache=None, timeout=None, proxy_info=None):
        self.requester = ContextIORequester(api_key=api_key,
                                        api_secret=api_secret,
                                        api_version=api_version,
                                        api_format=api_format,
                                        api_url=api_url,
                                        account=None,
                                        cache=cache, timeout=timeout, proxy_info=proxy_info)

    def _get_response(self, action, context):
        url = self.requester.build_url(action, context)
        return self.requester.get_response_for_url(url)

    def add_account(self, email, username, password,
                    server='imap.gmail.com', usessl=True, port=993):
        context = {
            'email': email,
            'username': username,
            'password': password,
            'server': server,
            'usessl': '1' if usessl else '0',
            'port': '%s' % port
        }
        return self._get_response('imap/addaccount.json', context)

    def discover(self, email):
        context = {
            'email': email
        }
        return self._get_response('imap/discover.json', context)

    def modify_account(self, credentials='', mailboxes=None):
        context = {}
        if credentials:
            context['credentials'] = credentials
        if mailboxes:
            context['mailboxes'] = ','.join(mailboxes)

        return self._get_response('imap/mofifyaccount.json',context)

    def remove_account(self, account):
        context = {'account':account}
        return self._get_response('imap/removeaccount.json', context)

    def reset_account(self, account):
        context = {'account':account}
        return self._get_response('imap/resetaccount.json', context)
