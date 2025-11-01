from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

H1_MAC = "00:00:00:00:00:01"
H3_MAC = "00:00:00:00:00:03"

def _handle_ConnectionUp (event):
    log.info("Switch %s conectado", event.dpid)

    # Regla 1: bloquear h1 -> h3
    fm1 = of.ofp_flow_mod()
    fm1.match.dl_src = H1_MAC
    fm1.match.dl_dst = H3_MAC
    # Sin acciones => drop
    event.connection.send(fm1)

    # Regla 2: bloquear h3 -> h1
    fm2 = of.ofp_flow_mod()
    fm2.match.dl_src = H3_MAC
    fm2.match.dl_dst = H1_MAC
    event.connection.send(fm2)

def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    log.info("Módulo blocking.py cargado")
