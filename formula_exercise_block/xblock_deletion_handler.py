""" receivers of course_published and library_updated events in order to trigger indexing task """

import logging
import db_service

from django.dispatch import receiver
from celery.task import task
from xmodule.modulestore.django import modulestore, SignalHandler

log = logging.getLogger(__name__)


@receiver(SignalHandler.item_deleted)
def CUSTOM_handle_xblock_deleted(sender, usage_key, user_id, **kwargs):
    """
    Receives the item_deleted signal sent by Studio when an XBlock is removed from
    the course structure and removes any gating milestone data associated with it or
    its descendants.

    Arguments:
        kwargs (dict): Contains the content usage key of the item deleted

    Returns:
        None
    """

#    db_service.delete_all_xblocks() this method is invoked correctly
#    usage_key = kwargs.get('usage_key')
    # do_something_slow.delay(usage_key)
    log.info('CUSTOM_handle_xblock_deleted: str(usage_key) :: ' + str(usage_key))
    


@task(name='xblock_deletion_handler.tasks.do_something_slow')
def do_something_slow(usage_key):

    usage_key = usage_key.for_branch(None)
    course_key = usage_key.course_key
    deleted_module = modulestore().get_item(usage_key)
    
    xblock_id = unicode(deleted_module.location.replace(branch=None, version=None))
    
    log.error('DELETE xblock_id: ' + xblock_id)
    log.debug('DELETE xblock_id: ' + xblock_id)
    log.log('DELETE xblock_id: ' + xblock_id)
    log.info('DELETE xblock_id: ' + xblock_id)
    log.warning('DELETE xblock_id: ' + xblock_id)
    log.exception('DELETE xblock_id: ' + xblock_id)
    
    db_service.delete_xblock(usage_key.block_id)
    
    raise ValueError('xblock_id: ' + xblock_id)
