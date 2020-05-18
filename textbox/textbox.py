import string
import pygame as pg

ACCEPTED = string.printable
BANNED = [pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN]

class TextBox(object):
    def __init__(self,rect,**kwargs):
        self.rect = pg.Rect(rect)
        self.buffer = []
        self.final = None
        self.rendered = None
        self.render_rect = None
        self.render_area = None
        self.offset = 0
        self.blink = True
        self.blink_timer = 0.0
        self.blink_pos = 0
        self.old_blink = 0
        self.key_cur = 0
        self.key_uni = None
        self.key_timer = 0.0
        self.back_press = False
        self.back_timer = 0.0

        self.ren_1 = 0.0
        self.process_kwargs(kwargs)

    def process_kwargs(self,kwargs):
        defaults = {"id" : None,
                    "command" : None,
                    "active" : True,
                    "color" : pg.Color("white"),
                    "font_color" : pg.Color("black"),
                    "outline_color" : pg.Color("black"),
                    "outline_width" : 2,
                    "active_color" : pg.Color("blue"),
                    "font" : pg.font.Font(None, self.rect.height+4),
                    "clear_on_enter" : False,
                    "inactive_on_enter" : True}
        for kwarg in kwargs:
            if kwarg in defaults:
                defaults[kwarg] = kwargs[kwarg]
            else:
                raise KeyError("InputBox accepts no keyword {}.".format(kwarg))
        self.__dict__.update(defaults)

    def getContents(self):
        return "".join(self.buffer)
    
    def get_event(self,event):
        if event.type == pg.KEYDOWN and self.active:
            if event.key != pg.K_BACKSPACE:
                self.back_press = False
            if event.key != self.key_cur:
                self.key_cur = 0
            if event.key in (pg.K_RETURN,pg.K_KP_ENTER):
                self.execute()
            if event.key == pg.K_LEFT and self.blink_pos > 0:
                self.blink_pos -= 1
                self.blink = True
            if event.key == pg.K_RIGHT and self.blink_pos < len("".join(self.buffer)):
                self.blink_pos += 1
                self.blink = True
            elif event.key == pg.K_BACKSPACE:
                if self.buffer:
                    self.buffer.pop()
                    if not self.back_press:
                        self.back_timer = pg.time.get_ticks()
                        self.back_press = True
            elif event.unicode in ACCEPTED and not event.key in BANNED:
                self.buffer.append(event.unicode)
                self.blink_pos += 1
                if self.key_cur != event.key:
                    self.key_timer = pg.time.get_ticks()
                    self.key_cur = event.key
                    self.key_uni = event.unicode
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

    def execute(self):
        if self.command:
            self.command(self.id,self.final)
        self.active = not self.inactive_on_enter
        if self.clear_on_enter:
            self.buffer = []

    def update(self):
        #Handle the input of holding down backspace to repeatedly remove letters
        if self.active and pg.key.get_pressed()[pg.K_BACKSPACE] and pg.time.get_ticks()-self.back_timer > 500 and self.back_press:
            self.back_timer -= 200
            if self.buffer:
                self.buffer.pop()
        if not pg.key.get_pressed()[pg.K_BACKSPACE]:
            self.back_press = False
        
        #Handle holding down of non-backspace keys
        if self.active and pg.key.get_pressed()[self.key_cur] and pg.time.get_ticks()-self.key_timer > 500:
            self.key_timer -= 200
            self.buffer.append(self.key_uni)
        if not pg.key.get_pressed()[self.key_cur]:
            self.key_cur = 0
            self.key_uni = None

        new = "".join(self.buffer)
        if new != self.final or self.old_blink != self.blink_pos:
            self.old_blink = self.blink_pos
            self.final = new
            self.rendered = self.font.render(self.final, True, self.font_color)
            self.render_rect = self.rendered.get_rect(x=self.rect.x+2,
                                                      centery=self.rect.centery)

            self.ren_1 = self.font.size("".join(self.buffer[0:self.blink_pos]))[0]
            if self.render_rect.width > self.rect.width-6:
                self.offset = self.render_rect.width-(self.rect.width-6)
                self.ren_1 -= self.offset
                #if self.ren_1 < 10:
                #    self.offset += self.ren_1 + 10
                self.render_area = pg.Rect(self.offset,0,self.rect.width-6,
                                           self.render_rect.height)
            else:
                self.offset = 0
                self.render_area = self.rendered.get_rect(topleft=(0,0))
            print(self.ren_1)
        if pg.time.get_ticks()-self.blink_timer > 500:
            self.blink = not self.blink
            self.blink_timer = pg.time.get_ticks()

    def draw(self,surface):
        outline_color = self.active_color if self.active else self.outline_color
        outline = self.rect.inflate(self.outline_width*2,self.outline_width*2)
        surface.fill(outline_color,outline)
        surface.fill(self.color,self.rect)
        if self.rendered:
            surface.blit(self.rendered,self.render_rect,self.render_area)
        if self.blink and self.active:
            curse = self.render_area.copy()
            curse.topleft = self.render_rect.topleft
            if curse.left+self.ren_1 > self.rect.width+self.rect.left-6:
                surface.fill(self.font_color, (self.rect.width+self.rect.left-6, curse.y, 2, curse.h))
            else:
                surface.fill(self.font_color, (curse.left+self.ren_1+1, curse.y, 2, curse.h))
            #surface.fill(self.font_color,(curse.right+1,curse.y,2,curse.h))

