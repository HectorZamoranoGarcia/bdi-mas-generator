// fibonacci_agent.asl
// Agente que calcula e imprime la serie de Fibonacci hasta un valor límite.

// Creencia inicial: límite de la serie
limit(21).

// Objetivo inicial
!start.

// Plan principal: iniciar la serie de Fibonacci
+!start : limit(Max) <-
    .print("=== Serie de Fibonacci hasta ", Max, " ===");
    !fibonacci(0, 1, Max).

// Plan recursivo: imprimir mientras el valor actual no supere el límite
+!fibonacci(A, B, Max) : A <= Max <-
    .print(A);
    Next = A + B;
    !fibonacci(B, Next, Max).

// Plan de parada: cuando A supera el límite
+!fibonacci(A, B, Max) : A > Max <-
    .print("=== Fin de la serie ===").

// Plan de contingencia
+!start <- .print("Error: no se encontró el límite.").
