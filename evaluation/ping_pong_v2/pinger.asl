// pinger.asl
// Agente que envía "Ping" al ponger y repite durante N iteraciones.

// Creencias iniciales
max_iter(5).
current_iter(0).

// Objetivo inicial
!start.

// Plan: iniciar el primer Ping
+!start <-
    .print("=== Ping-Pong con 5 iteraciones ===");
    !do_ping.

// Plan: enviar Ping si no se ha alcanzado el máximo
+!do_ping : current_iter(I) & max_iter(Max) & I < Max <-
    NewI = I + 1;
    -+current_iter(NewI);
    .print("[Iteracion ", NewI, "] Enviando Ping a ponger...");
    .send(ponger, tell, ping(NewI)).

// Plan: parar cuando se alcanza el máximo
+!do_ping : current_iter(I) & max_iter(Max) & I >= Max <-
    .print("=== Fin: alcanzadas ", Max, " iteraciones ===").

// Plan: recibir Pong y continuar
+pong(Iter)[source(ponger)] <-
    .print("[Iteracion ", Iter, "] Recibido: Pong de ponger");
    .wait(200);
    !do_ping.

// Plan de contingencia
+!do_ping <- .print("Error en do_ping").
