# ===========================================================================
# Importaciones de clases y librerias necesarias en este archivo main
# ===========================================================================
# Region -  Importaciones de archivos o librerias
from json import load
from json import dumps
from os import  path, getcwd
from datetime import datetime

from controller.Log import Log
from content.NuevaEPS import NuevaEPS
from controller.Impresor import Impresor
from content.Peticiones import Peticiones
from controller.utils.Configurations import Configurations
# Endregion - Importaciones de archivos o librerias

# ===========================================================================
# VARIABLES GLOBALES - LOCALES - INICIALIZACION DE OBJETOS
# ===========================================================================

# Region - Instancia de clases de archivos importado
logger = Log()
neps = NuevaEPS()
peti = Peticiones()
consola = Impresor()
config= Configurations()

directorioProyecto = getcwd()
# Endregion - Instancia de clases de archivos importado

class Armado:
    """
        Armado
        ======= 
        Esta clase se encargará de gestionar las carpetas, y archivos
        pertenecientes al renombrado de la entidad dada. Para ello
        se hará uso de metodos generales, que se utilizarán como
        apoyo a los metodos especificos de cada EPS.
        ## Usos
            - `lecturaJSON`: Leer los JSON que se le setean desde los attr de clase.
            - `existeCarpeta`: Busca la existencia de una carpeta en especifico.
            - `orquestarArmado`: Orquestado de las funciones con orden de proceso.
    """

    def __init__(self):
        """
        Metodo constructor de la clase Armado, aquí
        se inicializarán las variables correspondientes
        al armado de la EPS dada, según los parametros.

        - `Descripción de variables:`
            - self.rutaSoportesJSON (str): JSON de relación de soportes requeridos.
            - self.rutaNomenclaJSON (str): JSON de nomenclatura de renombre de soportes.
            - self.rutaSopsDescargados (str): Ruta de la carpeta donde se descargan los soportes x factura.
            - self.rutaSopsDescargados (str): Ruta de la carpeta donde se están las facturas en PDF.
            - self.dataSoportesJSON (JSON): Data obtenido del JSON de soportes requeridos.
            - self.dataNomenclaJSON (JSON): Data obtenido del JSON para renombre de sopores.
            - self.__cuentasArmar (List): Listado de aquellas facturas que no tienen carpeta de soportes descargados.
        """
        # Rutas de JSON o paths para hacer lecturas
        self.rutaSoportesJSON = config.getConfigValue("routes", "UbicacionJSONsoportes")
        self.rutaNomenclaJSON = config.getConfigValue("routes", "UbicacionJSONnomenclatura")
        self.rutaAntiguaPeticionJSON = config.getConfigValue("routes", "UbicacionJSONDatosAnteriores")
        self.rutaSopsDescargados = config.getConfigValue("variables", "pathSoportesDescargados")
        self.rutaFacturasDescarg = config.getConfigValue("variables", "pathCarpetaFacturas")

        self.__entornoDesarrollo = config.getConfigValue("enviroment", "entornoProceso")
        # if(self.__entornoDesarrollo != "dev"):
        #     self.__fechaEjecucion = datetime.today().strftime('%d-%m-%Y')
        #     self.rutaFacturasDescarg = path.join(self.rutaFacturasDescarg, f"facturas-{self.__fechaEjecucion}")

        # Variables para almacenar el contenido de los JSON
        self.dataSoportesJSON = ""
        self.dataNomenclaJSON = ""

        # Lista de cuentas que pueden ser armadas.
        self.__cuentasArmar = []

    def lecturaJSON(self):
        """
        Este metodo se encarga de la lectura de los JSON
        complementarios para obtener la información de
        relación entre los soportes y entidades.
        """
        procede = False
        try:
            with open(self.rutaSoportesJSON,'r') as arch:
                self.dataSoportesJSON = load(arch)
                arch.close()

            with open(self.rutaNomenclaJSON,'r') as arch:
                self.dataNomenclaJSON = load(arch)
                arch.close()

            logger.registrarComentario("INFO", f"Los JSON se han leido con éxito, se tienen ({len(self.dataSoportesJSON)}) datos de soportes, y ({len(self.dataNomenclaJSON)}) datos de nomenclaturas.")
            procede = True
        except Exception as e:
            logger.registrarLogEror(f"Error leyendo los JSON de nomenclatura o soportes, error: {e}", "lecturaJSON")
        finally:
            return procede
        
    def existeCarpeta(self, carpeta: str) -> bool:
        """
        Este metodo se encargará de validar si existe la
        carpeta recibida por argumento o no existe aún.
        - `Argumentos:`
            - `carpeta`: (str) Referencia de la factura a buscar.
        - `Return:`
            - `existe`: (bool) Boolean para existencia o no de carpeta
        """
        existe = False
        try:
            rutaSoportesFactura = path.join(self.rutaSopsDescargados, carpeta)
            carpetaEnDescargaSoportes = path.exists(rutaSoportesFactura)
            if(carpetaEnDescargaSoportes):
                existe = True
        except Exception as e:
            logger.registrarLogEror(f"La carpeta de la factura [{carpeta}], no existe en la carpeta de soportes descargados.", "existeCarpeta")
        finally:
            return existe

    def escribirDatosAnterioresJSON(self, datos):
        """
        Para llevar un control de los datos, se escribirá en un
        JSON los datos anteriores de la respuesta de la API
        sobre las cuentas que se deben procesar. 
        """
        try:
            if(path.isfile(path.join(directorioProyecto, self.rutaAntiguaPeticionJSON))):
                datosSeteados = dumps(datos, indent = 4)
                consola.imprimirComentario("escribirDatosAnterioresJSON", f"Escribiendo datos anteriores en JSON de antigua petición, con {len(datos)} datos existentes.")
                with open(path.join(directorioProyecto, self.rutaAntiguaPeticionJSON), "w") as archivoJSON:
                    archivoJSON.write(datosSeteados)
                    archivoJSON.close()
        except Exception as e:
            consola.imprimirError(f"Error al escribir los datos anteriores de la petición, error: {e}")
            logger.registrarLogEror(f"No se ha podido escribir los datos del JSON para peticiones anteriores.", "escribirDatosAnterioresJSON")

    def orquestarArmado(self):
        """
        Este metodo orquesta el renombre,
        y armado de las carpetas según disposición.
        """
        leerJsonComplementarios = self.lecturaJSON() # Lectura de JSON complementarios para configuración
        if(leerJsonComplementarios):
            neps.dataNomenclatura = self.dataNomenclaJSON["renombreZentriaNEPS"] # Asignación de atributo de renombre de Zentria
            datos = peti.obtenerListadoFacturas() # Se obtienen los datos de las cuentas a renombrar
            self.__cuentasArmar = datos # Listado con datos de cuentas armar.
            if(len(datos) > 0):
                self.escribirDatosAnterioresJSON(datos)
                cuentasNoArmables = [] # Listado de cuentas alerta
                for factura in datos:
                    validacionExitencia = self.existeCarpeta(factura["numero_factura"]) # Validación si existe carpeta de cuenta
                    if(validacionExitencia == False):
                        cuentasNoArmables.append(factura)
                        self.__cuentasArmar.remove(factura) # Si no existe, no se procesará.
                if(len(self.__cuentasArmar) > 0): # Armado de cuentas.
                    for cuenta in self.__cuentasArmar:
                        rutaSoportesFactura = path.join(self.rutaSopsDescargados, cuenta["numero_factura"])
                        neps.copiadoSop(rutaSoportesFactura, cuenta["numero_factura"], "NEPS") # Copiado de soportes
                        neps.tratadoArchivosCargueSoportes("NEPS", cuenta["numero_factura"]) # Tratado de archivos en carpeta Cargue Archivos
                        neps.renombrarArchivos("NEPS", cuenta["numero_factura"]) # Renombre de archivos
                        neps.copiadoFactura(self.rutaFacturasDescarg, cuenta["numero_factura"], "NEPS") # Copiado de factura
                        neps.moverSegunRegimen("NEPS", cuenta["regimen"], cuenta["numero_factura"]) # Se mueve la cuenta de la carpeta de armados, a la del regimen
                        neps.renombrarPDEconOTRO("NEPS", cuenta["regimen"], cuenta["numero_factura"], "PDE", "OTR") # ! Se renombra un archivo en especifico Es temporal
                        peti.actualizarEstadoCuenta(cuenta["id_pdf"], "armado_cuentas") # Actualización de estado.
                    neps.controlFinal()
                else:
                    logger.registrarLogEror(f"La API ha retornado datos, pero no ha encontrado carpetas para armar.", "orquestarArmado")
            else:
                logger.registrarLogEror(f"La respuesta de la API no ha devuelto datos.", "orquestarArmado")


        