# 🚀 GUÍA RÁPIDA: Laboratorio SDN Mininet + POX
**Tiempo total: ~60 minutos | Basado en niveles de dificultad**

---

## 📋 SETUP INICIAL (5 minutos)

### 1. Verificar Mininet
```bash
which mn
mn --version
```

### 2. Descargar POX (si no lo tienes)
```bash
git clone https://github.com/noxrepo/pox.git
cd pox
chmod +x pox.py
```

### 3. Preparar 3 terminales
- **Terminal 1**: Mininet
- **Terminal 2**: POX (Controlador)
- **Terminal 3**: Utilidades (opcional)

---

## 🟢 NIVEL 1: BÁSICO (15 minutos)

### Terminal 1 - Crear Topología
```bash
sudo mn --topo single,3 --controller=remote,ip=127.0.0.1,port=6633 --switch ovsk
```

**Resultado esperado:**
```
*** Starting Mininet ***
mininet> 
```

### Terminal 2 - Lanzar Controlador POX
```bash
cd pox
./pox.py forwarding.l2_learning log.level --DEBUG
```

**En los logs verás:**
```
[l2_learning] Switch s1 has connected
```

### Prueba 1: Sin conectividad (Línea de base)
```bash
mininet> h1 ping -c 2 h2
# FALLA (sin reglas)
```

### Prueba 2: Con aprendizaje
```bash
mininet> pingall
# ✅ ÉXITO - El controlador aprendió las rutas
```

### Inspeccionar reglas instaladas
```bash
mininet> dpctl dump-flows
# Verás: dl_src=XX:XX... dl_dst=YY:YY... actions=output:X
```

**✅ Checkpoint Nivel 1:** Entienden cómo el controlador aprende MAC y programa reglas.

---

## 🟡 NIVEL 2: INTERMEDIO (20 minutos)

### Cambiar a Hub (Forwarding no inteligente)

**Terminal 2 - Detener POX:**
```bash
Ctrl+C
```

**Reiniciar como HUB:**
```bash
./pox.py forwarding.hub log.level --DEBUG
```

### Comparar comportamientos

**En Mininet:**
```bash
mininet> pingall
mininet> dpctl dump-flows
```

**Diferencias observadas:**

| Aspecto | Hub | Switch L2 |
|--------|-----|-----------|
| **Reglas** | `actions=output:ALL` | `actions=output:X` |
| **Tráfico** | Inunda todo | Solo destino |
| **Ancho de banda** | Bajo (ineficiente) | Alto (eficiente) |

**Visualizar tráfico (opcional):**
```bash
mininet> h1 ping -c 1 h3
# En Terminal 2 (POX logs), verás packet-in de BROADCAST
```

**✅ Checkpoint Nivel 2:** Comprendieron diferencia entre forwarding ciego vs inteligente.

---

## 🔴 NIVEL 3: AVANZADO (25 minutos)

### Crear política de bloqueo

**1. Crear blocking.py en POX:**
```bash
cat > pox/pox/forwarding/blocking.py << 'EOF'
from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

H1_MAC = "00:00:00:00:00:01"
H3_MAC = "00:00:00:00:00:03"

def _handle_ConnectionUp(event):
    log.info("Switch %s conectado", event.dpid)
    
    # Bloquear h1 -> h3
    fm1 = of.ofp_flow_mod()
    fm1.match.dl_src = H1_MAC
    fm1.match.dl_dst = H3_MAC
    event.connection.send(fm1)
    
    # Bloquear h3 -> h1
    fm2 = of.ofp_flow_mod()
    fm2.match.dl_src = H3_MAC
    fm2.match.dl_dst = H1_MAC
    event.connection.send(fm2)

def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    log.info("Módulo blocking.py cargado")
EOF
```

**2. En Terminal 2 - Detener y reiniciar:**
```bash
Ctrl+C
./pox.py forwarding.blocking log.level --DEBUG
```

**Deberías ver en logs:**
```
[blocking] Módulo blocking.py cargado
[blocking] Switch s1 conectado
```

**3. Probar bloqueo en Mininet:**
```bash
mininet> h1 ping -c 2 h3
# ❌ FALLA - 100% packet loss (bloqueado)

mininet> h1 ping -c 2 h2
# ✅ FUNCIONA - h2 no está bloqueada

mininet> h3 ping -c 2 h2
# ✅ FUNCIONA - h3 solo está bloqueada con h1
```

**Verificar que reglas drop existen:**
```bash
mininet> dpctl dump-flows
# Verás: dl_src=00:00:00:00:00:01 dl_dst=00:00:00:00:00:03 actions=drop
```

**✅ Checkpoint Nivel 3:** Implementaron política de seguridad selectiva sin tocarse

---

## 📊 CHECKLISTS DE VALIDACIÓN

### ✅ Validar Nivel 1
- [ ] Topología se crea sin errores
- [ ] POX se conecta correctamente
- [ ] `pingall` muestra 0% packet loss
- [ ] `dpctl dump-flows` muestra reglas MAC

### ✅ Validar Nivel 2
- [ ] Hub genera reglas con `output:ALL`
- [ ] Switch L2 genera reglas con `output:X` específico
- [ ] Entienden diferencia de eficiencia
- [ ] Pueden explicar flooding vs aprendizaje

### ✅ Validar Nivel 3
- [ ] blocking.py se carga sin errores
- [ ] h1↔h3 está bloqueado (100% loss)
- [ ] h1→h2 funciona (0% loss)
- [ ] h3→h2 funciona (0% loss)
- [ ] `dpctl dump-flows` muestra DROP actions

---

## 🐛 TROUBLESHOOTING RÁPIDO

| Problema | Comando Fix |
|----------|------------|
| "Connection refused" | `sudo mn -c` |
| POX "No module named pox" | `cd pox` antes de ejecutar |
| Ping no funciona | Verifica que POX está corriendo |
| Reglas no se instalan | Reinicia con `Ctrl+C` y ejecuta de nuevo |
| h1 MAC no es 00:00:00:00:00:01 | Usa `dpctl dump-flows` para ver MAC real |

**Limpiar todo antes de reintentar:**
```bash
sudo mn -c
killall pox.py 2>/dev/null || true
```

---

## 🎯 COMANDOS CLAVE MININET

```bash
# Ver topología
mininet> net

# Ping entre hosts
mininet> h1 ping -c 2 h2

# Ping todos vs todos
mininet> pingall

# Ver reglas de flujo
mininet> dpctl dump-flows

# Terminal en un host
mininet> xterm h1

# Ver interfaz de red
mininet> h1 ip addr show

# Generar tráfico
mininet> iperf

# Salir
mininet> exit
```

---

## 📚 CONCEPTOS INTERNALIZADOS

### Plano de Datos vs Control
- **Datos**: Switches reenvían según reglas
- **Control**: POX decide qué reglas instalar
- **Separación**: Permite programación centralizada

### Flujo Packet-In
```
Host envía paquete
    ↓
Switch no tiene regla
    ↓
Envía PACKET_IN a POX
    ↓
POX decide (aprender, bloquear, reescribir)
    ↓
POX instala regla (FLOW_MOD)
    ↓
Switch reenvía según regla
```

### Regla de Flujo (Flow)
```
Match: dl_src=MAC_ORIGEN, dl_dst=MAC_DESTINO
Action: output:PUERTO (reenviar) | drop (descartar)
Priority: Orden de evaluación (mayor primero)
```

---

## 🚀 EXTENSIONES (Si quedan minutos)

### 1. Topología por Script
```bash
cat > topo_custom.py << 'EOF'
from mininet.topo import Topo

class MyTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        for i in range(1, 4):
            h = self.addHost(f'h{i}')
            self.addLink(h, s1)

topos = {'mytopo': MyTopo}
EOF

sudo mn --custom topo_custom.py --topo=mytopo --controller=remote
```

### 2. Ver MACs reales de los hosts
```bash
mininet> h1 ifconfig eth0 | grep HWaddr
```

### 3. Implementar whitelist en lugar de blacklist
```python
# En lugar de DROP, hacer ACTION explícitamente
fm = of.ofp_flow_mod()
fm.match.dl_src = H1_MAC
fm.match.dl_dst = H2_MAC
# Action: forward a puerto 1 (en lugar de drop)
```

---

## ✍️ NOTAS FINALES

1. **POX usa Python 2.7** - Algunos sistemas lo tienen como `python2`
2. **MACs se asignan secuencialmente** - h1=01, h2=02, h3=03
3. **Reglas persisten** - Para limpiar: `sudo mn -c`
4. **Debug es tu amigo** - Siempre usa `log.level --DEBUG`

---

**Tiempo estimado por nivel:**
- Básico: 15 min ✅
- Intermedio: 20 min ✅
- Avanzado: 25 min ✅
- **TOTAL: ~60 minutos** ⏱️

¡Listo para ejecutar! 🎯
