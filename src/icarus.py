import json
from os.path import dirname, join
from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.properties import AliasProperty, DictProperty
import os

# late import to prevent recursion
CoreImage = None


class Icarus(EventDispatcher):
    """Modified version of Kivy's Atlas class.
    """

    textures = DictProperty({})

    def _get_filename(self):
        return self._filename

    filename = AliasProperty(_get_filename, None)

    def __init__(self, filename):
        self._filename = filename
        super(Icarus, self).__init__()

    def __getitem__(self, key):
        if key in self.textures:
            return self.textures[key]
        self.load(key)
        return self.textures[key]

    def __contains__(self, item):
        return item in self.textures

    def load(self, image_name):
        # late import to prevent recursive import.
        global CoreImage
        if CoreImage is None:
            from kivy.core.image import Image as CoreImage

        # must be a name finished by .atlas ?
        filename = self._filename
        assert(filename.endswith('.atlas'))
        filename = filename.replace('/', os.sep)

        Logger.debug('Atlas: Load <%s>' % filename)
        with open(filename, 'r') as fd:
            meta = json.load(fd)

        d = dirname(filename)
        textures = {}
        found = None
        ids_found = None
        for sub, ids in meta.items():
            if image_name in ids:
                found = sub
                ids_found = ids
        if found is None:
            Logger.error('Icarus: ' + image_name + ' not found')
        subfilename = join(d, found)
        Logger.debug('Atlas: Load <%s>' % subfilename)

        # load the image
        ci = CoreImage(subfilename)
        atlas_texture = ci.texture

        # for all the uid, load the image, get the region, and put
        # it in our dict.
        for meta_id, meta_coords in ids_found.items():
            x, y, w, h = meta_coords
            textures[meta_id] = atlas_texture.get_region(*meta_coords)

        self.textures = textures
