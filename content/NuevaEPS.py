# ===========================================================================
# Importaciones de clases y librerias necesarias en este archivo main
# ===========================================================================
# Region -  Importaciones de archivos o librerias
from shutil import copytree, copy2
from os import listdir, path, rename

from controller.Log import Log
from controller.Impresor import Impresor
from controller.utils.Configurations import Configurations
# Endregion - Importaciones de archivos o librerias

# ===========================================================================
# VARIABLES GLOBALES - LOCALES - INICIALIZACION DE OBJETOS
# ===========================================================================

# Region - Instancia de clases de archivos importado
logger = Log()
consola = Impresor()
config= Configurations()
# Endregion - Instancia de clases de archivos importado

class NuevaEPS:
    """
        NuevaEPS
        ======= 
        La clase NuevaEPS solo se encargará de gestionar los
        parametros para el renombre y movimiento de los archivos
        que pertenecen a la entidad Nueva EPS.
        ## Usos:
            - `copiadoSop`: Función para copiar soportes de Descarga, a Armado
            - `renombrarArchivos`: Función encargada del renombre según NEPS
    """
    
    # Constructor de la clase
    def __init__(self):
        """
        Metodo constructor de la clase NuevaEPS.

        - `Descripción de variables:`
            - rutaSopXEPSJSON (str): [pathLike] Ruta de ubicación del JSON de NEPS.
            - dataEPSJSON (str): [pathLike || JSON data] Variable vacia inicial, luego tendrá datos de JSON.
        """
        # Variables para almacenar el contenido de los JSON
        self.dataNomenclatura = ""
        self.__nitEntidad = config.getConfigValue("variables", "entidadNIT")
        self.__rutaArmado = config.getConfigValue("variables", "pathCarpetaArmados")

        self.__pacientesSinSoportes = []
    
    def copiadoSop(self, ruta: str, cuenta: str, eps: str):
        """
        Este metodo se encarga de copiar todos los archivos
        encontrados en la carpeta de la ruta dada, y dejarlos
        en la misma carpeta del folder de Soportes
        - `Args:`
            - `ruta:` (str) Ruta de la carpeta de la factura en Soportes Descargados.
            - `cuenta:` (str) Cuenta o factura que se esta iterando y se copiarán sus archivos.
            - `eps:` (str) Abreviatura de la EPS que se esta haciendo el renombre.
        """
        try:
            rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta)
            if(len(listdir(ruta)) > 0):
                copytree(ruta, rutaCarpetaPacienteArmado, dirs_exist_ok = True)
        except Exception as e:
            logger.registrarLogEror(f"Error reportado en el armado de cuentas, y copia de archivos, error: {e}", "copiadoSoportes")

    def copiadoFactura(self, ruta: str, cuenta: str, eps: str):
        """
        Este metodo se encargará de que en cada iteración en
        que sea llamado, busque la factura de la cuenta en
        PDF y la copie a la ruta de armado de cuenta.
        - `Args:`
            - `ruta` (str): Ruta contenedora de las cuentas de facturas
            - `cuenta` (str): Cuenta que se esta iterando
            - `eps` (str): EPS que se esta tratando.
        """
        try:
            rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta)
            rutaCarpetaPacienteFactura = path.join(ruta, cuenta)
            rutaFacturaPaciente = path.join(rutaCarpetaPacienteFactura, f"{cuenta}.pdf")
            if(path.isfile(rutaFacturaPaciente)):
                copy2(rutaFacturaPaciente, rutaCarpetaPacienteArmado)

        except Exception as e:
            print(e)
            logger.registrarLogEror(f"Error reportado en el armado de cuentas, y copia de archivos, error: {e}", "copiadoSoportes")
        
    def renombrarArchivos(self, eps: str, cuenta: str):
        """
        Este metodo recorrerá todas las carpetas de radicado,
        identificando los soportes y renombrando según el orden
        que se trae en su nomenclatura.
        - `Argumentos:`
            - `eps:` (str) Abreviatura de la EPS que se esta procesando.
            - `cuenta:` (str) Cuenta o factura que se esta iterando y se hará renombre de archivos.
        """
        rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta)
        if(len(listdir(rutaCarpetaPacienteArmado)) > 0):
            for soporte in listdir(rutaCarpetaPacienteArmado):
                try:
                    strNomenSoporte = self.dataNomenclatura["renombreSoporte"]
                    soporteRecorrido = path.splitext(soporte)
                    strRenombreSoporte = strNomenSoporte.replace("$soporte", soporteRecorrido[0]).replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    rename(path.join(rutaCarpetaPacienteArmado, soporte), path.join(rutaCarpetaPacienteArmado, strRenombreSoporte))
                except Exception as e:
                    print(e)
                    logger.registrarLogEror(f"Error en el renombre del soporte: {soporte} de la cuenta: {cuenta}, error: {e}", "renombrarArchivos")
        else:
            self.__pacientesSinSoportes.append(cuenta)
