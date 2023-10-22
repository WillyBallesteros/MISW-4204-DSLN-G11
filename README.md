# MISW-4204-DSLN-G11


# Proyecto

Proyecto Desarrollo Software en la Nube

## Requisitos

- PostgresSQL: en la máquina host debe estar instalado postgresSQL con una base de datos creada. Por defecto se utiliza el ROL postgres con la base de datos cloudb pero se puede cambiar en archivo .env de ms_api
- RabbitMQ: en la máquina host debe estar instalado el broker de mensajería RabbitMQ instalado
- Docker Compose: en la máquina host debe estar instalado Docker y Docker Compose

### Configuración
Sigue estos pasos para configurar y ejecutar el proyecto:

#### 1. Clona el repositorio

#### 2. Crea la imagen:

docker-compose build

#### 3. Despliega la imagen:

docker-compose up

#### 4. Comandos para revisar el estado de los contenedores:
docker-compose stats: muestra es estado de consumo de los contenedores
docker-compose ps: lista los servicios
docker-compose logs ms_api: muestra la salida por consola del servicio ms_api
docker-compose logs ms_worker: muestra la salida por consola del servicio ms_worker
