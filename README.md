# MISW-4204-DSLN-G11


# Proyecto

Proyecto Desarrollo Software en la Nube entrega 3

## Requisitos

- Acceso por SSH a 3 instancias ubuntu 20 de gcloud para desplegar los servicio requeridos (no se incluye la llave en el repositorio pero está disponible para verificación)
- Tener creada una base de datos Cloud SQL de tipo postgres 14 con la conexión privada abierta
- Tener acceso a cloud storage 

### Configuración
Sigue estos pasos para configurar y ejecutar el proyecto:

#### 1. Configurar Cloud Storage
1. Crear un nuevo bucket llamado misw-4204_video_files
2. Desmarcar la opción de protección para acceso público
3. Modificar el tipo de permisos para que permita una granularidad fina
#### 2. Configurar RabbitMQ
1. Acceder por ssh a la instancia rabbit-mq
2. Instalar y configurar el broker de mensajería:
   sudo apt-get update
   sudo apt-get upgrade
   sudo apt-get install rabbitmq-server
   sudo systemctl enable rabbitmq-server
   sudo systemctl start rabbitmq-server
   sudo systemctl status rabbitmq-server
   listeners.tcp.default = 5672
   sudo nano /etc/rabbitmq/rabbitmq.conf
   sudo systemctl restart rabbitmq-server
   sudo ufw allow 5672
3. Habilitar monitoreo:
   sudo rabbitmq-plugins enable rabbitmq_management
   sudo systemctl restart rabbitmq-server
#### 3. Crear y configurar el grupo de servidor web:
1. En una instancia, instalar requerimientos (docker, nginx y client nfs):
```
  sudo apt install nginx
  sudo systemctl status nginx
  sudo systemctl start nginx
  sudo ufw allow 'Nginx HTTP'
  sudo apt install apt-transport-https ca-certificates curl software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
  sudo apt update
  sudo apt install docker-ce
  sudo apt install nfs-common
```
2. Clonar el repositorio
3. De ser necesario, actualizar el archivo .env
4. Construir y ejecutar imagen docker:
```
  cd /RUTA_BASE/MISW-4204-DSLN-G11/ms_api
  sudo docker build -t web_server:tag .
  sudo docker run --restart always -p 127.0.0.1:5000:5000 --name web_server -v /RUTA_BASE/MISW-4204-DSLN-G11/ms_api:/app web_server:tag
```
5. Configurar nginx como proxy inverso:
```
  Editar con  /etc/nginx/sites-enabled/default:
  server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
  }

  Ejecutar:
    sudo nginx -t
    sudo systemctl restart nginx
```
6. Apagar la instancia y desde la opción de consola crear un grupo llamado web-server-grup a partir de la instancia
7. Configurar las poíticas de escalamiento.
#### 4. Configurar el Load Balancer:
1. Crear un load balancer del tipo Classic Application Load Balancer
2. Configurar en front-end indicando que las paticiones son por http al puerto 80
3. Crear y configurar un health check a la ruta /api/health
4. Configurar el backend para que apunte al grupo web-server-group
#### 5. Configurar worker:
1. Instalar requerimientos (docker y client nfs):
```
  sudo apt install apt-transport-https ca-certificates curl software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
  sudo apt update
  sudo apt install docker-ce
  sudo apt install nfs-common
```
2. Clonar el repositorio
3. Construir y ejecutar imagen docker:
```
  cd /RUTA_BASE/MISW-4204-DSLN-G11/ms_worker
  sudo docker build -t worker:tag .
  sudo docker run --restart always -d --name worker -v /RUTA_BASE/MISW-4204-DSLN-G11/ms_worker:/app -v /RUTA_BASE/MISW-4204-DSLN-G11/tmp:/app/tmp worker:tag
```
