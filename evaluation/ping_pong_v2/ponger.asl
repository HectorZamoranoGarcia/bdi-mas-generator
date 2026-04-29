// ponger.asl
// Agente que responde con "Pong" cuando recibe un "Ping" (versión iterativa).

// Plan: al recibir un Ping con número de iteración, responder con Pong
+ping(Iter)[source(Sender)] <-
    .print("[Iteracion ", Iter, "] Recibido: Ping de ", Sender);
    .print("[Iteracion ", Iter, "] Enviando Pong a ", Sender, "...");
    .send(Sender, tell, pong(Iter)).
