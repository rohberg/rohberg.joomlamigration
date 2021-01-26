# coding: utf-8
from bs4 import BeautifulSoup
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from plone.outputfilters.filters.resolveuid_and_caption import ResolveUIDAndCaptionFilter
from zope.interface import provider
from zope.interface import implementer

import logging
import re
import six


logger = logging.getLogger('rohberg.joomlamigration.createimages')

class LinkedImageConversionParser(ResolveUIDAndCaptionFilter):
    """
    Eventuell plone.outputfilters_captioned_image überschreiben: snippet für images
    """

    def __init__(self, target='images'):
        ResolveUIDAndCaptionFilter.__init__(self)
        # self.atag = None
        # self.abuffer = []
        self.items = []
        self.target = target

    def __call__(self, data):
        data = re.sub(r'<([^<>\s]+?)\s*/>', self._shorttag_replace, data)
        # TODO safe_unicode?
        soup = BeautifulSoup(data, 'html.parser')

        for elem in soup.find_all('img'):
            attributes = elem.attrs
            src = attributes.get('src', '')
            title = attributes.get('title', '')
            alt = attributes.get('alt', '')
            logger.debug("found image node src: {} {} {}".format(src, title, alt))
            if src.startswith("image/"):
                logger.debug("do handle_captioned_image")
                image = None
                # todo create image
                if image:
                    self.items.append(image)
                # todo replace image snippet
            else:
                logger.debug("src found not starting with image/")
        return six.text_type(soup)
        # return data


@provider(ISectionBlueprint)
@implementer(ISection)
class CreateLinkedImages(object):
    """
    Parse HTML for images and inject them into the pipeline so that they can
    be served locally.

    update text with resolveuid/trallala
    """


    def __init__(self, transmogrifier, name, options, previous):
        self.options = options
        self.previous = previous
        self.textsource = options.get('textsource', 'text')
        self.sourcedomain = options.get('sourcedomain', '')
        self.targetcontainer_path = options.get('targetcontainer_path', 'images')

    def __iter__(self):
        for item in self.previous:
            images = []
            if self.textsource in item:
                text = item[self.textsource]
                parser = LinkedImageConversionParser(target=self.targetcontainer_path)
                images = []
                logger.info('** find images in {}'.format(item['_path']))
                logger.info(item[self.textsource])
                # import pdb; pdb.set_trace()
                try:
                    item[self.textsource] = parser(text)
                    images = parser.items # sind das die gefundenen images?
                except AttributeError:
                    # breakpoint()
                    logger.error('AttributeError')
                    import pdb; pdb.set_trace()
                    yield item
                if images:
                    logger.info('!! found images {}'.format(images))
                else:
                    logger.info('no images found')

            yield item

            for item in images:
                yield item
