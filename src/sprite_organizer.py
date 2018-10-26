class SpriteOrganizer:

    def __init__(self):
        self.sprites = []

    def add_sprite(self, sprite):
        if sprite in self.sprites:
            self.sprites.remove(sprite)
        self.sprites.insert(0, sprite)

    def get_sprites(self):
        return self.sprites
