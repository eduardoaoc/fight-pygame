import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps):
        self.player= player
        self.size= data[0]
        self.image_scale= data[1]
        self.offset= data[2]
        self.flip= flip
        self.animation_list= self.load_images(sprite_sheet, animation_steps)
        self.action= 0 #0:idle #1:run #2:jump #3:attack1 #4:attack2 #5:hit #6:death
        self.frame_index= 0 
        self.image= self.animation_list[self.action][self.frame_index]
        self.update_time= pygame.time.get_ticks()
        #Position of player - cada retângulo representa um player
        self.rect= pygame.Rect((x, y, 80, 180))
        self.vel_y= 0 
        self.running= False
        self.jump = False
        self.attacking= False
        self.attack_type= 0
        self.attack_cooldown= 0
        self.hit= False
        self.health = 100
        self.alive= True

    def load_images(self, sprite_sheet, animation_steps):
        #extract images from spritsheet 
        animation_list= []
        for y, animation in enumerate(animation_steps):
            temp_img_list= []
            for x in range(animation):
                temp_img= sprite_sheet.subsurface(x  * self.size, y * self.size, self.size, self.size)            
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list       

    #function for movement - função para movimentação 
    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED= 10 
        GRAVITY= 2
        dx= 0 
        dy= 0 
        self.attack_type= 0
        self.running= False

        #get keypresses 
        key= pygame.key.get_pressed()

        #can only perform other actions if not currently attacking 
        #só pode executar outras ações se não estiver atacando no momento
        if self.attacking == False and self.alive == True and round_over == False:
            #check player 1 controls 
            if self.player == 1:
                #movement 
                if key[pygame.K_a]:
                    dx= -SPEED
                    self.running= True
                if key[pygame.K_d]:
                    dx= SPEED
                    self.running= True

                #jump 
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y= - 30
                    self.jump= True 

                #attack 
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)

                    #determine witch attack type was used - determina o tipi de ataque que será usado 
                    if key[pygame.K_r]:
                        self.attack_type= 1
                    if key[pygame.K_t]:
                        self.attack_type= 2



            #check player 2 controls 
            if self.player == 2:
                #movement 
                if key[pygame.K_LEFT]:
                    dx= -SPEED
                    self.running= True
                if key[pygame.K_RIGHT]:
                    dx= SPEED
                    self.running= True

                #jump 
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y= - 30
                    self.jump= True 

                #attack 
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)

                    #determine witch attack type was used - determina o tipi de ataque que será usado 
                    if key[pygame.K_KP1]:
                        self.attack_type= 1
                    if key[pygame.K_KP2]:
                        self.attack_type= 2


        #apply gravity - gravidade
        self.vel_y += GRAVITY

        dy += self.vel_y

        #ensure player stays on screen - garantir que o personagem está parado na tela
        if self.rect.left + dx < 0:
            dx= -self.rect.left
        if self.rect.right + dx > screen_width:
            dx= screen_width - self.rect.right
            #definição do contato ao solo - contact at floor
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y= 0 
            self.jump= False
            dy= screen_height - 110 - self.rect.bottom

        #ensure players face each other - certifique-se de que os jogadores se enfrentam
        if target.rect.centerx > self.rect.centerx:
            self.flip= False
        else:
            self.flip= True    

        #apply attack cooldown - aplicando o cooldown de ataque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        #update player position - atualiza a posição do personagem 
        self.rect.x += dx 
        self.rect.y += dy 


    #handle animation updates
    #lidar com atualizações de animação
    def update(self):
        #check what action the player is performing  
        #verificar que ação o jogador está realizando
        if self.health <= 0:
            self.health= 0
            self.alive= False
            self.update_action(6)# 6death
        elif self.hit == True:
            self.update_action(5) #5 hit
        elif self.attacking == True: 
            if self.attack_type == 1:
                self.update_action(3) #3 attack 1
            elif self.attack_type == 2:
                self.update_action(4)   #4 attack 2
        elif self.jump == True:
            self.update_action(2) #2 jump
        elif self.running == True:
            self.update_action(1) #0 run
        else:
            self.update_action(0) #0 idle

        animation_cooldown= 50

        #update image
        self.image= self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update 
        #verifique se já passou tempo suficiente desde a última atualização
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        #check if the animation has finished
        #verificar se a animação terminou
        if self.frame_index >= len(self.animation_list[self.action]):
            #if the player is dead then end the animation - 
            if self.alive == False:
                self.frame_index= len(self.animation_list[self.action]) - 1
            else:    
                self.frame_index= 0 
            #check if an attack was executed
            #verificar se um ataque foi executado
            if self.action == 3 or self.action == 4:
                self.attacking= False
                self.attack_cooldown= 20
            #check if damage was taken     
            if self.action == 5:
                self.hit = False
                #if the player was in the middle opf an attack, then the attack is stopped
                ##se o jogador estava no meio opf um ataque, então o ataque é interrompido
                self.attacking= False
                self.attack_cooldown= 20



    #attack function 
    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking= True
            #Rect - PARA CRIAR Retângulos
            attacking_rect= pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip),  self.rect.y, 2 * self.rect.width, self.rect.height)
            #colisão de ataques - colision of attack
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit= True


    def update_action(self, new_action):
        #check if the new action is different to the previous one 
        #verificar se a nova ação é diferente da anterior
        if new_action != self.action:
            self.action= new_action
            #update animation settings
            self.frame_index= 0
            self.update_time= pygame.time.get_ticks()

    #create fuction for drawing fighters - função para desenhar os lutadores    
    def draw(self, surface):
        img= pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))

