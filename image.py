import pygame
images = []
images2 = []
image1 = pygame.image.load("white_pawn.png")
image2 = pygame.image.load("black_pawn.png")
image3 = pygame.image.load("white_rook.png")
image4 = pygame.image.load("black_rook.png")
image5 = pygame.image.load("white_king.png")
image6 = pygame.image.load("black_king.png")
image7 = pygame.image.load("white_knight.png")
image8 = pygame.image.load("black_knight.png")
image9 = pygame.image.load("white_bishop.png")
image10 = pygame.image.load("black_bishop.png")
image11 = pygame.image.load("white_queen.png")
image12 = pygame.image.load("black_queen.png")
images=[image1, image2, image3, image4, image5, image6, image7, image8, image9, image10, image11, image12]
for i in range(len(images)):
    images[i].set_colorkey((0, 0, 0))
    images[i]= pygame.transform.scale(images[i], (50, 50))
    images2.append(pygame.transform.scale(images[i], (100, 100)))
