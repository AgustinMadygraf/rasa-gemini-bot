Collecting workspace information# Informe: Integración de Google Gemini como Fallback para Rasa

## Análisis de la problemática

### Situación actual
Actualmente, el bot implementado con Rasa 3.6.21 está diseñado para funcionar en uno de tres modos mutuamente excluyentes:

1. **Modo RASA**: Utiliza exclusivamente el motor de Rasa con intenciones, historias y reglas predefinidas
2. **Modo GOOGLE_GEMINI**: Delega todas las respuestas al modelo Gemini
3. **Modo ESPEJO**: Simplemente repite lo que el usuario dice (para pruebas)

El problema se manifiesta en situaciones como la mostrada en el diálogo de ejemplo, donde el usuario responde "Listo, ya lo instalé" después de recibir instrucciones para instalar Git. En este caso, Rasa no reconoce esta respuesta y contesta con "No tengo una respuesta en este momento", interrumpiendo el flujo conversacional.

### Comportamiento deseado
Se requiere un **modo híbrido** donde:

- Rasa siga siendo el motor principal para los flujos de conversación definidos
- Cuando Rasa no pueda determinar una respuesta adecuada (por limitaciones en el NLU, falta de historias/reglas, o baja confianza), automáticamente se active Gemini
- Gemini debe generar respuestas considerando el contexto completo de la conversación hasta ese momento
- La transición entre Rasa y Gemini debe ser transparente para el usuario final

## Diagnóstico técnico

### Causas del problema

1. **Limitaciones en la extracción de slots**: 
   - El método `extract_git_instalado()` en `ValidateInstalarRasaForm` tiene reglas muy restrictivas para reconocer confirmaciones
   - No reconoce variantes como "Listo, ya lo instalé", "Terminé de instalarlo", etc.

2. **Ausencia de mecanismo de fallback avanzado**: 
   - El `FallbackClassifier` actual solo activa respuestas genéricas como "No entendí tu mensaje"
   - No existe un puente entre el sistema de fallback de Rasa y el motor de Gemini

3. **Arquitectura de modos exclusivos**:
   - La selección de modo en run.py implementa una lógica excluyente (o Rasa o Gemini)
   - No hay un mecanismo establecido para la comunicación entre los motores

### Puntos de integración disponibles

1. **`FallbackClassifier` en la pipeline de Rasa**:
   - Ya está configurado en config.yml con threshold de 0.3
   - Se podría aprovechar para desencadenar la activación de Gemini

2. **Acciones personalizadas de Rasa**:
   - actions.py permite implementar lógica personalizada para manejar fallbacks
   - Se podría crear una nueva acción específica para delegación a Gemini

3. **Tracker de Rasa**:
   - Contiene todo el historial de la conversación
   - Se puede extraer para construir el contexto para Gemini

4. **Infraestructura de Gemini**:
   - `GeminiService` y `GeminiGateway` ya están implementados
   - Pueden ser reutilizados desde las acciones de Rasa

## Desafíos técnicos

1. **Historial de conversación**:
   - Convertir el formato de eventos de Rasa a un formato apropiado para Gemini
   - Decidir cuánta historia enviar (últimos N turnos vs. conversación completa)

2. **Mantenimiento del estado**:
   - Asegurar que los slots y variables de estado se mantengan coherentes cuando Gemini responda
   - Evitar que Gemini genere respuestas que contradigan el modelo de dominio

3. **Control de flujo**:
   - Determinar cuándo Gemini debe ceder el control de vuelta a Rasa
   - Manejar situaciones donde el usuario vuelve a un flujo definido después de haber pasado por Gemini

4. **Rendimiento y latencia**:
   - La llamada a la API de Gemini añade latencia adicional
   - Considerar timeout adecuados para evitar bloqueos

5. **Coherencia semántica**:
   - Garantizar que las respuestas de Gemini sean coherentes con el "personaje" del bot
   - Evitar respuestas inapropiadas o fuera de contexto

## Enfoques de solución

### Enfoque 1: Acción de fallback personalizada

- Crear una nueva acción de fallback (`ActionGeminiFallback`) que se active cuando Rasa no tenga suficiente confianza
- Configurar en domain.yml para reemplazar la acción `action_default_fallback` estándar
- Modificar config.yml para ajustar el comportamiento del `FallbackClassifier`
- Ventaja: Mayor control, integración nativa con el sistema de fallback de Rasa
- Desventaja: Limitado a escenarios de baja confianza, podría no cubrir todos los casos deseados

### Enfoque 2: Modo híbrido como nuevo modo de ejecución

- Implementar un nuevo modo "RASA_GEMINI" en run.py y configuración
- Modificar el servidor de acciones para detectar cuándo no hay respuesta definida
- Crear un middleware que intercepte respuestas vacías o de bajo valor
- Ventaja: Solución más completa, cubre más escenarios
- Desventaja: Mayor complejidad de implementación, posibles cambios en la arquitectura existente

### Enfoque 3: Extensión de `FormValidationAction`

- Mejorar las funciones de extracción y validación en `ValidateInstalarRasaForm`
- Añadir procesamiento de lenguaje natural más avanzado para detectar confirmaciones
- Incluir llamadas a Gemini para casos ambiguos dentro del propio formulario
- Ventaja: Solución específica para el problema del formulario, menor impacto en la arquitectura
- Desventaja: No resuelve el problema general, solo el caso particular del formulario

## Consideraciones adicionales

1. **Persistencia del modo híbrido**:
   - ¿Debe ser configurable el umbral de confianza para activar Gemini?
   - ¿Debe ser posible desactivar esta característica para ciertos flujos?

2. **Instrucciones de sistema para Gemini**:
   - Las instrucciones actuales en system_instructions.json podrían necesitar actualización
   - Adaptar para que Gemini comprenda que está actuando como fallback de Rasa

3. **Logging y monitoreo**:
   - Implementar registro detallado de cuándo y por qué se activa Gemini
   - Permitir análisis posterior para mejorar el modelo de Rasa

4. **Costos de API**:
   - Considerar el aumento potencial en llamadas a la API de Gemini
   - Implementar mecanismos para controlar frecuencia y volumen de uso

## Recomendación preliminar

El **Enfoque 1 (Acción de fallback personalizada)** parece ofrecer el mejor equilibrio entre esfuerzo de implementación y resultado esperado. Esta solución:

1. Requiere cambios mínimos en la arquitectura existente
2. Aprovecha mecanismos nativos de Rasa (sistema de fallback)
3. Permite una integración natural con el flujo de conversación
4. Puede implementarse de manera incremental, empezando con casos específicos

Para una solución más robusta a largo plazo, podría considerarse posteriormente el Enfoque 2, pero comenzar con el Enfoque 1 permitiría obtener resultados rápidamente mientras se evalúa la efectividad de la integración Rasa-Gemini.

## Próximos pasos recomendados

1. Evaluar si el enfoque recomendado cumple con los requisitos específicos del proyecto
2. Definir métricas de éxito para la implementación (reducción de respuestas genéricas, satisfacción de usuarios, etc.)
3. Decidir el alcance inicial de la implementación (solo formularios o fallback general)
4. Determinar el formato y cantidad de contexto conversacional a enviar a Gemini

Una vez validados estos puntos, se puede proceder con la implementación técnica detallada.