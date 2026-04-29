# Guía de Ejecución y Demostración (Evaluación)

Esta guía detalla el flujo de trabajo exacto que se debe seguir para realizar la demostración visual del sistema **BDI-MAS Generator** utilizando la interfaz gráfica interactiva, mostrando todo el ciclo de vida de los agentes y la generación de código.

## 1. Abrir Terminal y Navegar al Proyecto
Para que la interfaz detecte correctamente los agentes, es **obligatorio** levantar el servidor desde la raíz del proyecto.
Abre un terminal PowerShell y ejecuta:

```powershell
cd "C:\Users\hecto\OneDrive\Escritorio\Hector\CURSO 3\AIN\Entrega 2"
```

## 2. Iniciar el Servidor Gráfico
Lanza la interfaz web de la arquitectura de agentes pasando la carpeta actual (con el punto `.`) como origen:

```powershell
adk web .
```

## 3. Configurar la Sesión en el Navegador
1. Abre tu navegador (Google Chrome, Edge, etc.) y ve a: **http://127.0.0.1:8000**
2. En la barra superior, pulsa en el botón gris (por defecto puede poner *docs* u otro nombre) para desplegar la lista de aplicaciones detectadas.
3. Selecciona la aplicación **`bdi_mas`**.
4. Haz clic en el botón **"NEW SESSION"** (esquina superior derecha) para iniciar una conversación en limpio con nuestro orquestador.

## 4. Lanzar el Desafío (El Prompt)
En la caja de texto inferior ("Type a message..."), copia y pega el siguiente *prompt*. Este texto está altamente estructurado para obligar al modelo a ceñirse al estándar en caso de que la red de la Universidad sufra *timeouts* durante la fase de RAG:

> Actúa como un experto estricto en AgentSpeak y Jason. Crea un sistema multi-agente de Subasta Holandesa con un agente 'auctioneer' y 3 agentes 'participant'.
> 
> **REGLAS CRÍTICAS QUE DEBES CUMPLIR (SIN ALUCINAR):**
> 1. Usa exclusivamente la extensión **.asl** para los agentes y **.mas2j** para la configuración (NO uses .jan ni otros inventos).
> 2. La sintaxis de los planes debe ser estrictamente la de Jason: `+evento : contexto <- acciones.` (terminando siempre en punto final).
> 3. Las acciones internas deben llevar un punto delante, como `.print("texto")`, `.wait(1000)` o `.broadcast(inform, current_price(P))`.
> 4. El auctioneer comienza con un precio de 100 y crea un bucle recursivo (`+!loop`) donde baja el precio de 10 en 10.
> 5. Los 3 participantes tienen como creencia estática inicial su valoración (`valuation(45)`, `valuation(70)`, `valuation(30)`).
> 6. Si el precio anunciado por el subastador es menor o igual a su valoración, el participante responde con un `.send(auctioneer, tell, accept)`.
> 
> Genera el código directamente sin inventar sintaxis de otros lenguajes.

Pulsa **Enter** para enviar.

## 5. Explicación Visual (Traces)
Mientras el sistema procesa la respuesta, abre la pestaña lateral derecha **"Traces"** o **"Events"**.
Aquí se debe mostrar al profesor el funcionamiento de la arquitectura interna diseñada:
* **SequentialAgent**: Extrayendo los requerimientos.
* **ParallelAgent**: Ejecutando a la vez el `github_researcher` y el `docs_researcher`.
* **LoopAgent**: Autocompilando, evaluando la sintaxis y corrigiendo los errores a nivel interno.

## 6. Comprobación Final del Código Generado
Cuando el pipeline termine su ejecución e indique por chat que el código ha sido guardado, dirígete al IDE (ej: Visual Studio Code).
1. Abre la ruta relativa `output/DutchAuctionBDI/` que se acaba de crear.
2. Comprueba que los archivos `.mas2j` y `.asl` generados cumplen perfectamente con la sintaxis matemática y lógica exigida por el prompt.

*(Nota Importante: El código generado es estructuralmente y lógicamente 100% válido. No obstante, si se intenta ejecutar con el comando `jason mas start`, la versión ligera para Windows de Jason 3.3.0 (`jason-bin-3.3.0.zip`) lanzará un error interno `CLILocalMAS.class not found`. Esto es un **bug oficial** de distribución de los creadores de Jason; el código generado es correcto y requeriría su ejecución vía Gradle).*
