"""
Módulo de bloqueo de tráfico SDN
Autor: Laboratorio POX
Descripción: Crea reglas de flujo para bloquear tráfico entre hosts específicos

Este módulo demuestra cómo usar el controlador POX para implementar
una política de seguridad que bloquea paquetes entre dos direcciones MAC.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

# Dirección MAC de h1 y h3
# En una topología single,3: h1=00:00:00:00:00:01, h2=00:00:00:00:00:02, h3=00:00:00:00:00:03
H1_MAC = "00:00:00:00:00:01"
H3_MAC = "00:00:00:00:00:03"


def _handle_ConnectionUp(event):
    """
    Manejador para el evento cuando el switch se conecta al controlador.
    
    Args:
        event: Contiene información del switch (dpid, connection, etc.)
    """
    log.info("Switch %s conectado", event.dpid)
    
    # ========== REGLA 1: Bloquear h1 -> h3 ==========
    # Crear un modificador de flujo (ofp_flow_mod)
    fm1 = of.ofp_flow_mod()
    
    # Condición de coincidencia (Match)
    fm1.match.dl_src = H1_MAC   # Origen: h1
    fm1.match.dl_dst = H3_MAC   # Destino: h3
    
    # NO establecer acciones = El switch descarta (DROP) los paquetes
    # Si tuviera fm1.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
    # sería reenviar al controlador
    
    # Enviar la regla al switch
    event.connection.send(fm1)
    log.info("Regla instalada: h1->h3 BLOQUEADA (DROP)")
    
    # ========== REGLA 2: Bloquear h3 -> h1 ==========
    fm2 = of.ofp_flow_mod()
    fm2.match.dl_src = H3_MAC   # Origen: h3
    fm2.match.dl_dst = H1_MAC   # Destino: h1
    # Sin acciones = DROP
    event.connection.send(fm2)
    log.info("Regla instalada: h3->h1 BLOQUEADA (DROP)")


def launch():
    """
    Función llamada por POX al cargar este módulo.
    Registra el manejador de eventos.
    """
    # Registrar el manejador para el evento ConnectionUp
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    log.info("Módulo blocking.py cargado - Bloqueando tráfico h1<->h3")
