def deserializeString(seq :bytes)->str:
    return seq.decode('utf-8')

def deserializeInt(seq :bytes)->int:
    return int.from_bytes(seq, byteorder='big',signed=False)

def serializeBool(flag:bool)->bytes:
    # 1 para confirmación, 0 para rechazo
    return b'\x01' if flag else b'\x00'
