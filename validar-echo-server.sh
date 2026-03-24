SERVER_HOST="server"
SERVER_PORT=12345
MSG="Hola_Distribuidos"
NETWORK="tp0_testing_net"

RESULTADO=$(docker run --rm \
    --network $NETWORK \
    alpine sh -c "echo $MSG | nc -w 2 $SERVER_HOST $SERVER_PORT 2>/dev/null" 2>/dev/null)

if [ "$RESULTADO" = "$MSG" ] && [ ! -z "$RESULTADO" ]; then
    echo "action: test_echo_server | result: success"
    exit 0
else
    echo "action: test_echo_server | result: fail"
    exit 1
fi