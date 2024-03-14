# ===========================================================================
# Importaciones de clases y librerias necesarias en este archivo main
# ===========================================================================
# Region -  Importaciones de archivos o librerias
from shutil import copytree, copy2
from os import listdir, path, rename, remove
from pypdf import PdfWriter


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

        self.__existenciaSoportes = {
            "existePDX": False,
            "existeTRIAGE": False,
            "existeHAU": False,
        }
        self.__pacientesSinSoportes = []
        self.__pacientesSinFacturas = []
    
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
            rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta) # Ruta en la carpeta de cuentas armadas, por paciente
            rutaCarpetaPacienteFactura = path.join(ruta, cuenta) # Ruta de la factura actual [Donde se descarga la factura]
            rutaFacturaPaciente = path.join(rutaCarpetaPacienteFactura, f"{cuenta}.pdf") # Ruta total donde se descargo la factura del paciente.
            if(path.isfile(rutaFacturaPaciente)): # Valida si existe la factura correctamente.
                copy2(rutaFacturaPaciente, rutaCarpetaPacienteArmado) # Copia la factura de donde se descargo, a la ruta del armado.
                rutaFacturaCopiada = path.join(rutaCarpetaPacienteArmado, f"{cuenta}.pdf") # Ruta de la factura copiada en la carpeta del armado.
                cuenta = cuenta.replace("CASM-", "CASM") # Reemplazo para renombre de la factura
                strNomenSoporte = self.dataNomenclatura["renombreFactura"] # Nomenclatura para renombre de factura.
                strRenombreFactura = strNomenSoporte.replace("$soporte", "FEV").replace("$nit", self.__nitEntidad).replace("$factura", cuenta) # Formateo de str de nuevo nombre
                rename(rutaFacturaCopiada, path.join(rutaCarpetaPacienteArmado, strRenombreFactura))
            else:
                self.__pacientesSinFacturas.append(cuenta)
        except Exception as e:
            self.__pacientesSinFacturas.append(cuenta)
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
        cuenta = cuenta.replace("CASM-", "CASM")
        strNomenSoporte = self.dataNomenclatura["renombreSoporte"]
        existenPDX = False 
        listadoPDX = []
        existenHAU = False 
        listadoHAU = []
        existenTRIAGE = False 
        listadoTRIAGE = []
        if(len(listdir(rutaCarpetaPacienteArmado)) > 0):
            for soporte in listdir(rutaCarpetaPacienteArmado):
                try:
                    if("PDX" in soporte):
                        existenPDX = True 
                        listadoPDX.append(path.join(rutaCarpetaPacienteArmado, soporte))
                    elif("HAU" in soporte):
                        existenHAU = True 
                        listadoHAU.append(path.join(rutaCarpetaPacienteArmado, soporte))
                    elif("TRIAGE" in soporte):
                        existenTRIAGE = True 
                        listadoTRIAGE.append(path.join(rutaCarpetaPacienteArmado, soporte))
                    else:
                        soporteRecorrido = path.splitext(soporte)
                        nombreSoporte = soporteRecorrido[0] if "Admision" not in soporteRecorrido[0] else "CRC"
                        strRenombreSoporte = strNomenSoporte.replace("$soporte", nombreSoporte).replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                        rename(path.join(rutaCarpetaPacienteArmado, soporte), path.join(rutaCarpetaPacienteArmado, strRenombreSoporte))
                except Exception as e:
                    logger.registrarLogEror(f"Error en el renombre del soporte: {soporte} de la cuenta: {cuenta}, error: {e}", "renombrarArchivos")
            try: # Si existen archivos de tipo PDX, el bot unira los PDF en caso de ser necesario, y hará el renombre.
                if(existenPDX):
                    if(len(listadoPDX) > 1):                        
                        self.unirArchivos(listadoPDX, rutaCarpetaPacienteArmado, "PDX") # Unión de PDFs con el nombre PDX#
                    strRenombreSoporte = strNomenSoporte.replace("$soporte", "PDX").replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    rename(path.join(rutaCarpetaPacienteArmado, "PDX.pdf"), path.join(rutaCarpetaPacienteArmado, strRenombreSoporte))

                if(existenHAU):
                    if(len(listadoHAU) > 0):
                        if(existenTRIAGE and len(listadoTRIAGE) > 0):
                            listadoHAU.append(listadoTRIAGE[0])
                        self.unirArchivos(listadoHAU, rutaCarpetaPacienteArmado, "HAU") # Unión de PDFs con el nombre HAU
                    strRenombreSoporte = strNomenSoporte.replace("$soporte", "HAU").replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    rename(path.join(rutaCarpetaPacienteArmado, "HAU.pdf"), path.join(rutaCarpetaPacienteArmado, strRenombreSoporte))

            except Exception as e:
                print(e)
                logger.registrarLogEror(f"Error haciendo el tratado de soporte de tipo [PDX] de la cuenta: {cuenta}, error: {e}", "renombrarArchivos")
        else:
            self.__pacientesSinSoportes.append(cuenta)
    
    def unirArchivos(self, listadoSoportesUnir: list, rutaCarpetaGuardar: str, soporte: str):
        """
        Este metodo se encargará de unir los archivos
        usando la librería de PyPDF2 y su metodo Merge
        """
        merger = PdfWriter()
        for pdf in listadoSoportesUnir:
            merger.append(pdf)
            remove(pdf)
        merger.write(f"{rutaCarpetaGuardar}\\{soporte}.pdf")
        merger.close()
