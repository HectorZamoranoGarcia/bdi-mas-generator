// pinger.asl
// Agente que envía un mensaje "Ping" al agente ponger.

// Objetivo inicial
!start.

// Plan: enviar Ping al ponger
+!start <-
    .print("Enviando Ping a ponger...");
    .send(ponger, tell, ping).

// Plan: recibir respuesta Pong del ponger
+pong[source(ponger)] <-
    .print("Recibido: Pong de ponger").
