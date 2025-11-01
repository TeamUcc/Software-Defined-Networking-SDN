# 🎓 GUÍA DE RESPUESTAS Y EXTENSIONES

---

## ✅ RESPUESTAS ESPERADAS A PREGUNTAS DE REFLEXIÓN

### NIVEL 1: Conceptos Básicos

**P1: ¿Qué es un Packet-In?**

Respuesta esperada:
- Es un mensaje OpenFlow que envía el switch al controlador
- Se genera cuando un paquete NO coincide con ninguna regla de flujo
- El controlador debe decidir qué hacer
- Es el mecanismo de comunicación entre plano de datos y control

**P2: ¿Cómo el controlador POX "aprende" las direcciones MAC?**

Respuesta esperada:
- Cuando llega un Packet-In, examina la dirección MAC de origen
- Asocia esa MAC con el puerto del switch
- Instala una regla (Flow Mod) para ese par origen-destino
- Próximos paquetes de ese origen usan la regla (sin Packet-In)

Ejemplo:
```
Paquete: h1→h2 LLEGA SIN REGLA
    ↓
POX ve: MAC origen=00:00:00:00:00:01 en puerto 1
    ↓
POX aprende: "Si ves 01 de origen, es puerto 1"
    ↓
POX instala: Regla para 01→* con acción OUT:1
```

**P3: ¿Qué sucede cuando llega un paquete sin regla?**

Respuesta esperada:
- El switch no puede decidir qué hacer
- Envía el paquete completo al controlador (Packet-In)
- El controlador examina el paquete
- Toma una decisión (aprender, bloquear, reenviar)
- Instala una regla para próximos paquetes similares
- El switch envía el paquete original según la decisión

---

### NIVEL 2: Comparación Hub vs Switch

**P4: ¿Qué diferencia observaste entre hub y switch? ¿Por qué?**

Respuesta esperada:

| Aspecto | Hub | Switch |
|--------|-----|--------|
| Regla | 1 sola regla | N reglas (1 por par MACs) |
| Acción | output:ALL o FLOOD | output:X (puerto específico) |
| Tráfico | Alto (duplicado) | Bajo (optimizado) |
| Búsqueda | O(1) siempre | O(1) pero selectivo |
| Ancho de banda | Ineficiente | Eficiente |

**Por qué?**
- Hub no aprende: reenvía por todos los puertos
- Switch aprende direcciones MAC: reenvía solo al correcto
- Switch es más inteligente (capa 2)

**P5: ¿Qué implicaciones tiene el hub para la seguridad?**

Respuesta esperada:
- Todos ven todo el tráfico (flooding)
- Sniffer en h2 ve paquetes destinados a h3
- Información viaja por todos los puertos
- Posible spoofing fácil
- No hay privacidad en la red

---

### NIVEL 3: Políticas de Seguridad

**P6: ¿Cómo podrías extender blocking.py para priorizar tráfico (QoS)?**

Respuesta esperada:

```python
# En lugar de DROP, establecer prioridad
def _handle_ConnectionUp(event):
    log.info("Switch %s conectado", event.dpid)
    
    # Regla 1: h1→h3 con baja prioridad (20)
    fm1 = of.ofp_flow_mod()
    fm1.priority = 20  # Baja prioridad
    fm1.match.dl_src = H1_MAC
    fm1.match.dl_dst = H3_MAC
    fm1.actions.append(of.ofp_action_output(port=3))
    event.connection.send(fm1)
    
    # Regla 2: h1→h2 con alta prioridad (100)
    fm2 = of.ofp_flow_mod()
    fm2.priority = 100  # Alta prioridad
    fm2.match.dl_src = H1_MAC
    fm2.match.dl_dst = H2_MAC
    fm2.actions.append(of.ofp_action_output(port=2))
    event.connection.send(fm2)
```

Cómo funciona:
- Mayor priority = se evalúa primero
- h1→h2 siempre se procesa antes
- Si hay congestion, h1→h2 obtiene ancho de banda

---

## 🚀 EXTENSIONES NIVEL 4+

### Extensión 1: Whitelist en lugar de Blacklist

**Concepto:** En lugar de bloquear algunos hosts, permitir solo comunicación específica

```python
from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

# MACs permitidas
ALLOWED_PAIRS = [
    ("00:00:00:00:00:01", "00:00:00:00:00:02"),  # h1→h2
    ("00:00:00:00:00:02", "00:00:00:00:00:01"),  # h2→h1
    ("00:00:00:00:00:02", "00:00:00:00:00:03"),  # h2→h3
    ("00:00:00:00:00:03", "00:00:00:00:00:02"),  # h3→h2
]

def _handle_ConnectionUp(event):
    log.info("Switch %s conectado con whitelist", event.dpid)
    
    # Instalar reglas PERMITIDAS
    for src_mac, dst_mac in ALLOWED_PAIRS:
        fm = of.ofp_flow_mod()
        fm.match.dl_src = src_mac
        fm.match.dl_dst = dst_mac
        fm.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
        event.connection.send(fm)
    
    # Regla por defecto: DROP todo lo demás
    default_drop = of.ofp_flow_mod()
    default_drop.priority = 0  # Prioridad baja
    # Sin acciones = DROP implícito
    event.connection.send(default_drop)

def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    log.info("Módulo whitelist.py cargado")
```

**Prueba:**
```bash
mininet> h1 ping -c 1 h3  # FALLA - no en whitelist
mininet> h1 ping -c 1 h2  # FUNCIONA - en whitelist
mininet> h3 ping -c 1 h1  # FALLA - no en whitelist
```

---

### Extensión 2: Bloqueo por protocolo (IP)

**Concepto:** Bloquear basado en IP, no solo MAC

```python
from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

def _handle_ConnectionUp(event):
    log.info("Switch %s conectado", event.dpid)
    
    # Bloquear basado en dirección IP
    # h1 = 10.0.0.1, h3 = 10.0.0.3
    fm = of.ofp_flow_mod()
    fm.match.nw_src = "10.0.0.1"  # Cualquier fuente
    fm.match.nw_dst = "10.0.0.3"  # Solo destino h3
    fm.match.nw_proto = 1          # ICMP (ping)
    # Sin acciones = DROP
    event.connection.send(fm)
    
    log.info("Bloqueado: ICMP hacia 10.0.0.3")

def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
```

---

### Extensión 3: Contador de paquetes (Telemetría)

**Concepto:** Contar cuántos paquetes pasan por una regla

```python
from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

FLOW_COUNTERS = {}  # Diccionario de contadores

def _handle_StatsReply(event):
    """Procesar respuestas de estadísticas"""
    for flow in event.stats:
        key = (flow.match.dl_src, flow.match.dl_dst)
        FLOW_COUNTERS[key] = flow.packet_count
    
    log.info("Estadísticas: %s", FLOW_COUNTERS)

def _handle_ConnectionUp(event):
    log.info("Switch conectado")
    
    # Crear regla normal
    fm = of.ofp_flow_mod()
    fm.match.dl_src = "00:00:00:00:00:01"
    fm.match.dl_dst = "00:00:00:00:00:02"
    fm.actions.append(of.ofp_action_output(port=2))
    event.connection.send(fm)

def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("FlowStatsReply", _handle_StatsReply)
    
    # Solicitar estadísticas cada 5 segundos
    from pox.lib.recoco import Timer
    Timer(5, lambda: _request_stats(), recurring=True)

def _request_stats():
    for connection in core.openflow._connections.values():
        request = of.ofp_stats_request()
        request.type = of.OFPST_FLOW
        connection.send(request)
```

---

### Extensión 4: Topología de árbol (Tree Topology)

**Crear una topología más compleja para redes mayores:**

```python
from mininet.topo import Topo

class TreeTopology(Topo):
    """
    Topología de árbol (Tree):
    
               s1
              / \
            s2   s3
           /  \ / \
          h1 h2 h3 h4
    """
    
    def build(self):
        # Crear switches
        s1 = self.addSwitch('s1')  # Raíz
        s2 = self.addSwitch('s2')  # Nivel 2
        s3 = self.addSwitch('s3')  # Nivel 2
        
        # Crear hosts
        hosts = []
        for i in range(1, 5):
            h = self.addHost(f'h{i}')
            hosts.append(h)
        
        # Conectar hosts a switches
        self.addLink(hosts[0], s2)  # h1→s2
        self.addLink(hosts[1], s2)  # h2→s2
        self.addLink(hosts[2], s3)  # h3→s3
        self.addLink(hosts[3], s3)  # h4→s3
        
        # Conectar switches (árbol)
        self.addLink(s2, s1)
        self.addLink(s3, s1)

topos = {'tree': TreeTopology}

# Usar:
# sudo mn --custom tree_topo.py --topo=tree --controller=remote
```

---

### Extensión 5: Enrutamiento dinámico basado en carga

**Concepto:** Cambiar rutas según carga de CPU del host

```python
from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

# Rutas alternativas
PRIMARY_ROUTE = 2
BACKUP_ROUTE = 3

def _handle_ConnectionUp(event):
    log.info("Switch conectado - Rutas dinámicas activas")
    
    # Ruta primaria: h1→h2 por puerto 2
    fm1 = of.ofp_flow_mod()
    fm1.match.dl_src = "00:00:00:00:00:01"
    fm1.match.dl_dst = "00:00:00:00:00:02"
    fm1.actions.append(of.ofp_action_output(port=PRIMARY_ROUTE))
    event.connection.send(fm1)

def change_route():
    """Cambiar a ruta backup (simulación)"""
    for connection in core.openflow._connections.values():
        fm = of.ofp_flow_mod()
        fm.command = of.OFPFC_MODIFY  # Modificar regla existente
        fm.match.dl_src = "00:00:00:00:00:01"
        fm.match.dl_dst = "00:00:00:00:00:02"
        fm.actions.append(of.ofp_action_output(port=BACKUP_ROUTE))
        connection.send(fm)
    
    log.info("Ruta cambiada a BACKUP")

def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
```

---

## 🧪 EXPERIMENTOS SUGERIDOS

### Experimento 1: Medir latencia de Packet-In

**Objetivo:** Cuánto tarda en instalar una regla

**Pasos:**
1. Añadir timestamps en blocking.py
2. Registrar cuándo llega ConnectionUp
3. Medir tiempo entre primer ping y segundos
4. Graficar: Primer ping lento, resto rápido

---

### Experimento 2: Comparar consumo de CPU

**Objetivo:** Hub vs Switch en términos de recursos

```bash
# Terminal: Monitorear CPU de POX
watch -n 1 'ps aux | grep pox'

# Terminal Mininet: Generar tráfico
mininet> iperf h1 h2
```

**Resultado esperado:**
- Hub: Mayor CPU (más procesamiento)
- Switch: Menor CPU (reglas instaladas)

---

### Experimento 3: Escalabilidad

**Crear topología con N hosts:**

```python
class ScalableTopology(Topo):
    def build(self, n=10):  # n hosts
        s1 = self.addSwitch('s1')
        for i in range(1, n+1):
            h = self.addHost(f'h{i}')
            self.addLink(h, s1)

topos = {'scale': lambda: ScalableTopology(n=50)}

# sudo mn --custom scale_topo.py --topo=scale
```

Preguntas:
- ¿Cuántas reglas se instalan con 50 hosts?
- ¿Afecta la latencia del controlador?

---

## 📚 RECURSOS AVANZADOS

### Lecturas recomendadas
1. **OpenFlow 1.0 Specification** - OpenNetworking.org
2. **POX Wiki** - https://noxrepo.github.io/pox-doc/
3. **Mininet Documentation** - http://mininet.org/
4. **SDN Controllers Overview** - IEEE papers

### Otros controladores para investigar
- OpenDaylight
- ONOS
- Floodlight
- Ryu

### Protocolo OpenFlow versions
- 1.0 (básico, usado en lab)
- 1.3 (mejorado)
- 1.4+ (avanzado)

---

## 🎯 PROYECTO FINAL SUGERIDO

### Proyecto: "Balanceador de carga simple"

**Requisitos:**
- Topología: 1 cliente (h1), 2 servidores (h2, h3), 1 switch
- Objetivo: Distribuir tráfico entre servidores
- Implementación: Módulo POX que alterna puertos

```python
def _handle_ConnectionUp(event):
    # Alternancia: par de conexiones a h2, impar a h3
    counter = 0
    
    # Regla 1: Conexión impar → h3
    fm1 = of.ofp_flow_mod()
    # Implementar lógica de alternancia
    
    # Regla 2: Conexión par → h2
    fm2 = of.ofp_flow_mod()
    # Implementar lógica de alternancia
```

**Evaluación:**
- ¿Se distribuye equitativamente?
- ¿Qué pasa con conexiones UDP?
- ¿Cómo mantienes estado de sesiones?

---

## ✅ CHECKLIST DE CONCEPTOS AVANZADOS

Después de completar todas las extensiones, deberías poder:

- [ ] Explicar diferencia entre Drop y Deny en OpenFlow
- [ ] Implementar reglas con múltiples criterios (MAC + IP + Puerto)
- [ ] Diseñar topología de árbol completa
- [ ] Escribir módulo POX con manejo de estadísticas
- [ ] Debuggear problemas de conectividad en SDN
- [ ] Proponer soluciones de seguridad para cada capa
- [ ] Comparar rendimiento de diferentes topologías
- [ ] Explicar escalabilidad de controladores centralizados
- [ ] Implementar failover automático
- [ ] Diseñar experimento científico con SDN

---

**¡Completa estos experimentos para dominar SDN!** 🎓
