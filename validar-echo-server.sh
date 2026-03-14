# Configuración
SERVER_HOST="server"
SERVER_PORT=12345        # Ajusta al puerto que use tu servidor
MSG="Hola_Distribuidos"   # Mensaje de prueba (sin espacios para facilitar nc)
NETWORK="tp0_testing_net"


# 2. Ejecutamos un contenedor efímero con netcat
# Usamos 'alpine' porque es la imagen más liviana que trae nc
RESULTADO=$(docker run --rm \
    --network $NETWORK \
    alpine sh -c "echo $MSG | nc -w 2 $SERVER_HOST $SERVER_PORT")

# 3. Validación de la respuesta
if [ "$RESULTADO" == "$MSG" ]; then
    echo "action: test_echo_server | result: success"
    exit 0
else
    echo "action: test_echo_server | result: fail"
    exit 1
fi