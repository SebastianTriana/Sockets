# Chat Bidireccional con Python, Sockets y Tkinter

Este repositorio contiene un **chat bidireccional local** usando:
- Python   
- Sockets TCP   
- Threads 
- Tkinter   

Permite que varios clientes en la misma máquina se conecten a un servidor y chateen en tiempo real.

---

## Estructura del Proyecto

```
chat_project/
├── server.py      # Servidor TCP multihilo
└── client.py      # Cliente con interfaz Tkinter
```

---

## Cómo usarlo

### 1. Ejecutar el servidor:
```
python server.py
```

### 2. Ejecutar uno o varios clientes:
```
python client.py
```

Cada cliente abre una ventana independiente y todos reciben los mensajes enviados por los demás.

---

## Requisitos

- Python 3.10+
- Tkinter (ya incluido en Windows)

---

## Funcionamiento Interno

### Servidor
- Acepta múltiples conexiones.
- Usa un hilo por cliente.
- Hace *broadcast* de cada mensaje a todos los conectados.

### Cliente
- Usa Tkinter para la interfaz.
- Un hilo escucha mensajes sin bloquear la ventana.
- Permite enviar mensajes instantáneamente.

