# Desplegar todo el proyecto

Con el comando `run.sh` se despliega todo el proyecto, se compila el código y se ejecuta el programa.

En el archivo `./nginx/.htpasswd` se encuentra el usuario y contraseña para acceder a dagster y mlflow.

Se debe cambiar el password por uno seguro. Para generar un password seguro se puede usar el siguiente comando:

```bash
htpasswd -c ./nginx/.htpasswd yourusername
```

O también se puede usar la siguiente página web para generar el password:

[https://www.htaccesstools.com/htpasswd-generator/](https://www.htaccesstools.com/htpasswd-generator/)

Donde se debe copiar el contenido en el archivo `./nginx/.htpasswd`.

Para desplegar todo el proyecto se debe ejecutar el siguiente comando:

```bash
./run.sh
```

Levanta instancias de dagster, de mlflow y un stack de ELK.

Para detener el proyecto se debe ejecutar el siguiente comando:

```bash
./stop.sh
```

Cada servicio cuenta con su propio `compose.yaml` y su `run.sh` y `stop.sh` para desplegar y detener los servicios de manera independiente.

Todos los servicios se conectan mediante una red llamada `web` en docker

Se crea automáticamente en el archivo `run.sh`  de la raiz del proyecto

También se puede crear la red de manera manual con el siguiente comando:

```bash
docker network create web
```