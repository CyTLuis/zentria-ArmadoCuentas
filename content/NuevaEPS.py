# ===========================================================================
# Importaciones de clases y librerias necesarias en este archivo main
# ===========================================================================
# Region -  Importaciones de archivos o librerias
from shutil import copytree, copy2, move
from os import listdir, path, rename, remove, system
from pypdf import PdfWriter
from typing import Dict, List


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

        self.__pacientesConErrores = []
        self.__pacientesSinSoportes = []
        self.__pacientesSinFacturas = []

        self.soportes: Dict[str, List[str]] = {
            "PDX": [],
            "HAM": [],
            "HAU": [],
            "TRIAGE": []
        }
    
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
            rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta) # Se busca la cuenta en la carpeta de soportes descargados.
            if(path.isdir(ruta) == False or len(listdir(ruta)) == 0): # En caso de no existir o no tener soportes, se reportará
                self.__pacientesSinSoportes(cuenta)
            else:
                copytree(ruta, rutaCarpetaPacienteArmado, dirs_exist_ok = True) # Copia del archivo completo
                consola.imprimirProceso(f"Se ha hecho el copiado del arbol para la cuenta: {cuenta}")
        except Exception as e:
            consola.imprimirError(f"Error en la cuenta: {cuenta}, en el copiado del arbol, con error: {e}")
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
            # rutaCarpetaPacienteFactura = path.join(ruta, cuenta) # Ruta de la factura actual [Donde se descarga la factura]
            rutaFacturaPaciente = path.join(ruta, f"{cuenta}.pdf") # Ruta total donde se descargo la factura del paciente.
            if(path.isfile(rutaFacturaPaciente)): # Valida si existe la factura correctamente.
                copy2(rutaFacturaPaciente, rutaCarpetaPacienteArmado) # Copia la factura de donde se descargo, a la ruta del armado.
                rutaFacturaCopiada = path.join(rutaCarpetaPacienteArmado, f"{cuenta}.pdf") # Ruta de la factura copiada en la carpeta del armado.
                cuenta = cuenta.replace("CASM-", "CASM") # Reemplazo para renombre de la factura
                strNomenSoporte = self.dataNomenclatura["renombreFactura"] # Nomenclatura para renombre de factura.
                strRenombreFactura = strNomenSoporte.replace("$soporte", "FVS").replace("$nit", self.__nitEntidad).replace("$factura", cuenta) # Formateo de str de nuevo nombre
                rename(rutaFacturaCopiada, path.join(rutaCarpetaPacienteArmado, strRenombreFactura))
            else:
                consola.imprimirProceso(f"No existe factura para la cuenta: {cuenta}.")
                self.__pacientesSinFacturas.append(cuenta)
        except Exception as e:
            self.__pacientesSinFacturas.append(cuenta)
            consola.imprimirError(f"Fallo con factura de cuenta: {cuenta}, para copiar la factura, error: {e}")
            logger.registrarLogEror(f"Error reportado en el armado de cuentas, y copia de archivos, error: {e}", "copiadoSoportes")
    
    def _manejarError(self, error: Exception, cuenta: str, tipo_soporte: str):
        consola.imprimirError(f"Error reportado desde la unión de los archivos {tipo_soporte} de la cuenta: {cuenta}, con error: {error}")
        logger.registrarLogEror(f"Error haciendo el tratado de soporte de tipo [{tipo_soporte}] de la cuenta: {cuenta}, error: {error}", "renombrarArchivos")

    def validarSoportesTratadoDiferente(self, soporte: str, rutaCarpPacArmado: str, cuenta: str, momento: int, strNombreSoporte: str = None):
        """
        En caso de tener soportes que se unan desde el inicio del
        proceso, se deberán identificar y ordenar en una lista
        para hacer su tratado.
        - `Args:`
            - `soporte (str)`: Nombre del soporte
            - `rutaCarpPacArmado (str)`: Ruta del soporte completo.
            - `cuenta (str)`: Cuenta o factura que se esta armando.
            - `momento (int)`: Identificador del momento del metodo.
            - `strNombreSoporte (str)`: Variable de renombre desde el JSON para soporte.
        """
        if momento == 1:
            if "PDX" in soporte or "PDX50" in soporte:
                self.soportes["PDX"].append(path.join(rutaCarpPacArmado, soporte))
            elif "HAM" in soporte:
                self.soportes["HAM"].append(path.join(rutaCarpPacArmado, soporte))
            elif "HAU" in soporte:
                self.soportes["HAU"].append(path.join(rutaCarpPacArmado, soporte))
            elif "TRIAGE" in soporte:
                self.soportes["TRIAGE"].append(path.join(rutaCarpPacArmado, soporte))
        elif momento == 2:
            try:
                if len(self.soportes["PDX"]) > 0:
                    self.unirArchivos(self.soportes["PDX"], rutaCarpPacArmado, "PDX")
                    strRenombreSoporte = strNombreSoporte.replace("$soporte", "PDX").replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    nombrePDX = "PDX.pdf" if path.isfile(path.join(rutaCarpPacArmado, "PDX.pdf")) else "PDX50.pdf"
                    rename(path.join(rutaCarpPacArmado, nombrePDX), path.join(rutaCarpPacArmado, strRenombreSoporte))
            except Exception as e:
                self._manejarError(e, cuenta, "PDX")
            try:
                if len(self.soportes["HAM"]) > 0:
                    self.unirArchivos(self.soportes["HAM"], rutaCarpPacArmado, "HAM")
                    nombreHAM = strNombreSoporte.replace("$soporte", "HAM").replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    rename(path.join(rutaCarpPacArmado, "HAM.pdf"), path.join(rutaCarpPacArmado, nombreHAM))
            except Exception as e:
                self._manejarError(e, cuenta, "HAM")
            try:
                if len(self.soportes["HAU"]) > 0:
                    if len(self.soportes["TRIAGE"]) > 0:
                        self.soportes["HAU"].insert(0, self.soportes["TRIAGE"][0])
                    self.unirArchivos(self.soportes["HAU"], rutaCarpPacArmado, "HAU")
                    strRenombreSoporte = strNombreSoporte.replace("$soporte", "HAU").replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    rename(path.join(rutaCarpPacArmado, "HAU.pdf"), path.join(rutaCarpPacArmado, strRenombreSoporte))
            except Exception as e:
                self._manejarError(e, cuenta, "HAU")

    def renombrarArchivos(self, eps: str, cuenta: str):
        """
        Este metodo recorrerá todas las carpetas de radicado,
        identificando los soportes y renombrando según el orden
        que se trae en su nomenclatura.
        - `Argumentos:`
            - `eps:` (str) Abreviatura de la EPS que se esta procesando.
            - `cuenta:` (str) Cuenta o factura que se esta iterando y se hará renombre de archivos.
        """
        self.soportes["PDX"].clear(), self.soportes["HAM"].clear(), self.soportes["HAU"].clear(), self.soportes["TRIAGE"].clear()
        rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta)
        cuenta = cuenta.replace("CASM-", "CASM")
        strNomenSoporte = self.dataNomenclatura["renombreSoporte"]
        try:
            if(len(listdir(rutaCarpetaPacienteArmado)) > 0): # Si hay archivos en la carpeta, se inicia proceso
                consola.imprimirProceso(f"Se empezará el proceso de renombrado de la cuenta: {cuenta}.")
                for soporte in listdir(rutaCarpetaPacienteArmado):
                    try: # Primero se valida los soportes de tratado especial.
                        if any(subcadena in soporte for subcadena in ["PDX", "PDX50", "HAM", "HAU", "TRIAGE"]):
                            self.validarSoportesTratadoDiferente(soporte, rutaCarpetaPacienteArmado, cuenta, 1)
                        else:
                            soporteRecorrido = path.splitext(soporte)
                            nombreSoporte = soporteRecorrido[0] if "Admision" not in soporteRecorrido[0] else "CRC" # En caso de ser admisión se llamará CRC
                            strRenombreSoporte = strNomenSoporte.replace("$soporte", nombreSoporte).replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                            if(path.isfile(path.join(rutaCarpetaPacienteArmado, soporte))):
                                rename(path.join(rutaCarpetaPacienteArmado, soporte), path.join(rutaCarpetaPacienteArmado, strRenombreSoporte))
                                if(path.isfile(path.join(rutaCarpetaPacienteArmado, soporte))):
                                    remove(path.join(rutaCarpetaPacienteArmado, soporte))
                    except Exception as e:
                        logger.registrarLogEror(f"Error en el renombre del soporte: {soporte} de la cuenta: {cuenta}, error: {e}", "renombrarArchivos")
                self.validarSoportesTratadoDiferente(soporte, rutaCarpetaPacienteArmado, cuenta, 2, strNomenSoporte)
            else:
                self.__pacientesSinSoportes.append(cuenta)
        except Exception as e:
            self.__pacientesConErrores.append(cuenta)
    
    def tratadoArchivosCargueSoportes(self, eps: str, cuenta: str):
        """
        Este metodo se encargará de tratar aquellos archivos que
        están dentro de la carpeta, cargue de soportes.
        """
        rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta)
        rutaCarpetaPacienteCargue = path.join(rutaCarpetaPacienteArmado, "Cargue de Archivos")
        if(path.isdir(rutaCarpetaPacienteCargue)):
            archivosCargados = listdir(rutaCarpetaPacienteCargue)
            listadosPDE = []
            listadoTAP = []
            listadoPDX = []
            for cargue in archivosCargados:
                rutaSoporteCargue = path.join(rutaCarpetaPacienteCargue, cargue)
                if any(subcadena in cargue for subcadena in ["AUTORIZAC", "SOPORTES CIRUGIA", "DOCUMENTO DE I", "DE DERECHOS", "PDX", "PDXCA", "COTIZACIONES", "VIRAL"]):
                    listadosPDE.append(rutaSoporteCargue)
                if any(subcadena in cargue for subcadena in ["TRASLADO"]):
                    listadoTAP.append(rutaSoporteCargue)
                if any(subcadena in cargue for subcadena in ["ELECTRO", "AYUDAS"]):
                    listadoPDX.append(rutaSoporteCargue)
                
            if(len(listadosPDE) > 0):
                self.unirArchivos(listadosPDE, rutaCarpetaPacienteCargue, "PDE")
                if(path.isfile(path.join(rutaCarpetaPacienteArmado, "PDE.pdf"))):
                    listaMultiplesPDE = [path.join(rutaCarpetaPacienteCargue, "PDE.pdf"), path.join(rutaCarpetaPacienteArmado, "PDE.pdf")]
                    self.unirArchivos(listaMultiplesPDE, rutaCarpetaPacienteCargue, "PDE")
                move(path.join(rutaCarpetaPacienteCargue, "PDE.pdf"), path.join(rutaCarpetaPacienteArmado, "PDE.pdf"))

            if(len(listadoTAP) > 0):
                self.unirArchivos(listadoTAP, rutaCarpetaPacienteCargue, "TAP")
                move(path.join(rutaCarpetaPacienteCargue, "TAP.pdf"), path.join(rutaCarpetaPacienteArmado, "TAP.pdf"))

            if(len(listadoPDX) > 0):
                self.unirArchivos(listadoPDX, rutaCarpetaPacienteCargue, "PDX")
                move(path.join(rutaCarpetaPacienteCargue, "PDX.pdf"), path.join(rutaCarpetaPacienteArmado, "PDX50.pdf"))

    def unirArchivos(self, listadoSoportesUnir: list, rutaCarpetaGuardar: str, soporte: str):
        """
        Este metodo se encargará de unir los archivos
        usando la librería de PyPDF2 y su metodo Merge
        """
        merger = PdfWriter() # Se instancia el escritor de PDF
        for pdf in listadoSoportesUnir:
            merger.append(pdf) # Se agrega cada full path de los PDF
            remove(pdf) # Se elimina el PDF de la ruta
        merger.write(f"{rutaCarpetaGuardar}\\{soporte}.pdf") # Se unen todos los PDF en uno
        merger.close() # Se cierra la instancia del escritor.
    
    def moverSegunRegimen(self, eps: str, regimen: str, cuenta: str):
        """
        Este metodo será el final del tratado de la cuenta
        pues se encargará de mover la carpeta de armado, a
        la carpeta perteneciente al regimen que trae asignado.
        `Args:`
            `regimen (str):` Regimen de la cuenta que se esta iterando
            `cuenta (str):` Cuenta que se itera
        """
        rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta)
        rutaCarpetaPacientePorRegimen = path.join(self.__rutaArmado, eps, regimen, cuenta)
        move(rutaCarpetaPacienteArmado, rutaCarpetaPacientePorRegimen)

    def controlFinal(self):
        """
        Este metodo se encargará de gestionar los datos
        de las listas que se tienen con datos erroneos,
        o sin soportes, o que han sido erroneos.
        """
        logger.registrarComentario("Pacientes sin facturas", f"{self.__pacientesSinFacturas}")
        logger.registrarComentario("Pacientes sin soportes", f"{self.__pacientesSinSoportes}")
        logger.registrarComentario("Pacientes con errores", f"{self.__pacientesConErrores}")
