'''
Created on 8 Jan 2024

@author: jacklok
'''
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from google.cloud import ndb
from trexmodel.models.datastore.merchant_models import MerchantUser,\
    MerchantAcct
from trexlib.utils.string_util import is_not_empty, random_string
from datetime import datetime
from trexmodel import program_conf, conf
import trexmodel.conf as model_conf
import logging

logger = logging.getLogger('model')

class PushNotificationSetup(BaseNModel, DictModel):
    '''
    Merchant Acct as ancestor
    
    '''
    
    title                   = ndb.StringProperty(required=True)
    desc                    = ndb.StringProperty(required=True)
    send_mode               = ndb.StringProperty(required=True, default="send_now", choices=set(['send_now','send_schedule']))
    schedule_datetime       = ndb.DateTimeProperty(required=False)
    
    content_settings        = ndb.JsonProperty()
    
    is_archived             = ndb.BooleanProperty(required=True)
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    archived_datetime       = ndb.DateTimeProperty(required=False)
    
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username     = ndb.StringProperty(required=False)
    
    archived_by             = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    archived_by_username    = ndb.StringProperty(required=False)
    
    send                    = ndb.BooleanProperty(required=True, default=False)
    sent_datetime           = ndb.DateTimeProperty(required=False)
    
    dict_properties = [
                        'title', 'desc', 'send_mode', 'schedule_datetime', 
                        'content_type', 'content_value', 'content_settings', 
                        'created_datetime', 'send', 'sent_datetime',
                    ]
    
    @property
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def content_type(self):
        if self.content_settings:
            return self.content_settings.get('content_type')
    
    @property
    def content_value(self):
        if self.content_settings:
            return self.content_settings.get('content_value')
        
    @property
    def image_url(self):
        if self.content_settings:
            if self.content_settings.get('content_type')=='image':
                return self.content_settings.get('content_value')
            
    @property
    def text_data(self):
        if self.content_settings:
            if self.content_settings.get('content_type')=='text':
                return self.content_settings.get('content_value')
            
    @property
    def action_link(self):
        if self.content_settings:
            if self.content_settings.get('content_type')=='action_link':
                return self.content_settings.get('content_value')                    
            
    @staticmethod
    def create(merchant_acct, title=None, desc=None, send_mode=None, schedule_datetime=None, content_settings={},
               created_by=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
                
        push_notification_setup = PushNotificationSetup(
                                                parent                  = merchant_acct.create_ndb_key(),
                                                title                   = title,
                                                desc                    = desc,
                                                send_mode               = send_mode,
                                                schedule_datetime       = schedule_datetime,
                                                content_settings        = content_settings,
                                                is_archived             = False,
                                                created_by              = created_by.create_ndb_key(),
                                                created_by_username     = created_by_username,
                                                )
        push_notification_setup.put()
        
        return push_notification_setup
    
    
    def to_configuration(self):
        return {
                
                }
    
    def archived(self, archived_by=None):
        
        archived_by_username = None
        if is_not_empty(archived_by):
            if isinstance(archived_by, MerchantUser):
                archived_by_username = archived_by.username
        
        self.is_archived                = True
        self.archived_datetime          = datetime.utcnow()
        self.archived_by                = archived_by.create_ndb_key()
        self.archived_by_username       = archived_by_username
        self.put()
        
    def update_as_send(self):
        self.send = True
        self.sent_datetime = datetime.utcnow()
        self.put()
        
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return PushNotificationSetup.query(ndb.AND(PushNotificationSetup.is_archived!=True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_archived_by_merchant_acct(merchant_acct):
        return PushNotificationSetup.query(ndb.AND(PushNotificationSetup.is_archived==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list(schedule_datetime=datetime.utcnow()):
        result = PushNotificationSetup.query(
                    ndb.AND(
                            PushNotificationSetup.send==False, 
                            PushNotificationSetup.schedule_datetime<=schedule_datetime)).fetch(offset=0, limit=conf.MAX_FETCH_RECORD)
        return result
    
class MarketingImage(BaseNModel, DictModel):
    '''
    Merchant Account as ancestor
    '''
    image_label                    = ndb.StringProperty(required=True)
    image_file_type                = ndb.StringProperty(required=True)
    image_file_public_url          = ndb.StringProperty(required=True)
    image_file_storage_filename    = ndb.StringProperty(required=True)
    
    dict_properties = ['image_label', 'image_file_public_url', 'image_file_storage_filename', 'image_file_type']
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        result = MarketingImage.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        return result
    
    @staticmethod
    def upload_file(uploading_file, image_label, merchant_acct, bucket, image_file_type=None):
        file_prefix                         = random_string(8)
        image_file_storage_filename         = 'merchant/'+merchant_acct.key_in_str+'/marketing/'+file_prefix+'-'+uploading_file.filename
        blob                                = bucket.blob(image_file_storage_filename)
        
        logger.debug('image_label=%s', image_label)
        logger.debug('image_file_storage_filename=%s', image_file_storage_filename)
        
        blob.upload_from_string(
                uploading_file.read(),
                content_type=uploading_file.content_type
            )
        
        uploaded_url        = blob.public_url
        
        logger.debug('image_file_type=%s', image_file_type)
        
        image_file = MarketingImage(
                            parent                              = merchant_acct.create_ndb_key(),
                            image_label                         = image_label,
                            image_file_public_url               = uploaded_url,
                            image_file_storage_filename         = image_file_storage_filename,
                            image_file_type                     = image_file_type,
                            )
        
        image_file.put()
        
        return image_file
    
    @staticmethod
    def remove_file(image_file, bucket):
        
        old_logo_blob = bucket.get_blob(image_file.image_file_storage_filename) 
        if old_logo_blob:
            old_logo_blob.delete()
            image_file.delete()      

class ScheduledPushNotificationHistory(BaseNModel, DictModel):
    push_notification_setup = ndb.KeyProperty(name="push_notification_setup", kind=PushNotificationSetup)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    send                    = ndb.BooleanProperty(required=True, default=False)
    scheduled_datetime      = ndb.DateTimeProperty(required=True)
    sent_datetime           = ndb.DateTimeProperty(required=False)    

    @staticmethod
    def create(push_notification_setup, scheduled_datetime=None):
        if scheduled_datetime is None:
            scheduled_datetime = datetime.utcnow()
        ScheduledPushNotificationHistory(
                                    push_notification_setup = push_notification_setup.create_ndb_key(),
                                    scheduled_datetime      = scheduled_datetime,
                                    ).put()
                                    
    
    @staticmethod
    def list(scheduled_datetime=datetime.utcnow()):
        result = ScheduledPushNotificationHistory.query(
                    ndb.AND(
                            ScheduledPushNotificationHistory.send==False, 
                            ScheduledPushNotificationHistory.scheduled_datetime<=scheduled_datetime)).fetch(offset=0, limit=conf.MAX_FETCH_RECORD)
        return result
    