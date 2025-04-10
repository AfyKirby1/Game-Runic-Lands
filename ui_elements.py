import pygame

class Label:
    def __init__(self, text, x, y, font, color, align='center', tag=None):
        self.font = font
        self.color = color
        self.tag = tag
        self.align = align
        # Store initial position parameters
        self._initial_x = x
        self._initial_y = y
        self.set_text(text) # This will create image and rect

    def set_text(self, text):
        self.text = text
        self.image = self.font.render(self.text, True, self.color)
        self._update_rect(self._initial_x, self._initial_y) # Recalculate position based on alignment

    def _update_rect(self, x, y):
        """Calculates the rect based on alignment and the provided x, y"""
        self.rect = self.image.get_rect()
        if self.align == 'center':
            self.rect.center = (x, y)
        elif self.align == 'left':
            self.rect.midleft = (x, y)
        elif self.align == 'right':
             self.rect.midright = (x, y)
        else: # Default to center
            self.rect.center = (x, y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
    def is_button(self):
        """Helper method to check if an element is a button"""
        return False

class Button:
    def __init__(self, text, x, y, width, height, font, colors, action=None, tag=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.colors = colors
        self.action = action
        self.tag = tag
        self.is_hovered = False
        
        # Pre-render text
        self.text_surface = self.font.render(text, True, colors['button_text'])
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        # Draw button background
        color = self.colors['button_hover'] if self.is_hovered else self.colors['button']
        pygame.draw.rect(screen, color, self.rect)
        
        # Draw border
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        # Draw text
        screen.blit(self.text_surface, self.text_rect)
        
    def set_text(self, new_text):
        self.text = new_text
        self.text_surface = self.font.render(new_text, True, self.colors['button_text'])
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)

    def is_button(self):
        """Helper method to check if an element is a button"""
        return True

class ToggleButton(Button):
    def __init__(self, initial_state, x, y, w, h, font, colors, action=None, tag=None):
        super().__init__("On" if initial_state else "Off", x, y, w, h, font, colors, action, tag)
        self.is_on = initial_state

    def toggle(self):
        self.is_on = not self.is_on
        self.set_text("On" if self.is_on else "Off")

    def handle_event(self, event):
        """Handle mouse events for the toggle button"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.toggle()
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return False

    def draw(self, screen):
        # Change color based on state and hover
        if self.is_on:
            base_color = self.colors.get('toggle_on', (50, 150, 50))
            hover_color = self.colors.get('toggle_on_hover', (80, 180, 80))
        else:
            base_color = self.colors.get('toggle_off', (150, 50, 50))
            hover_color = self.colors.get('toggle_off_hover', (180, 80, 80))

        button_color = hover_color if self.is_hovered else base_color
        pygame.draw.rect(screen, button_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, self.colors.get('button_border', (200, 200, 200)), self.rect, 1, border_radius=5)
        screen.blit(self.text_surface, self.text_rect)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, current_val, colors, action=None, step=0.1, tag=None):
        self.rect = pygame.Rect(x, y - h // 2, w, h) # Slider track rect
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.colors = colors
        self.action = action
        self.tag = tag
        self.dragging = False
        self.handle_radius = h # Make handle easier to grab
        # Ensure initial value is set correctly
        self._value = current_val # Use internal variable to avoid triggering set_value logic initially if not needed
        self._update_handle_rect() # Calculate initial handle position

    @property
    def value(self):
        return self._value

    def set_value(self, value):
        new_value = max(self.min_val, min(self.max_val, value))
        # Snap to steps if step is defined
        if self.step > 0:
            new_value = round(new_value / self.step) * self.step
            # Re-clamp after stepping
            new_value = max(self.min_val, min(self.max_val, new_value))

        if self._value != new_value:
            self._value = new_value
            self._update_handle_rect()
            return True # Indicate value changed
        return False

    def _update_handle_rect(self):
         # Calculate handle position based on value
        # Avoid division by zero if min_val == max_val
        range_val = (self.max_val - self.min_val)
        if range_val == 0:
             ratio = 0.5
        else:
             ratio = (self._value - self.min_val) / range_val

        handle_x = self.rect.x + ratio * self.rect.width
        self.handle_rect = pygame.Rect(0, 0, self.handle_radius, self.handle_radius)
        self.handle_rect.center = (int(handle_x), self.rect.centery)


    def handle_event(self, event):
        updated = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click is on or near the handle OR the track
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                updated = self._update_value_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                # No need to update here, it was updated on mouse down/motion
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                updated = self._update_value_from_pos(event.pos[0])
        return updated

    def _update_value_from_pos(self, mouse_x):
        # Calculate value based on mouse position relative to slider track
        relative_x = max(0, min(self.rect.width, mouse_x - self.rect.x))
        ratio = relative_x / self.rect.width if self.rect.width > 0 else 0
        new_value = self.min_val + ratio * (self.max_val - self.min_val)
        return self.set_value(new_value) # Use set_value to handle clamping and stepping

    def draw(self, screen):
        # Draw slider track
        track_color = self.colors.get('slider_bg', (50, 50, 100))
        pygame.draw.rect(screen, track_color, self.rect, border_radius=self.rect.height // 2)
        # Draw handle
        handle_color = self.colors.get('slider_handle', (100, 100, 255))
        pygame.draw.circle(screen, handle_color, self.handle_rect.center, self.handle_radius // 2)
        # Optional: Add border to handle
        border_color = self.colors.get('button_border', (200, 200, 200))
        pygame.draw.circle(screen, border_color, self.handle_rect.center, self.handle_radius // 2, 1)
        
    def is_button(self):
        """Helper method to check if an element is a button"""
        return False
