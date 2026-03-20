package common

import (
	"encoding/binary"
)

const (
	TWO_BYTES = 2
)

func SerializeOneBet(buff []byte, bet *Bet) []byte {
	buff = serializeString(bet.Name, buff)
	buff = serializeString(bet.LastName, buff)
	buff = serializeString(bet.Document, buff)
	buff = serializeString(bet.Date, buff)
	buff = serializeString(bet.Number, buff)
	return buff
}

func SerializeUint16(num uint16, buf []byte) []byte {
	tmp := make([]byte, TWO_BYTES)
	binary.BigEndian.PutUint16(tmp, num)
	buf = append(buf, tmp...)
	return buf
}

func serializeString(str string, msg []byte) []byte {
	str_size := uint16(len(str))
	msg = SerializeUint16(str_size, msg)
	msg = append(msg, []byte(str)...)
	return msg
}
