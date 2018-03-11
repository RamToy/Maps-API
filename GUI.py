import pygame


class GUI:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def render(self, surface):
        for element in self.elements:
            render = getattr(element, "render", None)
            if callable(render):
                element.render(surface)

    def update(self):
        for element in self.elements:
            update = getattr(element, "update", None)
            if callable(update):
                element.update()

    def get_event(self, event):
        for element in self.elements:
            get_event = getattr(element, "get_event", None)
            if callable(get_event):
                element.get_event(event)

    def clear(self):
        self.elements.clear()


class Label:
    def __init__(self, rect, rect_color, text, font_color, center=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.rect_color = rect_color
        self.font_color = font_color
        self.center = center
        self.font = pygame.font.Font(None, self.rect.height - 4)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface):
        if self.rect_color != -1:
            surface.fill(self.rect_color, self.rect)
        self.rendered_text = self.font.render(self.text, 10, self.font_color)
        if self.center:
            self.rendered_rect = self.rendered_text.get_rect(center=self.rect.center)
        else:
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
        surface.blit(self.rendered_text, self.rendered_rect)


class Button(Label):
    def __init__(self, rect, rect_color, text, font_color):
        super().__init__(rect, rect_color, text, font_color)
        self.pressed = False

    def render(self, surface):
        surface.fill(self.rect_color, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        if not self.pressed:
            color1 = pygame.Color("white")
            color2 = pygame.Color("black")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 5, centery=self.rect.centery)
        else:
            color1 = pygame.Color("black")
            color2 = pygame.Color("white")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 7, centery=self.rect.centery + 2)

        pygame.draw.rect(surface, color1, self.rect, 2)
        pygame.draw.line(surface, color2, (self.rect.right - 1, self.rect.top),
                         (self.rect.right - 1, self.rect.bottom), 2)
        pygame.draw.line(surface, color2, (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right, self.rect.bottom - 1), 2)
        surface.blit(self.rendered_text, self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self.rect.collidepoint(*event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False


class ImageButton:
    def __init__(self, rect, rect_color, image, center=False):
        self.rect = pygame.Rect(rect)
        self.rect_color = rect_color
        self.image = image
        self.center = center
        self.pressed = False
        self.rendered_rect = None

    def render(self, surface):
        surface.fill(self.rect_color, self.rect)
        if not self.pressed:
            color1 = pygame.Color("white")
            color2 = pygame.Color("black")
            if self.center:
                self.rendered_rect = self.image.get_rect(center=self.rect.center)
            else:
                self.rendered_rect = self.image.get_rect(x=self.rect.x, centery=self.rect.centery)
        else:
            color1 = pygame.Color("black")
            color2 = pygame.Color("white")
            if self.center:
                self.rendered_rect = self.image.get_rect(centerx=self.rect.centerx + 2,
                                                         centery=self.rect.centery + 2)
            else:
                self.rendered_rect = self.image.get_rect(x=self.rect.x + 2, centery=self.rect.centery + 2)

        pygame.draw.rect(surface, color1, self.rect, 2)
        pygame.draw.line(surface, color2, (self.rect.right - 1, self.rect.top),
                         (self.rect.right - 1, self.rect.bottom), 2)
        pygame.draw.line(surface, color2, (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right, self.rect.bottom - 1), 2)
        surface.blit(self.image, self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self.rect.collidepoint(*event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False


class TextBox(Label):
    def __init__(self, rect, rect_color, text, font_color):
        super().__init__(rect, rect_color, text, font_color)
        self.active = False
        self.blink = False
        self.blink_timer = 0

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.active = False
                self.text = ""
            elif event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
            else:
                self.text += event.unicode
                if self.rendered_rect.width > self.rect.width:
                    self.text = self.text[:-1]
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(*event.pos)

    def update(self):
        if pygame.time.get_ticks() - self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def render(self, surface):
        super(TextBox, self).render(surface)
        if self.active and self.blink:
            pygame.draw.line(surface, [255 - self.font_color[c] for c in range(3)],
                             (self.rendered_rect.right + 2, self.rendered_rect.top + 2),
                             (self.rendered_rect.right + 2, self.rendered_rect.bottom - 2))
