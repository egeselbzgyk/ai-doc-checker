#!/usr/bin/env python3
"""
SSH Tunnel Manager for Qwen Server Connection
Automatically establishes and maintains SSH tunnel to ki4.mni.thm.de
"""

import subprocess
import time
import socket
import threading
import atexit
import os
import signal

class SSHTunnelManager:
    """Manages SSH tunnel to Qwen server"""
    
    def __init__(self, 
                 username: str = "ebzg73",
                 remote_host: str = "ki4.mni.thm.de", 
                 local_port: int = 5000,
                 remote_port: int = 5000):
        """
        Initialize SSH tunnel manager
        
        Args:
            username: SSH username
            remote_host: Remote server hostname
            local_port: Local port to forward
            remote_port: Remote port to forward to
        """
        self.username = username
        self.remote_host = remote_host
        self.local_port = local_port
        self.remote_port = remote_port
        self.ssh_process = None
        self.is_connected = False
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def is_port_available(self, port: int) -> bool:
        """Check if port is available on localhost"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except socket.error:
            return False
    
    def is_tunnel_working(self) -> bool:
        """Test if tunnel is working by connecting to localhost:5000"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex(('localhost', self.local_port))
                return result == 0
        except:
            return False
    
    def start_tunnel(self) -> bool:
        """
        Start SSH tunnel
        
        Returns:
            True if tunnel started successfully
        """
        if self.is_connected and self.is_tunnel_working():
            print("SSH tunnel already active")
            return True
        
        # Check if port is already in use
        if not self.is_port_available(self.local_port):
            if self.is_tunnel_working():
                print(f"Port {self.local_port} already forwarded (tunnel exists)")
                self.is_connected = True
                return True
            else:
                print(f"Port {self.local_port} is in use but not responding")
                return False
        
        try:
            print(f"Starting SSH tunnel to {self.username}@{self.remote_host}...")
            
            # SSH tunnel command
            ssh_cmd = [
                'ssh',
                '-L', f'{self.local_port}:localhost:{self.remote_port}',
                '-N',  # Don't execute remote command
                '-T',  # Disable pseudo-terminal allocation
                '-o', 'ConnectTimeout=10',
                '-o', 'ServerAliveInterval=60',
                '-o', 'ServerAliveCountMax=3',
                '-o', 'ExitOnForwardFailure=yes',
                f'{self.username}@{self.remote_host}'
            ]
            
            # Start SSH process
            self.ssh_process = subprocess.Popen(
                ssh_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            # Wait a moment for tunnel to establish
            time.sleep(3)
            
            # Check if tunnel is working
            if self.is_tunnel_working():
                self.is_connected = True
                print("SSH tunnel established successfully")
                print(f"   localhost:{self.local_port} -> {self.remote_host}:{self.remote_port}")
                return True
            else:
                print("SSH tunnel failed to establish")
                self.cleanup()
                return False
                
        except Exception as e:
            print(f"Failed to start SSH tunnel: {e}")
            self.cleanup()
            return False
    
    def stop_tunnel(self):
        """Stop SSH tunnel"""
        if self.ssh_process:
            try:
                self.ssh_process.terminate()
                self.ssh_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ssh_process.kill()
                self.ssh_process.wait()
            
            self.ssh_process = None
            self.is_connected = False
            print("SSH tunnel stopped")
    
    def cleanup(self):
        """Cleanup on exit"""
        if self.is_connected:
            self.stop_tunnel()
    
    def ensure_connection(self) -> bool:
        """
        Ensure tunnel is active, start if needed
        
        Returns:
            True if tunnel is active
        """
        if not self.is_connected or not self.is_tunnel_working():
            return self.start_tunnel()
        return True

# Global tunnel manager instance
tunnel_manager = None

def get_tunnel_manager() -> SSHTunnelManager:
    """Get or create global tunnel manager"""
    global tunnel_manager
    if tunnel_manager is None:
        tunnel_manager = SSHTunnelManager()
    return tunnel_manager

def ensure_qwen_connection() -> bool:
    """
    Ensure Qwen server connection is available
    
    Returns:
        True if connection is available
    """
    manager = get_tunnel_manager()
    return manager.ensure_connection()

if __name__ == "__main__":
    # Test SSH tunnel
    print("Testing SSH tunnel...")
    
    manager = SSHTunnelManager()
    
    if manager.start_tunnel():
        print("Tunnel test successful")
        
        # Test connection
        try:
            import requests
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("Qwen server is accessible")
                print(f"Response: {response.json()}")
            else:
                print(f"Qwen server responded with status {response.status_code}")
        except Exception as e:
            print(f"Failed to connect to Qwen server: {e}")
        
        # Keep tunnel open for testing
        try:
            print("Tunnel is active. Press Ctrl+C to stop...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping tunnel...")
    else:
        print("Tunnel test failed") 