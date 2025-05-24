import socket
import json
import threading
from typing import Dict, Any

class NetworkManager:
    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections: Dict[socket.socket, str] = {}
        self.running = False
        
    def start_server(self) -> None:
        """Start the game server"""
        self.socket.bind((self.host, self.port))
        self.socket.listen(2)  # Max 2 players
        self.running = True
        
        # Start accepting connections in a separate thread
        accept_thread = threading.Thread(target=self._accept_connections)
        accept_thread.daemon = True
        accept_thread.start()
        
    def _accept_connections(self) -> None:
        """Accept incoming connections"""
        while self.running:
            try:
                client_socket, _ = self.socket.accept()
                # Start a new thread to handle this client
                client_thread = threading.Thread(target=self._handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
            except:
                break
                
    def _handle_client(self, client_socket: socket.socket) -> None:
        """Handle individual client connections"""
        try:
            # First message should be player info
            data = client_socket.recv(1024).decode()
            player_info = json.loads(data)
            self.connections[client_socket] = player_info['player_id']
            
            while self.running:
                try:
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break
                    
                    game_state = json.loads(data)
                    # Broadcast to other players
                    self._broadcast(game_state, client_socket)
                except:
                    break
        finally:
            self._disconnect_client(client_socket)

    def _broadcast(self, game_state: Dict[str, Any], sender: socket.socket) -> None:
        """Broadcast game state to all other connected clients"""
        for client in self.connections:
            if client != sender:
                try:
                    client.send(json.dumps(game_state).encode())
                except:
                    continue

    def _disconnect_client(self, client_socket: socket.socket) -> None:
        """Handle client disconnection"""
        if client_socket in self.connections:
            del self.connections[client_socket]
        try:
            client_socket.close()
        except:
            pass

    def connect_to_server(self, server_host: str, player_id: str) -> socket.socket:
        """Connect to a game server as a client"""
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, self.port))
        
        # Send initial player info
        player_info = {'player_id': player_id}
        client_socket.send(json.dumps(player_info).encode())
        return client_socket

    def stop(self) -> None:
        """Stop the network manager"""
        self.running = False
        for client in list(self.connections.keys()):
            self._disconnect_client(client)
        self.socket.close() 