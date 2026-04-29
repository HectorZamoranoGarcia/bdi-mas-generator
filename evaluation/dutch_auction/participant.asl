// participant.asl
// Agente participante en una Subasta Holandesa.
// Cada participante tiene un presupuesto máximo aleatorio.
// Acepta la oferta cuando el precio está dentro de su presupuesto.

// Objetivo inicial: establecer presupuesto
!init.

// Plan: generar un presupuesto aleatorio entre 20 y 80
+!init <-
    .random(R);
    Budget = 20 + (R * 60);
    +my_budget(Budget);
    .my_name(Me);
    .print(Me, " - Mi presupuesto maximo: ", Budget).

// Plan: recibir una oferta de precio
+price_offer(Price)[source(auctioneer)] : my_budget(Budget) & Price <= Budget <-
    .my_name(Me);
    .print(Me, " - Precio ", Price, " esta dentro de mi presupuesto (", Budget, "). Acepto!");
    .send(auctioneer, tell, accept_offer(Price)).

// Plan: oferta demasiado cara
+price_offer(Price)[source(auctioneer)] : my_budget(Budget) & Price > Budget <-
    .my_name(Me);
    .print(Me, " - Precio ", Price, " es muy alto para mi (presupuesto: ", Budget, "). Paso.").

// Plan: subasta cerrada
+auction_closed(Winner, Price) <-
    .my_name(Me);
    .print(Me, " - Subasta cerrada. Ganador: ", Winner, " a precio ", Price).

// Plan: llegó tarde
+too_late <-
    .my_name(Me);
    .print(Me, " - Mi oferta llego tarde, la subasta ya cerro.").

// Plan de contingencia
+!init <- .print("Error inicializando participante.").
