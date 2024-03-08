# ===========================================================================
# Importaciones de clases y librerias necesarias en este archivo main
# ===========================================================================

# Region -  Importaciones de archivos o librerias
from controller.Log import Log
from content.Armado import Armado
from controller.Impresor import Impresor
# Endregion - Importaciones de archivos o librerias

# ===========================================================================
# VARIABLES GLOBALES - LOCALES - INICIALIZACION DE OBJETOS
# ===========================================================================

# Region - Instancia de clases de archivos importado
logger = Log()
armado = Armado()
consola = Impresor()
# Endregion - Instancia de clases de archivos importado

# Region - Body Metodo Principal
def main():
    try: 
        consola.imprimirInicio("Armado de cuenta - Zentria")
        logger.registroInicioProcesos()
        
        logger.registrarLogProceso("Inicio de ejecución del proceso")
        # bd.registrarInicioBaseDatos("Arquitectura", "Bots")
        
        # Region - Cuerpo de la automatización
        armado.orquestarArmado()
        # Endregion - Cuerpo de la automatización
        
        consola.imprimirFinal()
        logger.registroFinalProcesos()
    except Exception as e:
        logger.registrarLogEror(f"Excepción localizada en el main, error: {e}", "main")
        consola.imprimirError(f"Ocurrió un error en la ejecución: {e}")
# Endregion

# Metodo para ejecución del Script, invocando la función main()    
if __name__ == '__main__':
    main()