# Zentria Armado Cuentas

> ## Necesidad
>
> Se necesitará tomar la carpeta de los soportes descargados desde el bot de descarga de soporte del sistem GomediSys,, para armar las cuentas de cada uno, con el renombrado de la institución solicitada.
>
> ## Solución
>
> Se crea un proyecto con Python, usando las soluciones ofrecidas para manejo de archivos y directorios, teniendo en cuenta el armado de las rutas según datos que se traen de la API directamente.

### Estructura del desarrollo

1. ***API***

* Se utilizará una API para saber que facturas se deberán armar según aquellas cuentas que ya tengan soportes descargados.

2. ***Rutas absolutas***

* A través de parametros definidos en el archivos ***config.ini*** se darán los parametros de las rutas absolutas donde buscar las carpetas de las cuentas con soportes, o la facturas de cada cuenta.

3. ***Entorno de desarrollo***

* Desde el archivo de ***config.ini*** se establecerá el entorno de desarrollo, en pro de configuraciones adicionales, el entorno por defecto será `dev` en caso de no tener uno definido.

## Comentarios útiles para los procesos de automatización

### Comando para conversión de archivo *".py"* a ejecutable *".exe"*

Comando base para conversión a ejectutable:

* ***py -m PyInstaller  --icon="ruta-absoluta-archivo-ico" ruta-abosulta-main-proyecto***

Banderas de comando para ejecutable:

* **--onefile** Crea el ejecutable en un solo archivo comprimido que lleva el nombre del archivo main pasado, con extensión .exe
* **--windowed** Habilita una ventana de CMD durante la ejecución del programa la cual puede servir como depurador de los print dejados en los archivos **".py"**

Cabe resaltar que se debe tener instalada la libreria **Pyinstaller** antes de realizar este paso. **(pip install pyinstaller)**

## Librerias usadas en este proyecto.

La siguiente es la lista completa de librerias o paquetes usados en el desarrollo de este proyecto, usado en distintos archivos o metodos:

* [pypdf ](https://pypi.org/project/pypdf/) (pip install pypdf) Encargada de gestionar la unión de PDF
* [Requests](https://pypi.org/project/requests/)(pip install requests) Encargada de hacer peticiones a la API
