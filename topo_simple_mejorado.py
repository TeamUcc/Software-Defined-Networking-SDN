"""
Topología simple para Mininet
Autor: Laboratorio SDN
Descripción: Define una topología con 1 switch y 3 hosts

Este archivo demuestra cómo crear topologías de red
personalizadas en Mininet usando Python.
"""

from mininet.topo import Topo
from mininet.link import TCLink  # Para enlazar con parámetros de tráfico


class SimpleTopology(Topo):
    """
    Topología de estrella simple (star topology):
    
          h1
          |
    h2 -- s1 -- h3
    
    Todos los hosts están conectados a un único switch.
    """
    
    def build(self):
        """Construir la topología."""
        # Crear un switch
        s1 = self.addSwitch('s1')
        
        # Crear tres hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        
        # Conectar hosts al switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        
        # Alternativa con parámetros de enlace (descomentar para usar):
        # self.addLink(h1, s1, bw=10)      # 10 Mbps bandwidth
        # self.addLink(h2, s1, bw=10, delay='5ms')
        # self.addLink(h3, s1, bw=10, loss=1)  # 1% pérdida


class ExtendedTopology(Topo):
    """
    Topología extendida con 2 switches (opcional para extensión):
    
    h1 --- s1 --- s2 --- h3
    |             |
    h2            h4
    """
    
    def build(self):
        """Construir topología con dos switches."""
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        # Hosts conectados a s1
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        
        # Hosts conectados a s2
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        
        # Conectar hosts a switches
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        
        # Conectar switches entre sí
        self.addLink(s1, s2)


# Registrar topologías para que Mininet las encuentre
topos = {
    'simple': SimpleTopology,
    'extended': ExtendedTopology
}

# Uso:
# sudo mn --custom topo_simple.py --topo=simple --controller=remote
# sudo mn --custom topo_simple.py --topo=extended --controller=remote
