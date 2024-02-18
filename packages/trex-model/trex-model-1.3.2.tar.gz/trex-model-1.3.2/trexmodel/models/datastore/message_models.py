'''
Created on 9 Nov 2023

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexmodel.models.datastore.user_models import User
import trexmodel.conf as model_conf
import logging
from datetime import datetime, timedelta
from trexlib.utils.common.date_util import parse_datetime
from trexmodel import conf
from google.auth._default import default
from trexmodel.models.datastore.system_models import Tagging
from trexmodel.conf import MESSAGE_STATUS_SET, MESSAGE_STATUS_NEW, MESSAGE_CATEGORY_SYSTEM,\
    MESSAGE_STATUS_READ, MESSAGE_CATEGORIES, MESSAGE_CATEGORY_ANNOUNCEMENT
from trexmodel.models.datastore.transaction_models import CustomerTransaction


logger = logging.getLogger('model')

'''

message content is json like below format
{
content_type=[html]
content_body=[text in html]

}

'''

class Message(BaseNModel, DictModel):
    message_to              = ndb.KeyProperty(name="message_to", kind=User)
    source_key              = ndb.StringProperty(required=False)
    title                   = ndb.StringProperty(required=True)
    message_category        = ndb.StringProperty(required=True, default=MESSAGE_CATEGORY_SYSTEM, choices=MESSAGE_CATEGORIES)
    message_content         = ndb.JsonProperty(required=True, indexed=False)
    message_data            = ndb.JsonProperty(required=True, indexed=False)
    status                  = ndb.StringProperty(required=True, default=MESSAGE_STATUS_NEW, choices=MESSAGE_STATUS_SET)    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    read_datetime           = ndb.DateTimeProperty(required=False)
    email_sent_datetime     = ndb.DateTimeProperty(required=False)

    dict_properties = [
                        'source_key', 'message_to', 'title', 'message_category', 'message_content', 'message_data', 'status', 'created_datetime'
                    ]

    @property
    def user_acct_entity(self):
        return User.fetch(self.message_to.urlsafe())
    
    
    @property
    def customer_transaction_entity(self):
        customer_transaction_key = self.message_data.get('transaction_key')
        if customer_transaction_key:
            return  CustomerTransaction.fetch(customer_transaction_key) 
    
    @staticmethod
    def create(source_key=None, message_to=None, title=None, message_type=MESSAGE_CATEGORY_ANNOUNCEMENT,message_content={}):
        Message(
            source_key      = source_key,
            message_to      = message_to.create_ndb_key(),
            title           = title,
            message_type    = message_type,
            message_content = message_content,
            #created_datetime= datetime.utcnow(),
            ).put()
    
    @staticmethod        
    def update_read(message_key):
        message = Message.fetch(message_key)
        if message:
            user_acct = message.user_acct_entity
            logger.debug('found message title=%s', message.title)
            message.status = MESSAGE_STATUS_READ
            message.read_datetime = datetime.utcnow()
            message.put()
            
            user_acct.new_message_count-=1
            if user_acct.new_message_count<0:
                user_acct.new_message_count=0

            user_acct.put()
            
    @staticmethod        
    def update_delete(message_key):
        message = Message.fetch(message_key)
        
        if message:
            logger.debug('found message title=%s', message.title)
            message.delete()   
            
    @staticmethod
    def list_paginated_by_user_account(user_acct, limit=conf.MAX_FETCH_RECORD, start_cursor=None):
        query = Message.query(ndb.AND(Message.message_to==user_acct.create_ndb_key())).order(-Message.created_datetime)     
        
        return Message.list_all_with_condition_query(query, limit=limit, start_cursor=start_cursor, return_with_cursor=True, keys_only=False)
    

    @staticmethod
    def get_by_source_key(source_key):
        return  Message.query(ndb.AND(Message.source_key==source_key)).get()
    
