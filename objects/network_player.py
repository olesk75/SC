import pygame as pg
import json
import threading
from typing import Optional, Dict, Any

from objects.players import Player
from objects.network.network import NetworkManager

class NetworkPlayer(Player):
    def __init__(self, pos, heading, ship_type, config, is_host: bool = False) -> None:
        super().__init__(pos, heading, ship_type, config)
        self.network: Optional[NetworkManager] = None
        self.client_socket = None
        self.is_host = is_host
        self.player_id = f"player_{id(self)}"  # Unique ID for this player
        self.other_players: Dict[str, Dict[str, Any]] = {}
        self.last_state_update = pg.time.get_ticks()
        self.running = False

    def init_network(self, host: str = '0.0.0.0', port: int = 5000) -> None:
        """Initialize networking for this player"""
        self.network = NetworkManager(host, port)
        if self.is_host:
            self.network.start_server()
        else:
            self.client_socket = self.network.connect_to_server(host, self.player_id)
            # Start receiving updates in a separate thread
            self.running = True
            receive_thread = threading.Thread(target=self._receive_updates)
            receive_thread.daemon = True
            receive_thread.start()

    def _receive_updates(self) -> None:
        """Receive and process updates from the server"""
        while self.running and self.client_socket:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                game_state = json.loads(data)
                self._update_other_players(game_state)
            except:
                break

    def _update_other_players(self, game_state: Dict[str, Any]) -> None:
        """Update the state of other players based on received data"""
        player_id = game_state.get('player_id')
        if player_id and player_id != self.player_id:
            self.other_players[player_id] = game_state

    def send_state(self) -> None:
        """Send this player's state to the server"""
        if not self.client_socket:
            return

        current_time = pg.time.get_ticks()
        # Only send updates every 16ms (approximately 60 times per second)
        if current_time - self.last_state_update >= 16:
            state = {
                'player_id': self.player_id,
                'pos': (self.rect.x, self.rect.y),
                'heading': self.heading,
                'velocity': self.velocity,
                'direction': self.direction,
                'firing': self.firing,
                'projectiles': [(p.rect.x, p.rect.y) for p in self.projectiles]
            }
            try:
                self.client_socket.send(json.dumps(state).encode())
            except:
                pass
            self.last_state_update = current_time

    def update(self) -> None:
        """Override update to include network state sending"""
        super().update()
        if not self.is_host:
            self.send_state()

    def stop_network(self) -> None:
        """Stop network communication"""
        self.running = False
        if self.network:
            self.network.stop()
        if self.client_socket:
            self.client_socket.close() 