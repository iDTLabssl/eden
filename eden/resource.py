# -*- coding: utf-8; -*-
import logging
from flask import abort
from eve.utils import config

import eden

log = logging.getLogger(__name__)

not_indexed = {'type': 'string', 'index': 'no'}  # noqa
not_analyzed = {'type': 'string', 'index': 'not_analyzed'}


def build_custom_hateoas(hateoas, doc, **values):
    values.update(doc)
    links = doc.get(config.LINKS)
    if not links:
        links = {}
        doc[config.LINKS] = links

    for link_name in hateoas.keys():
        link = hateoas[link_name]
        link = {'title': link['title'], 'href': link['href']}
        link['href'] = link['href'].format(**values)
        links[link_name] = link


_METHODS = ['GET', 'HEAD', 'POST', 'PATCH', 'PUT', 'DELETE']


class Resource:
    '''
    Base model for all endpoints, defines the basic implementation
    for CRUD datalayer functionality.
    '''
    endpoint_name = None
    url = None
    item_url = None
    additional_lookup = None
    schema = {}
    allow_unknown = None
    item_methods = None
    resource_methods = None
    public_methods = None
    public_item_methods = None
    extra_response_fields = None
    embedded_fields = None
    datasource = None
    versioning = None
    internal_resource = None
    resource_title = None
    service = None
    endpoint_schema = None
    resource_preferences = None
    etag_ignore_fields = []
    mongo_prefix = None
    mongo_indexes = None
    auth_field = None
    authentication = None
    elastic_prefix = None
    query_objectid_as_string = None
    insert_readonly: list = None  # fields that should be readonly on create
    update_readonly: list = None  # fields that should be readonly on edit
    replace_readonly: list = None  # fields that should be readonly on edit

    def __init__(self, endpoint_name, app, service, endpoint_schema=None):
        self.endpoint_name = endpoint_name
        self.service = service
        if not endpoint_schema:
            endpoint_schema = {'schema': self.schema}
            if self.allow_unknown is not None:
                endpoint_schema.update({'allow_unknown': self.allow_unknown})
            if self.additional_lookup is not None:
                endpoint_schema.update({'additional_lookup': self.additional_lookup})
            if self.extra_response_fields is not None:
                endpoint_schema.update({'extra_response_fields': self.extra_response_fields})
            if self.datasource is not None:
                endpoint_schema.update({'datasource': self.datasource})
            if self.item_methods is not None:
                endpoint_schema.update({'item_methods': self.item_methods})
            if self.resource_methods is not None:
                endpoint_schema.update({'resource_methods': self.resource_methods})
            if self.public_methods is not None:
                endpoint_schema.update({'public_methods': self.public_methods})
            if self.public_item_methods is not None:
                endpoint_schema.update({'public_item_methods': self.public_item_methods})
            if self.url is not None:
                endpoint_schema.update({'url': self.url})
            if self.item_url is not None:
                endpoint_schema.update({'item_url': self.item_url})
            if self.embedded_fields is not None:
                endpoint_schema.update({'embedded_fields': self.embedded_fields})
            if self.versioning is not None:
                endpoint_schema.update({'versioning': self.versioning})
            if self.internal_resource is not None:
                endpoint_schema.update({'internal_resource': self.internal_resource})
            if self.resource_title is not None:
                endpoint_schema.update({'resource_title': self.resource_title})
            if self.etag_ignore_fields:
                endpoint_schema.update({'etag_ignore_fields': self.etag_ignore_fields})
            if self.mongo_prefix:
                endpoint_schema.update({'mongo_prefix': self.mongo_prefix})
            if self.auth_field:
                endpoint_schema.update({'auth_field': self.auth_field})
            if self.authentication:
                endpoint_schema.update({'authentication': self.authentication})
            if self.elastic_prefix:
                endpoint_schema.update({'elastic_prefix': self.elastic_prefix})
            if self.query_objectid_as_string:
                endpoint_schema.update({'query_objectid_as_string': self.query_objectid_as_string})
            if self.mongo_indexes:
                # used in app:initialize_data
                endpoint_schema['mongo_indexes__init'] = self.mongo_indexes

        self.endpoint_schema = endpoint_schema

        on_fetched_resource = getattr(app, 'on_fetched_resource_%s' % self.endpoint_name)
        on_fetched_resource -= service.on_fetched
        on_fetched_resource += service.on_fetched

        on_fetched_resource -= self.on_pre_fetched_resource
        on_fetched_resource += self.on_pre_fetched_resource

        on_fetched_item = getattr(app, 'on_fetched_item_%s' % self.endpoint_name)
        on_fetched_item -= service.on_fetched_item
        on_fetched_item += service.on_fetched_item

        on_fetched_item -= self.on_pre_fetched_item
        on_fetched_item += self.on_pre_fetched_item

        on_insert_event = getattr(app, 'on_insert_%s' % self.endpoint_name)
        on_insert_event -= service.on_create
        on_insert_event += service.on_create

        on_insert_event -= self.on_pre_insert
        on_insert_event += self.on_pre_insert

        on_inserted_event = getattr(app, 'on_inserted_%s' % self.endpoint_name)
        on_inserted_event -= service.on_created
        on_inserted_event += service.on_created

        on_update_event = getattr(app, 'on_update_%s' % self.endpoint_name)
        on_update_event -= service.on_update
        on_update_event += service.on_update

        on_update_event -= self.on_pre_update
        on_update_event += self.on_pre_update

        on_updated_event = getattr(app, 'on_updated_%s' % self.endpoint_name)
        on_updated_event -= service.on_updated
        on_updated_event += service.on_updated

        on_delete_event = getattr(app, 'on_delete_item_%s' % self.endpoint_name)
        on_delete_event -= service.on_delete
        on_delete_event += service.on_delete

        on_deleted_event = getattr(app, 'on_deleted_item_%s' % self.endpoint_name)
        on_deleted_event -= service.on_deleted
        on_deleted_event += service.on_deleted

        on_replace_event = getattr(app, 'on_replace_%s' % self.endpoint_name)
        on_replace_event -= service.on_replace
        on_replace_event += service.on_replace

        on_replace_event -= self.on_pre_replace
        on_replace_event += self.on_pre_replace

        on_replaced_event = getattr(app, 'on_replaced_%s' % self.endpoint_name)
        on_replaced_event -= service.on_replaced
        on_replaced_event += service.on_replaced

        # hook in our pre and post processors
        for phase in ('pre', 'post'):
            for method in _METHODS:
                on_event = getattr(app, 'on_%s_%s_%s' % (phase, method, self.endpoint_name))
                event_hook = getattr(self, phase + '_' + method)
                on_event -= event_hook
                on_event += event_hook

        app.register_resource(self.endpoint_name, endpoint_schema)
        eden.resources[self.endpoint_name] = self

    def on_pre_fetched_resource(self, docs):
        if not self.service.is_authorized("GET", docs):
            abort(403, "Access to record for operation is forbidden")

    def on_pre_fetched_item(self, docs):
        if not self.service.is_authorized("LIST", docs):
            abort(403, "Access to record for operation is forbidden")

    def on_pre_insert(self, docs):
        if not self.service.is_authorized("POST", docs):
            abort(403, "Access to record for operation is forbidden")
        if self.insert_readonly:
            for doc in docs:
                for key in set(self.insert_readonly).intersection(set(doc.keys())):
                    del doc[key]

    def on_pre_update(self, updates, original):
        if not self.service.is_authorized("PATCH", updates):
            abort(403, "Access to record for operation is forbidden")
        if self.update_readonly:
            for key in set(self.update_readonly).intersection(set(updates.keys())):
                del updates[key]

    def on_pre_replace(self, document, original):
        if not self.service.is_authorized("PUT"):
            abort(403, "Access to record for operation is forbidden")
        if self.replace_readonly:
            for key in set(self.replace_readonly).intersection(set(document.keys())):
                del document[key]

    @staticmethod
    def rel(resource, embeddable=True, required=False, type='objectid', nullable=False):
        return {
            'type': type,
            'required': required,
            'nullable': nullable,
            'data_relation': {'resource': resource, 'field': '_id', 'embeddable': embeddable}
        }

    @staticmethod
    def int(required=False, nullable=False):
        return {
            'type': 'integer',
            'required': required,
            'nullable': nullable,
        }

    @staticmethod
    def not_analyzed_field(type='string'):
        return {
            'type': type,
            'mapping': not_analyzed,
        }

    @staticmethod
    def pre_GET(request, lookup):
        pass

    @staticmethod
    def pre_HEAD(request, lookup):
        pass

    @staticmethod
    def pre_POST(request):
        pass

    @staticmethod
    def pre_PATCH(request, lookup):
        pass

    @staticmethod
    def pre_PUT(request, lookup):
        pass

    @staticmethod
    def pre_DELETE(request, lookup):
        pass

    @staticmethod
    def post_GET(request, payload):
        pass

    @staticmethod
    def post_HEAD(request, payload):
        pass

    @staticmethod
    def post_POST(request, payload):
        pass

    @staticmethod
    def post_PATCH(request, payload):
        pass

    @staticmethod
    def post_PUT(request, payload):
        pass

    @staticmethod
    def post_DELETE(request, payload):
        pass
