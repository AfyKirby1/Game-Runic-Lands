"""
State Manager for Runic Lands
Handles game state transitions and maintains the current state
"""

import pygame
from enum import Enum, auto
from typing import Dict, Callable, List, Any, Optional

class GameState(Enum):
    """Game states that control the flow of the game"""
    MAIN_MENU = auto()
    SINGLE_PLAYER = auto()
    LOCAL_COOP = auto()
    OPTIONS = auto()
    PAUSED = auto()
    INVENTORY = auto()
    GAME_OVER = auto()
    LOADING = auto()
    QUIT = auto()

class StateManager:
    """
    Manages game state transitions and ensures proper
    state handling including enter/exit actions
    """
    
    def __init__(self):
        """Initialize the state manager"""
        self.current_state = GameState.MAIN_MENU
        self.previous_state = None
        self.state_stack = []  # For nested states like PAUSE -> OPTIONS -> PAUSE
        
        # Event handlers by state
        self.event_handlers: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        
        # Update handlers by state
        self.update_handlers: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        
        # Draw handlers by state
        self.draw_handlers: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        
        # State transition handlers (called when entering/exiting a state)
        self.enter_handlers: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        self.exit_handlers: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        
        # Data storage for states
        self.state_data: Dict[GameState, Any] = {}
    
    def change_state(self, new_state: GameState, push_to_stack: bool = False):
        """
        Change the current game state
        If push_to_stack is True, the current state is saved on the stack
        """
        if new_state == self.current_state:
            return False
            
        # Execute exit handlers for current state
        for handler in self.exit_handlers[self.current_state]:
            handler()
            
        # Save previous state
        self.previous_state = self.current_state
        
        # Push to stack if requested
        if push_to_stack:
            self.state_stack.append(self.current_state)
            
        # Change state
        self.current_state = new_state
        
        # Execute enter handlers for new state
        for handler in self.enter_handlers[self.current_state]:
            handler()
            
        return True
    
    def pop_state(self):
        """Return to the previous state from the stack"""
        if not self.state_stack:
            return False
            
        previous = self.state_stack.pop()
        return self.change_state(previous)
    
    def register_event_handler(self, state: GameState, handler: Callable):
        """Register an event handler function for a specific state"""
        if handler not in self.event_handlers[state]:
            self.event_handlers[state].append(handler)
    
    def register_update_handler(self, state: GameState, handler: Callable):
        """Register an update handler function for a specific state"""
        if handler not in self.update_handlers[state]:
            self.update_handlers[state].append(handler)
    
    def register_draw_handler(self, state: GameState, handler: Callable):
        """Register a draw handler function for a specific state"""
        if handler not in self.draw_handlers[state]:
            self.draw_handlers[state].append(handler)
    
    def register_enter_handler(self, state: GameState, handler: Callable):
        """Register a handler function called when entering a state"""
        if handler not in self.enter_handlers[state]:
            self.enter_handlers[state].append(handler)
    
    def register_exit_handler(self, state: GameState, handler: Callable):
        """Register a handler function called when exiting a state"""
        if handler not in self.exit_handlers[state]:
            self.exit_handlers[state].append(handler)
    
    def set_state_data(self, state: GameState, key: str, value: Any):
        """Store data for a specific state"""
        if state not in self.state_data:
            self.state_data[state] = {}
        self.state_data[state][key] = value
    
    def get_state_data(self, state: GameState, key: str, default: Any = None) -> Any:
        """Retrieve data for a specific state"""
        if state not in self.state_data:
            return default
        return self.state_data[state].get(key, default)
    
    def handle_events(self, events: List[pygame.event.Event]):
        """Process events for the current state"""
        for handler in self.event_handlers[self.current_state]:
            for event in events:
                if handler(event):
                    break  # Event was handled, skip to next event
    
    def update(self, dt: float):
        """Update game logic for the current state"""
        for handler in self.update_handlers[self.current_state]:
            handler(dt)
    
    def draw(self, screen: pygame.Surface):
        """Draw the current state to the screen"""
        for handler in self.draw_handlers[self.current_state]:
            handler(screen)
    
    def quit_game(self):
        """Change to QUIT state to exit the game"""
        self.change_state(GameState.QUIT) 