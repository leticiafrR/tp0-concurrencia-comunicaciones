def deserializeString(seq :bytes)->str:
    return seq.decode('utf-8')

def deserializeInt(seq :bytes)->int:
    return int.from_bytes(seq, byteorder='big',signed=False)

def serializeBool(flag:bool)->bytes:
    # 1 para confirmación, 0 para rechazo
    return b'\x01' if flag else b'\x00'

def serializeUint8(num: int) -> bytes:
    return num.to_bytes(1, byteorder='big', signed=False)

def serializeUint16(num: int) -> bytes:
    return num.to_bytes(2, byteorder='big', signed=False)

def serializeString(value: str) -> bytes:
    encoded_value = value.encode('utf-8')
    return serializeUint16(len(encoded_value)) + encoded_value

def serializeWinners(winners: list[str]) -> bytes:
    if len(winners) > 255:
        raise ValueError("too many winners for one agency")

    payload = bytearray()
    payload.extend(serializeUint8(len(winners)))
    for winner_document in winners:
        payload.extend(serializeString(winner_document))
    return bytes(payload)