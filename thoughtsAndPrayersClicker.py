#Framework for pygame
import pygame, os, pathlib, random


def init(data):
    data.background = pygame.Surface((data.screen.get_size()))
    data.background.fill((255,255,255))
    data.buttons = []
    folder = "data" #name of folder containing button images
    data.buttons.append(pygame.image.load(os.path.join(folder, 
                                                "button.png")).convert_alpha())
    data.buttons.append(pygame.image.load(os.path.join(folder,
                                        "buttonPressed.png")).convert_alpha())
    data.currentButton = 0
    #set up button rect for collision detection
    data.buttonSize = data.buttons[0].get_size()
    data.buttonXY = (data.width//2 - data.buttonSize[0]//2, data.height//2 + 10)
    data.buttonRect = data.buttons[0].get_rect()
    data.buttonRect = data.buttonRect.move(data.buttonXY)
    #other visuals
    data.logo = pygame.image.load(os.path.join(folder,
                                                    "logo.png")).convert_alpha()
    data.text = pygame.image.load(os.path.join(folder,
                                                    "text.png")).convert_alpha()
    data.spacer = 40
    data.textXY = (data.width//2 - data.text.get_width()//2,
        data.buttonXY[1] + data.buttonSize[1] + data.spacer)
    data.textRect = data.text.get_rect().move(data.textXY)
    data.score = 0
    data.font = pygame.font.SysFont('arial', 32,) #arial may not be best option



def keyDownEvent(event, data):
    pass

def mousePressedEvent(event, data):
    #clicking button
    if event.__dict__['button'] == 1 and \
        data.buttonRect.collidepoint(event.__dict__['pos']):
        data.score += 1
        data.timeSinceClick = 0
        #shut up alexa
        if data.alexaChan.get_busy(): data.alexaChan.stop()
        #small chance of special sound playing on press
        diceRoll = random.randint(1,100)
        if diceRoll == 69:
            data.sans.play()
        else:
            data.ding.play()
        data.currentButton = 1
    #resetting score by pressing text "thoughts and prayers sent..."
    if pygame.mouse.get_pressed()[0] and \
        data.textRect.collidepoint(pygame.mouse.get_pos()):
        data.score = 0
        pygame.mixer.music.stop()
    if (data.score > 1 and data.score % 100 == 0) and \
        not pygame.mixer.music.get_busy():
        #play despacito at multiples of 100
        pygame.mixer.music.play()

def timerFired(data):
    if pygame.mouse.get_pressed()[0] and \
        data.buttonRect.collidepoint(pygame.mouse.get_pos()):
        data.currentButton = 1 #the pressed version of the image
    else: data.currentButton = 0 #the normal non-pressed version

def dirtyRectBlit(data):
    data.screen.blit(data.background, (0,0))
    logoSize = data.logo.get_size()
    data.screen.blit(data.logo, (data.width//2 - logoSize[0]//2,
        data.height//2 - data.logo.get_height() - 20)) #last num is buffer
    #buttons are equal size
    data.buttonXY = (data.width//2 - data.buttonSize[0]//2, data.height//2 + 10)
    data.screen.blit(data.buttons[data.currentButton], data.buttonXY)
    data.screen.blit(data.text, data.textXY)
    #put the score on the screen in default font
    fw, fh = data.font.size(str(data.score))
    fontSurf = data.font.render(str(data.score), True, (0,0,0)) #black counter
    data.screen.blit(fontSurf, (data.width//2 - fw//2, data.buttonXY[1] +
        data.buttonSize[1] + data.spacer + data.text.get_height() + \
                                                        data.spacer//2))


def blitMovers(data):
    pass

##Mixer stuff##
def loadSoundBank(dirPath):
    #returns a list of pygame sounds from ogg files at dirPath
    bank = []
    for file in os.listdir(os.path.join(dirPath)):
        if file.endswith(".ogg"):
            bank.append(pygame.mixer.Sound(os.path.join(dirPath,file)))
    return bank

## Pygame frame work ##

def run(width=680, height=500, fullScreen=False):
    #given width and height are effectively minimum values
    pygame.init()

    class Struct(): pass
    data = Struct()

    if fullScreen:
        fullScreen = pygame.FULLSCREEN
    else:
        fullScreen = 0

    data.screen=pygame.display.set_mode((width,height), fullScreen) 
    data.screenrect = data.screen.get_rect()
    data.width = data.screen.get_width()
    data.height = data.screen.get_height()

    init(data)       
    dirtyRectBlit(data)

    ##mixer stuff##
    pygame.mixer.pre_init()
    pygame.mixer.music.load(os.path.join("data", "despacito.wav"))
    data.alexaChan = pygame.mixer.Channel(0)
    dirPath = pathlib.PurePath("data", "alexaVoice") #location of alexa sounds
    alexaSoundBank = loadSoundBank(dirPath)
    data.ding = pygame.mixer.Sound(os.path.join("data", "buttonNoise",
                                                                "ding.ogg"))
    data.sans = pygame.mixer.Sound(os.path.join("data", "buttonNoise",
                                                                "sans.ogg"))


    data.clock = pygame.time.Clock()     #create pygame clock object
    mainloop = True
    FPS = 20               # desired max. framerate in frames per second. 
    playtime = 0
    data.timeSinceClick = 0
    while mainloop:
        milliseconds = data.clock.tick(FPS)  # millisecs passed since last frame
        data.seconds = milliseconds / 1000.0 # seconds passed since last frame 
        playtime += data.seconds #total playtime
        data.timeSinceClick += data.seconds
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousePressedEvent(event, data)
            if event.type == pygame.QUIT:
                mainloop = False # pygame window closed by user
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False # user pressed ESC

                #debug key controls########
                # print(data.timeSinceClick)
                # if event.key == pygame.K_m:
                #     data.alexaChan.play(random.choice(alexaSoundBank))
                # if event.key == pygame.K_s:
                #     data.score += 90
                # if event.key == pygame.K_q:
                #     data.timeSinceClick += 15
                # if event.key == pygame.K_s:
                #     data.sans.play()
                # else: keyDownEvent(event, data) 

        alexaPatienceTime = 20 #max time alexa will wait before yelling at you
        #   for being heartless and not sending thoughts and prayers
        if data.timeSinceClick >= alexaPatienceTime and \
            not data.alexaChan.get_busy():
            data.alexaChan.play(random.choice(alexaSoundBank))
            data.timeSinceClick = -10 #to provide some buffer time if idle

        pygame.display.set_caption("Amazon Thoughts and Prayers")

        #paint current location of items about to move (or just blit the whole
        #   bg)
        dirtyRectBlit(data)
        #move the items
        timerFired(data)
        #paint moved items
        blitMovers(data)

        pygame.display.flip()          # update the screen
    pygame.quit()

run(0,0, True)