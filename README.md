# MISW-4204-DSLN-G11


# Proyecto

Proyecto Desarrollo Software en la Nube entrega 2

## Requisitos

- Acceso por SSH a 5 instancias ubuntu 20 de gcloud para desplegar los servicio requeridos (no se incluye la llave en el repositorio pero está disponible para verificación)
- Tener creada una base de datos Cloud SQL de tipo postgres 14 con la conexión privada abierta 

### Configuración
Sigue estos pasos para configurar y ejecutar el proyecto:

#### 1. Configurar servidor NFS
1. Acceder por ssh a la instancia file-server
2. Instalar el servidor de archivos:
```
  sudo apt update
  sudo apt install nfs-kernel-server  
```
3. Crear las carpetas compartidas:
```
  mkdir -p $HOME/video_files/source 
  mkdir -p $HOME/video_files/destination 
```
4. Configurar el archivo /etc/export agregando la línea:
```
  /RUTA_BASE/video_files *(rw,sync,no_subtree_check,all_squash,anonuid=65534,anongid=65534)
```
5. Actualizar los campos con:
```
  sudo exportfs -a
  sudo systemctl restart nfs-kernel-serve
```
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
#### 3. Configurar servidor web:
1. Instalar requerimientos (docker, nginx y client nfs):
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
3. Montar en forma permanente el volumen compartido editando el archivo /etc/fstab
```
  Agregar la línea: IP_NFS_SERVER:/RUTA_BASE/video_files /RUTA_BASE/MISW-4204-DSLN-G11/video_files nfs defaults 0 0
  Ejecutar: sudo mount -a
```
4. De ser necesario, actualizar el archivo .env
5. Construir y ejecutar imagen docker:
```
  cd /RUTA_BASE/MISW-4204-DSLN-G11/ms_api
  sudo docker build -t web_server:tag .
  sudo docker run -d -p 5000:5000 --name web_server -v /RUTA_BASE/MISW-4204-DSLN-G11/ms_api:/app -v /RUTA_BASE/MISW-4204-DSLN-G11/video_files:/app/video_files web_server:tag
```
6. Configurar nginx como proxy inverso:
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
#### 4. Configurar worker:
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
3. Montar en forma permanente el volumen compartido editando el archivo /etc/fstab
```
  Agregar la línea: 
    IP_NFS_SERVER:/RUTA_BASE/video_files /RUTA_BASE/MISW-4204-DSLN-G11/video_files nfs defaults 0 0
  Ejecutar: 
    sudo mount -a
```
4. Construir y ejecutar imagen docker:
```
  cd /RUTA_BASE/MISW-4204-DSLN-G11/ms_worker
  sudo docker build -t worker:tag .
  sudo docker run -d -p 5000:5000 --name worker -v /RUTA_BASE/MISW-4204-DSLN-G11/worker:/app -v /RUTA_BASE/MISW-4204-DSLN-G11/video_files:/app/video_files worker:tag
```
