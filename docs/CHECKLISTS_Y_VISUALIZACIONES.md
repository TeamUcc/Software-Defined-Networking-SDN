# 📋 CHECKLISTS Y GUÍA VISUAL - Laboratorio SDN

---

## 🎯 CHECKLIST NIVEL 1: BÁSICO

### Antes de empezar
- [ ] Ubuntu 20.04 o superior
- [ ] `sudo apt update && sudo apt upgrade` ejecutado
- [ ] Mininet instalado: `which mn`
- [ ] POX clonado: carpeta `pox/` existe
- [ ] Terminal 1 lista para Mininet
- [ ] Terminal 2 lista para POX

### Ejecutar Nivel 1
- [ ] Terminal 1: `sudo mn --topo single,3 --controller=remote --switch ovsk`
  - Esperar prompt `mininet>`
- [ ] Terminal 2: `cd pox && ./pox.py forwarding.l2_learning log.level --DEBUG`
  - Ver log: "Switch s1 has connected"
- [ ] Terminal 1: Ejecutar `mininet> pingall`
  - Resultado esperado: 0% packet loss en todos los pings

### Validaciones Nivel 1
- [ ] Topología visible con `mininet> net`
  - Debe mostrar: s1, h1, h2, h3 con enlaces
- [ ] Ver reglas con `mininet> dpctl dump-flows`
  - Ver múltiples líneas con dl_src= dl_dst=
  - Todas tienen `actions=output:X`

### Preguntas clave Nivel 1
- [ ] Puedo responder: ¿Por qué primero pingall falla sin controlador?
- [ ] Puedo responder: ¿Qué es un Packet-In?
- [ ] Puedo responder: ¿Cómo el switch supo dónde enviar el siguiente paquete?

---

## 🎯 CHECKLIST NIVEL 2: INTERMEDIO

### Preparación
- [ ] Nivel 1 completado exitosamente
- [ ] Entiendo diferencia entre hub y switch
- [ ] Tengo nuevo snippet de código listo

### Cambiar a Hub
- [ ] Terminal 2: Presionar `Ctrl+C` para detener POX
- [ ] Esperar que Mininet muestre: "Connection Down"
- [ ] Terminal 2: `./pox.py forwarding.hub log.level --DEBUG`
  - Ver log: "Switch s1 has connected"

### Pruebas Comparativas
- [ ] Terminal 1: `mininet> pingall` (con hub)
- [ ] Terminal 1: `mininet> dpctl dump-flows`
  - ✓ VER: `actions=output:ALL` o `actions=FLOOD`
  - ✓ DIFERENTE a l2_learning

### Crear tabla comparativa
| Característica | Hub | L2_learning |
|---|---|---|
| Forwarding | ? | ? |
| MACs aprendidas | ? | ? |
| Tráfico | ? | ? |
| Seguridad | ? | ? |

- [ ] Completar tabla basado en observaciones

### Preguntas clave Nivel 2
- [ ] ¿Cuál consume más ancho de banda? ¿Por qué?
- [ ] ¿Dónde está el "aprendizaje" en l2_learning?
- [ ] ¿Qué MAC table tiene cada switch?

---

## 🎯 CHECKLIST NIVEL 3: AVANZADO

### Preparación Pre-Bloqueo
- [ ] Nivel 2 completado
- [ ] Archivo blocking.py existe: `ls /mnt/user-data/outputs/blocking_mejorado.py`
- [ ] Terminal 2: Presionar `Ctrl+C` para detener hub

### Instalar módulo blocking
- [ ] Copiar archivo a POX:
  ```bash
  cp /mnt/user-data/outputs/blocking_mejorado.py pox/pox/forwarding/blocking.py
  ```
- [ ] Verificar: `ls pox/pox/forwarding/blocking.py`

### Ejecutar controlador blocking
- [ ] Terminal 2: `cd pox && ./pox.py forwarding.blocking log.level --DEBUG`
- [ ] Ver en logs:
  - [ ] "Módulo blocking.py cargado"
  - [ ] "Switch s1 conectado"
  - [ ] "Regla instalada: h1->h3 BLOQUEADA"
  - [ ] "Regla instalada: h3->h1 BLOQUEADA"

### Pruebas de bloqueo
- [ ] Terminal 1: `mininet> h1 ping -c 2 h3`
  - ✓ ESPERADO: 100% packet loss
- [ ] Terminal 1: `mininet> h1 ping -c 2 h2`
  - ✓ ESPERADO: 0% packet loss
- [ ] Terminal 1: `mininet> h3 ping -c 2 h2`
  - ✓ ESPERADO: 0% packet loss
- [ ] Terminal 1: `mininet> h2 ping -c 2 h3`
  - ✓ ESPERADO: 0% packet loss

### Inspeccionar reglas
- [ ] Terminal 1: `mininet> dpctl dump-flows`
- [ ] Buscar regla con DROP:
  - [ ] Existe: `dl_src=00:00:00:00:00:01 dl_dst=00:00:00:00:00:03`
  - [ ] Con: `actions=drop`

### Entender el código
- [ ] Puedo explicar qué hace `fm1.match.dl_src`
- [ ] Puedo explicar por qué NO hay `fm1.actions.append(...)`
- [ ] Puedo responder: ¿Cómo pondría una regla al revés?

### Preguntas clave Nivel 3
- [ ] ¿Qué diferencia hay entre una regla vacía y `actions=drop`?
- [ ] ¿Cómo permitirías solo h1↔h2?
- [ ] ¿Qué pasaría si instalas más reglas de bloqueo?

---

## 🔄 DIAGRAMA DE FLUJO DEL LABORATORIO

```
INICIO
  │
  ├─→ NIVEL 1: Topología + L2Learning
  │   ├─ Crear topología (sudo mn ...)
  │   ├─ Lanzar POX (./pox.py l2_learning)
  │   ├─ Probar pingall
  │   └─ Ver reglas (dpctl dump-flows)
  │
  ├─→ NIVEL 2: Comparar Hub vs Switch
  │   ├─ Detener POX (Ctrl+C)
  │   ├─ Lanzar como HUB (./pox.py hub)
  │   ├─ Comparar resultados
  │   └─ Completar tabla comparativa
  │
  ├─→ NIVEL 3: Bloqueo de tráfico
  │   ├─ Crear/copiar blocking.py
  │   ├─ Lanzar POX con blocking
  │   ├─ Verificar h1↔h3 bloqueado
  │   └─ Verificar h1↔h2 y h3↔h2 abierto
  │
  └─→ FIN
     ✓ Laboratorio completado
```

---

## 🌐 ARQUITECTURA VISUAL

### Topología física
```
┌─────────────────────────────────┐
│      h1        h2        h3      │
│      │         │         │       │
│      └─────────┼─────────┘       │
│                │                 │
│               s1                 │
│               (Switch)           │
│     Open vSwitch (OVS)           │
└─────────────────────────────────┘
```

### Plano de Control vs Datos
```
┌─────────────────────────────────────────┐
│         PLANO DE CONTROL                │
│      (Tomador de decisiones)            │
│                                         │
│      ┌──────────────────────┐           │
│      │  Controlador POX     │           │
│      │  - forwarding.l2     │           │
│      │  - forwarding.hub    │           │
│      │  - blocking          │           │
│      └──────────────────────┘           │
│              ↑     ↓                     │
│         (6633)  OpenFlow                │
│              ↑     ↓                     │
├─────────────────────────────────────────┤
│         PLANO DE DATOS                  │
│      (Ejecución de paquetes)            │
│                                         │
│   ┌───────────────────────────────┐    │
│   │ Open vSwitch (s1)             │    │
│   │  Tabla de flujos (Flow Table) │    │
│   │  ├─ Regla 1: h1→h2 OUT:1     │    │
│   │  ├─ Regla 2: h2→h1 OUT:2     │    │
│   │  └─ Regla 3: h1↔h3 DROP      │    │
│   │                               │    │
│   │  Puertos: 1(h1) 2(h2) 3(h3)  │    │
│   └───────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Ciclo de vida de un Packet-In
```
1. h1 envía ping a h3
           │
           ↓
2. Switch recibe paquete
   ¿Hay regla?
           │
           ├─ NO → PACKET_IN
           │
           ↓
3. Controlador recibe PACKET_IN
   ┌─────────────────────────┐
   │ ¿Qué hago?              │
   │ ├─ Aprender MAC         │
   │ ├─ Bloquear tráfico     │
   │ └─ Reenviar             │
   └─────────────────────────┘
           │
           ↓
4. Controlador envía FLOW_MOD
   (regla) al switch
           │
           ↓
5. Switch instala regla
   en su tabla de flujos
           │
           ↓
6. Siguiente paquete
   h1→h3 coincide regla
           │
           ↓
7. ¿Qué dice la regla?
   ├─ output:3 → Reenviar a h3
   ├─ output:ALL → Inundar (hub)
   └─ (vacío) → DROP / Bloquear
```

---

## 📊 TABLA DE REGLAS POR MÓDULO

### forwarding.l2_learning
```
Switch: s1
┌──────────────────────────────────────────────────┐
│ Regla | dl_src          | dl_dst          | Acción   │
├──────────────────────────────────────────────────┤
│ 1    | 00:00:00:00:00:01| 00:00:00:00:00:02| OUT:2   │
│ 2    | 00:00:00:00:00:02| 00:00:00:00:00:01| OUT:1   │
│ 3    | 00:00:00:00:00:01| 00:00:00:00:00:03| OUT:3   │
│ 4    | 00:00:00:00:00:03| 00:00:00:00:00:01| OUT:1   │
│ ...  | ...              | ...              | ...     │
└──────────────────────────────────────────────────┘
```

### forwarding.hub
```
Switch: s1
┌──────────────────────────────────────────────────┐
│ Regla | dl_src | dl_dst | Acción              │
├──────────────────────────────────────────────────┤
│ 1    | *     | *     | OUT:1,2,3 (FLOOD)     │
└──────────────────────────────────────────────────┘
(Una sola regla que inunda todo)
```

### forwarding.blocking
```
Switch: s1
┌──────────────────────────────────────────────────┐
│ Regla | dl_src          | dl_dst          | Acción  │
├──────────────────────────────────────────────────┤
│ 1    | 00:00:00:00:00:01| 00:00:00:00:00:03| DROP    │
│ 2    | 00:00:00:00:00:03| 00:00:00:00:00:01| DROP    │
└──────────────────────────────────────────────────┘
(Las 2 reglas de bloqueo, resto funciona)
```

---

## 🔍 COMANDOS DEBUGGING

### Si pingall falla:
```bash
# Terminal 2: Ver logs detallados
Ctrl+C (detener POX)
./pox.py forwarding.l2_learning log.level --DEBUG log.file=logfile.txt

# Terminal 3: Monitorear logs en vivo
tail -f pox/logfile.txt
```

### Si switch no se conecta:
```bash
# Terminal 1: Limpiar
sudo mn -c

# Terminal 2: Ver puertos
netstat -tlnp | grep 6633

# Terminal 1: Especificar IP
sudo mn --topo single,3 --controller=remote,ip=127.0.0.1,port=6633
```

### Ver MACs reales de hosts:
```bash
mininet> h1 ifconfig eth0 | grep HWaddr
mininet> h2 ifconfig eth0 | grep HWaddr
mininet> h3 ifconfig eth0 | grep HWaddr
```

---

## 📈 MÉTRICAS DE ÉXITO

| Nivel | Métrica | Éxito | Advertencia |
|-------|---------|-------|------------|
| 1 | pingall | 0% loss | > 0% = problema |
| 1 | dpctl flows | n > 0 reglas | 0 reglas = no conectó |
| 2 | Hub flood | ALL puertos | Otros valores = error |
| 2 | L2 port | X específico | ALL = no aprendió |
| 3 | h1↔h3 blocked | 100% loss | < 100% = no bloqueó |
| 3 | h1↔h2 open | 0% loss | > 0% = bloqueó mal |

---

## 🎓 MATRIZ DE COMPETENCIAS

### Después de Nivel 1 deberías poder:
- [ ] Explicar qué es un Packet-In
- [ ] Nombrar 3 módulos POX
- [ ] Usar dpctl para inspeccionar reglas
- [ ] Dibujar topología single,3

### Después de Nivel 2 deberías poder:
- [ ] Comparar flooding vs aprendizaje
- [ ] Calcular diferencia de tráfico hub vs switch
- [ ] Explicar por qué flooding es inseguro
- [ ] Implementar topología propia con topo_simple.py

### Después de Nivel 3 deberías poder:
- [ ] Escribir módulo POX basic
- [ ] Crear reglas de bloqueo selectivas
- [ ] Debuggear por qué una regla no funciona
- [ ] Diseñar política de seguridad simple

---

**✅ Completar todos los checklists = Laboratorio exitoso**
