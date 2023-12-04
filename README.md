# MISW-4204-DSLN-G11


# Proyecto

Proyecto Desarrollo Software en la Nube entrega 3

## Requisitos

- Acceso a cloud run y artifact registry
- Tener creada una base de datos Cloud SQL de tipo postgres 14
- Tener acceso a cloud storage 
- Tener acceso a pub/sub storage

### Configuración
Sigue estos pasos para configurar y ejecutar el proyecto:

#### 1. Configurar Cloud Storage
1. Crear un nuevo bucket llamado misw-4204_video_files
2. Desmarcar la opción de protección para acceso público
3. Modificar el tipo de permisos para que permita una granularidad fina
#### 2. Configurar PUB/SUB
1. Acceder al servicio de pub/sub
2. Crear los tópicos EVENTS y TASKS, deshabilitando la opción de crear suscriptor por defecto.
3. Crear las subscripciones EVENTS y TASKS en modo pull y con un deadline de ack de 300 segundos  
#### 3. Configurar Artifact Registry
1. Crear un repositorio en artifact registry llamado container-ws
2. Copiar la ruta del recurso
#### 4. Crear y configurar el servicio de servidor web en cloud run:
1. En cloud shell ejecutar
```
  git clone https://github.com/WillyBallesteros/MISW-4204-DSLN-G11.git
  cd MISW-4204-DSLN-G11/ms_api
  docker build -t us-docker.pkg.dev/tfg-demo-318500/container-ws/web_server .
  docker push us-docker.pkg.dev/tfg-demo-318500/container-ws/web_server
```
2. Habilitar los permisos requeridos en AIM en el usuario utilizado por google cloud run para acceso a Pub/Sub, Storage y Cloud SQL
3. Habilitar el acceso desde el servicio a CLoud SQL
4. Configurar el servicio con 2 cpu , 2 gb de memoria ram y las politicas de escalamiento
5. Crear el servicio
#### 5. Crear y configurar el servicio de worker en cloud run:
1. En cloud shell ejecutar
```
  git clone https://github.com/WillyBallesteros/MISW-4204-DSLN-G11.git
  cd MISW-4204-DSLN-G11/ms_worker
  docker build -t us-docker.pkg.dev/tfg-demo-318500/container-ws/worker .
  docker push us-docker.pkg.dev/tfg-demo-318500/container-ws/worker
```
2. Configurar el servicio con 2 cpu siempre asignados de 2da generación, 2 gb de memoria ram y las politicas de escalamiento
3. Crear el servicio