import datetime
import hashlib
import imp
import inspect
import ipaddress
import json
import logging
import os
import re
import string
import sys
import uuid

from urllib.parse import urlparse

from django.db import connections

from django.db import models
from django.utils.deconstruct import deconstructible

from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import JSONField


def bumpy_case_words(string):
    return [s for s in re.findall('([A-Z]*[a-z]*)', string) if len(s) > 0]


def string_with_unique_suffix(value, haystack):
    """
    Args:
        value: The string to generate a unique value for
        haystack: The set of strings to compare against for uniqueness

    Returns: The given value with a suffix index that renders it unique among the given set
    """
    haystack.sort()
    suffix = 1
    needle = value
    while needle in haystack:
        needle = '{}-{}'.format(value, suffix)
        suffix += 1

    return needle


def split_path(string, separator='/', count=1):
    """
    Given a path, return a tuple containing the specified number of initial elements
    and the remainder, which may be none.  Raises ValueError if the given path does
    not contain the specified number of components.

    e.g.

      > split_path('yabba/dabba/doo')
      ('yabba', 'dabba/doo')

      > split_path('yabba/dabba/doo', count=2)
      ('yabba', 'dabba', 'doo')

      > split_path('yabba.dabba.doo', '.', 3)
      ('yabba', 'dabba', 'doo', None)

    """
    result = []
    for i in range(0, count):
        if string is None:
            raise ValueError('empty path')
        index = string.find(separator)
        if index >= 0:
            result.append(string[:index])
            string = string[index+len(separator):]
        else:
            result.append(string)
            string = None
    result.append(string)
    return result


def path_components(string, separator='/'):
    """
    """
    element, rest = split_path(string, separator)
    if rest is None:
        return [element]
    return [element] + path_components(rest, separator)


def get_module_from_path(module_path, search_path=None):
    """
    Return the module associate with the given path (e.g. 'django.db'), loading the
    module if necessary.  Returns None if the named module cannot be found.
    """
    if module_path is None:
        return None

    # Lookup the module path in python's dictionary of loaded modules...
    module = sys.modules.get(module_path)
    if module is None:
        def _get_module(module_name, parent_module=None):
            module_path = parent_module.__name__ + '.' + module_name if parent_module else module_name
            module = sys.modules.get(module_path)
            if module is None:
                (file, path, desc) = imp.find_module(module_name, parent_module.__path__ if parent_module else search_path)
                if file or path:
                    try:
                        module = imp.load_module(module_path, file, path, desc)
                    except Exception as e:
                        raise Exception("failed to load '%s' -- %s" % (path, e.message))
                    finally:
                        if file:
                            file.close()
            return module
        for component in path_components(module_path, '.'):
            parent_module = module
            module = _get_module(component, parent_module)
            if module is None:
                logger = logging.getLogger('alpha')
                if parent_module:
                    logger.info("module '%s' has no component named '%s'" % (parent_module.__path__, component))
                else:
                    logger.info("unknown top-level module '%s"'' % component)
                break

    return module


def get_path_from_class(cls):
    """
    Return the relative path of the given class in the form <module-path>.<class-name>.
    """
    return '{}.{}'.format(cls.__module__, cls.__name__)


def get_class_from_path(path, superclass=None, search_path=None):
    """
    Return the class object corresponding to the given path, which has the
    form <module-path>.<class-name>.
    """
    module_path, class_name = string.rsplit(path, '.', 1)
    module = get_module_from_path(module_path, search_path)
    return get_class_from_module(module, class_name, superclass) if module else None


def get_class_from_module(module, class_name, superclass=None):
    """
    Return the named class from the given module; optionally require the class
    be derived from the given superclass.
    """
    cls = module.__dict__.get(class_name)
    if not inspect.isclass(cls):
        raise Exception("module '{}' has no class-valued attribute '{}'".format(module.__name__, class_name))
    if superclass and not issubclass(cls, superclass):
        raise Exception("class '{}' of module '{}' is not derived from class '{}'".format(class_name, module.__name__, superclass.__name__))
    return cls


def assign_timestamps(obj, date_created, date_modified):
    with connections[obj._state.db].cursor() as cursor:
        query_template = "UPDATE {trg_table_name} SET date_created='{date_created}',date_modified='{date_modified}' WHERE id={pk}"
        update_query = query_template.format(
            trg_table_name=obj._meta.db_table,
            pk=obj.pk,
            date_created=date_created.isoformat(),
            date_modified=date_modified.isoformat(),
        )
        return cursor.execute(update_query)


def sync_auto_timestamps(db, src, trg):
    fetch_query_template = "SELECT date_created,date_modified FROM {src_table_name} WHERE id={pk}"
    update_query_template = "UPDATE {trg_table_name} SET date_created='{date_created}',date_modified='{date_modified}' WHERE id={pk}"

    fetch_query = fetch_query_template.format(
        src_table_name=src._meta.db_table,
        pk=src.pk
    )
    db.execute(fetch_query)
    src_info = db.fetchone()

    update_query = update_query_template.format(
        trg_table_name=trg._meta.db_table,
        date_created=src_info[0],
        date_modified=src_info[1],
        pk=trg.pk
    )
    db.execute(update_query)


def value_for_attr_path(obj, attr_path):
    value = obj
    attributes = attr_path.split('.')
    for attribute in attributes:
        value = getattr(value, attribute)
    return value


def value_for_key_path(object, keypath, default=None, raise_exception=False):
    """
    Provide access to a property chain
    """
    target_object = object

    keys = keypath.split('.')
    for key in keys:
        try:
            if isinstance(target_object, dict):
                target_object = target_object[key]
            else:
                target_object = target_object.__getitem__(key)
        except (KeyError, AttributeError) as e:
            if raise_exception:
                raise KeyError('Keypath "{}" could not be resolved to a value'.format(keypath))
            return default

    return target_object


def filter_dict(value, keys):
    return {k: v for k, v in value.items() if k in keys}


def random_digest(digest_size=8):
    return hashlib.blake2s(digest_size=digest_size).hexdigest()


def top_level_domain(url):
    hostname = urlparse(url).hostname
    try:
        # If the hostname is an IP address, return it as-is
        ipaddress.IPv4Address(hostname)
        return hostname
    except ValueError:
        domain_parts = hostname.split('.')
        if len(domain_parts) > 2:
            domain_parts = domain_parts[-2:]
        return '.'.join(domain_parts)


class SimpleModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, models.Model):
            return str(obj)

        return super().default(obj)


def hashed_filename(image_file):
    hash = hashlib.blake2b(digest_size=4)
    if isinstance(image_file, str):
        with open(image_file, 'rb') as source_file:
            hash.update(source_file.read())
    else:
        hash.update(image_file.tobytes())
    return hash.hexdigest()


def primitive_attribute_names(ModelClass):
    """
    Given a django model class, return a list containing the names of all
    primitive fields (ex: strings, numbers, dates, booleans, etc).

    A primitive attribute is any field that _does not_ represent a relationship
    or complex data structure (ex: JSONField)
    """
    model_fields = ModelClass._meta.get_fields()
    return [field.name for field in model_fields if not (
            isinstance(field, GenericRelation)
            or isinstance(field, JSONField)
            or field.one_to_many
            or field.auto_created
            or field.many_to_many
            or field.one_to_one
    )]


@deconstructible
class UploadTo(object):
    """
    This class is used to generate a unique directory for uploaded files so as
    to avoid having to rename the uploaded file due to a name collision.
    An instance of this class may be supplied as the 'upload_to' parameter of
    a FileField whereby the given media_path_prefix is a subdirectory under the
    media root directory (ex: 'attachments', 'avatars', etc).
    """
    def __init__(self, media_path_prefix=None):
        self.media_path_prefix = media_path_prefix

    def upload_path(self, instance, filename):
        # To keep the paths a bit shorter, use only the last eight characters of
        # a generated UUID. It is _highly unlikely_ that the same character sequence
        # will be generated twice in one day.
        return os.path.join(
            datetime.datetime.today().strftime('%Y/%m/%d'),
            str(uuid.uuid4())[:8],
            filename
        )

    def __call__(self, instance, filename):
        path_components = [self.upload_path(instance, filename)]

        if self.media_path_prefix:
            path_components.insert(0, self.media_path_prefix)

        if os.environ.get('TEST'):
            path_components.insert(0, 'test')

        return os.path.join(*path_components)


@deconstructible
class UploadImageAttachmentTo(UploadTo):
    def upload_path(self, attachment, filename):
        obj = attachment.object
        media_attachment_directory = obj.get_media_attachment_directory(attachment)
        return os.path.join(media_attachment_directory, filename)


@deconstructible
class UploadSecureAttachmentTo(UploadTo):
    def upload_path(self, attachment, filename):
        obj = attachment.object
        media_attachment_directory = obj.get_media_attachment_directory(attachment)

        return os.path.join(
            media_attachment_directory,
            filename
        )


def django_request_from_drf_request(request):
    django_request = request._request
    post_data = django_request.POST.copy()
    for k, v in request.data.items():
        post_data[k] = v
    django_request.POST = post_data
    return django_request
