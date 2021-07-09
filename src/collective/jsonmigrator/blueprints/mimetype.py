# -*- coding: utf-8 -*-
from collective.transmogrifier.interfaces import ISection, ISectionBlueprint
from collective.transmogrifier.utils import defaultKeys, Matcher, traverse
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implementer, provider


try:
    from Products.Archetypes.interfaces import IBaseObject
except ImportError:
    IBaseObject = None


@provider(ISectionBlueprint)
@implementer(ISection)
class Mimetype(object):
    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context

        if "path-key" in options:
            pathkeys = options["path-key"].splitlines()
        else:
            pathkeys = defaultKeys(options["blueprint"], name, "path")
        self.pathkey = Matcher(*pathkeys)

        if "mimetype-key" in options:
            mimetypekeys = options["mimetype-key"].splitlines()
        else:
            mimetypekeys = defaultKeys(options["blueprint"], name, "format")
        self.mimetypekey = Matcher(*mimetypekeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*list(item.keys()))[0]
            mimetypekey = self.mimetypekey(*list(item.keys()))[0]

            if not pathkey or not mimetypekey or mimetypekey not in item:
                # not enough info
                yield item
                continue

            path = safe_unicode(item[pathkey].lstrip("/")).encode("ascii")
            obj = traverse(self.context, path, None)

            if obj is None:
                # path doesn't exist
                yield item
                continue

            if IBaseObject and IBaseObject.providedBy(obj):
                obj.setFormat(item[mimetypekey])

            yield item
