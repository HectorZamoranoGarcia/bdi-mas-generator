// ponger.asl
// Agente que responde con "Pong" cuando recibe un "Ping".

// Plan: al recibir un Ping, imprimir y responder con Pong
+ping[source(Sender)] <-
    .print("Recibido: Ping de ", Sender);
    .print("Enviando Pong a ", Sender, "...");
    .send(Sender, tell, pong).
