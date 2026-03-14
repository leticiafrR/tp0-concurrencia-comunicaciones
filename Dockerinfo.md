# Docker info
## reiniciar y reconstruir una imagen de docker
- El container es el proceso en ejecución 
- La imagen es el molde de piedra

Aveces es suficiente reiniciar el contenedor `docker restart <nombre>` cuando la lógica no es la que cambia. Como por ejemplo:
- Cambios de variable de entorno
- Ajuste de configuración externo: si por ejemplo el archivo está en un volumen (Es decir que está montado desde la computadora al contenedor) entonces el cambio es instantáneo, solo se necesita que la aplicación vuelva a leer el volumen para ver que está diferente.
- En ciertos casos, el código en desarrollo (con volúmenes) y ciertos lenguajes de programación pueden modificarse sin necesidad de reiniciar el contendor. Este mismo detecta el cambio y se refresca solo.


En cambio en las sgts situaciones es obligatorio reconstruir (`docker build` o `docker-compose up --build`):
- si cambia el dockerfile
- se agrega una nueva lib que debe agregarse en una capa de la imagen
- si el código es de **producción** el código fuente se **copia** dentro de la imagen (no funciona con volúmenes de código pues es más lento leerlo de afuera)
