# -*- coding: utf-8 -*-

from contextIO.ContextIO import ContextIO

api_key = 'YOUR_KEY'
api_secret = 'YOUR_SECRET'
mailbox_to_query = 'jim@acme.com'

api_client = ContextIO(api_key=api_key,
                       api_secret=api_secret)

# EXAMPLE 1
# Print the subject line of the last 20 emails sent to with bill@example.com
response = api_client.contactmessages(account=mailbox_to_query,to_address='bill@example.com',limit=20)
for message in response.get_data():
    print 'Subject %s' % message['subject']


# EXAMPLE 2
# Download all versions of the last 2 attachments exchanged with bill@example.com

response = api_client.contactfiles(account=mailbox_to_query,email='bill@example.com',limit=2)
for document in response.get_data():
    print "Downloading all versions of document %s" % document['fileName']

    for attachment in document['occurences']:
        file_response = api_client.downloadfile(file_id=attachment['fileId'])
        file_content_type = file_response.get_content_type()

        fileobj = open(attachment['fileName'], mode="wb")
        fileobj.write(file_response.get_content())
        fileobj.close()

# EXAMPLE 3
# Download all attachments with a file name that contains the word 'proposal'

print "Downloading all attachments matching 'proposal'\n"
response = api_client.filesearch(account=mailbox_to_query,filename='proposal')
for attachment in response.get_data():
    print "Downloading attachment %s" % attachment['fileName']

    file_response = api_client.downloadfile(file_id=attachment['fileId'])
    fileobj = open(attachment['fileName'], mode="wb")
    fileobj.write(file_response.get_content())
    fileobj.close()
