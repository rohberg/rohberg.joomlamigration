# coding: utf-8
from bs4 import BeautifulSoup
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import Expression
from plone.namedfile import NamedImage
from plone.outputfilters.filters.resolveuid_and_caption import ResolveUIDAndCaptionFilter
from zope.interface import provider
from zope.interface import implementer

import logging
import re
import requests
import six


logger = logging.getLogger('rohberg.joomlamigration.imageFetcher')


def createImage(src):
    """ returns imagedata as in fetched response
    no: returns NamedImage (not dexterity image)
    """
    image = None
    url = src
    filename = url.split("/")[-1]
    r = requests.get(url, timeout=0.5)

    if r.status_code == 200:
        # image = NamedImage(r.content, filename=filename)
        image = r.content
        # with open("/Users/ksuess/Desktop/_temp/joom/" + filename, 'wb') as f:
        #     f.write(r.content)
    else:
        logger.warn("couldn't fetch image")
            
    # res = safe_urlopen(src)
    # if res is not None:
    #     mimetype = res.info()['content-type']

    # if res is not None:
    #     scheme, host, path, query, frag = urlsplit(src)
    #     filename = path.split('/')[-1]
    #     # Zope ids need to be ASCII
    #     filename = unquote_plus(filename).decode('utf8').encode('ascii', 'ignore')
    #     # wrap the data so it'll get added with the correct filename & mimetype
    #     data = File(filename, 'image', StringIO(res.read()), mimetype)

    return image


class LinkedImageConversionParser(ResolveUIDAndCaptionFilter):
    """
    Eventuell plone.outputfilters_captioned_image überschreiben: snippet für images
    """

    def __init__(self, target='images', sourcedomain=''):
        ResolveUIDAndCaptionFilter.__init__(self)
        # self.atag = None
        # self.abuffer = []
        self.items = []
        self.target = target
        self.sourcedomain = sourcedomain

    def __call__(self, data):
        data = re.sub(r'<([^<>\s]+?)\s*/>', self._shorttag_replace, data)
        # TODO safe_unicode?
        soup = BeautifulSoup(data, 'html.parser')

        for elem in soup.find_all('img'):
            attributes = elem.attrs
            src = attributes.get('src', '')
            title = attributes.get('title', '')
            alt = attributes.get('alt', '')
            logger.info("found image node src: {}|{}|{}".format(src, title, alt))
            # import pdb; pdb.set_trace()
            if src.startswith("images/"):
                # logger.info("do handle_captioned_image")
                image = None
                imageid = src.split('/')[-1]
                # fetch image data
                # stuff imagedata in additonal pipeline item as data
                imagedata = createImage(self.sourcedomain + '/' + src)
                if imagedata:
                    image = {
                        # '_path': image.absolute_url(),
                        '_path': self.target + "/" + imageid,
                        '_type': 'Image',
                        'image': {
                            'filename': imageid,
                            'contenttype': '',
                            'data': imagedata
                        }
                        }
                    self.items.append(image)
                # TODO replace image snippet
            else:
                logger.warn("src found not starting with images/ src: {}".format(src))
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
        self.textsource = Expression(options.get('textsource', 'text'),
                                   transmogrifier, name, options)
        self.sourcedomain = Expression(options.get('sourcedomain', ''),
                                   transmogrifier, name, options)
        self.targetcontainer_path = Expression(options.get('targetcontainer_path', 'images'),
                                   transmogrifier, name, options)

    def __iter__(self):
        for item in self.previous:
            textsource = self.textsource(item)
            sourcedomain = self.sourcedomain(item)
            targetcontainer_path = self.targetcontainer_path(item)
            images = []
            if textsource in item:
                text = item[textsource]
                parser = LinkedImageConversionParser(target=targetcontainer_path, sourcedomain=sourcedomain)
                images = []
                try:
                    item[textsource] = parser(text)
                    images = parser.items
                except AttributeError:
                    # breakpoint()
                    logger.error('AttributeError')
                    import pdb; pdb.set_trace()
                    yield item
                if images:
                    logger.info('!! found images {}'.format(images))
                else:
                    logger.info('no images found for {}'.format(item['_path']))

            yield item

            for item in images:
                yield item
