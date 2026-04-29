// auctioneer.asl
// Agente subastador que implementa una Subasta Holandesa.
// Comienza con un precio alto y lo baja progresivamente hasta que
// un participante acepta o se alcanza el precio mínimo.

// Creencias iniciales
item("Cuadro antiguo").
start_price(100).
min_price(10).
decrement(10).
current_price(100).
auction_active(true).

// Objetivo inicial
!start.

// Plan: iniciar la subasta
+!start : item(Item) & start_price(P) <-
    .print("=== SUBASTA HOLANDESA ===");
    .print("Articulo: ", Item);
    .print("Precio inicial: ", P);
    .wait(1000);
    !announce_price.

// Plan: anunciar el precio actual a todos los participantes
+!announce_price : current_price(P) & min_price(Min) & P >= Min & auction_active(true) <-
    .print("--- Precio actual: ", P, " ---");
    .broadcast(tell, price_offer(P));
    .wait(2000);
    !check_bids.

// Plan: nadie ha aceptado, bajar el precio
+!check_bids : auction_active(true) & current_price(P) & decrement(D) & min_price(Min) <-
    NewP = P - D;
    .print("Nadie acepta a ", P, ". Bajando precio...");
    -+current_price(NewP);
    !announce_price.

// Plan: precio por debajo del mínimo, subasta desierta
+!announce_price : current_price(P) & min_price(Min) & P < Min & auction_active(true) <-
    .print("=== SUBASTA DESIERTA: precio minimo alcanzado ===");
    -+auction_active(false).

// Plan: un participante acepta la oferta
+accept_offer(P)[source(Buyer)] : auction_active(true) <-
    .print("*** VENDIDO a ", Buyer, " por ", P, " ***");
    -+auction_active(false);
    .broadcast(tell, auction_closed(Buyer, P)).

// Plan: oferta recibida pero subasta ya cerrada
+accept_offer(P)[source(Buyer)] : auction_active(false) <-
    .send(Buyer, tell, too_late).

// Planes de contingencia
+!start <- .print("Error iniciando subasta.").
+!announce_price <- .print("Error anunciando precio.").
+!check_bids <- .print("Error verificando ofertas.").
