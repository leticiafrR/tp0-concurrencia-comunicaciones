package common

import (
	"encoding/binary"
)

func serializeString(str string, msg []byte) []byte {
	str_size := uint16(len(str))
	msg = append(msg, serializeUint16(str_size, msg)...)
	msg = append(msg, []byte(str)...)
	return msg
}

func serializeUint16(num uint16, buf []byte) []byte {
	tmp := make([]byte, 2)
	binary.BigEndian.PutUint16(tmp, num)
	buf = append(buf, tmp...)
	return buf
}

func serializeUint32(num uint32, buf []byte) []byte {
	tmp := make([]byte, 4)
	binary.BigEndian.PutUint32(tmp, num)
	buf = append(buf, tmp...)
	return buf
}

func reserveBuffer(bet *Bet) []byte {
	estimatedSize := len(bet.Name) + len(bet.LastName) + 14
	return make([]byte, 0, estimatedSize)
}

func Serialize(bet *Bet) []byte {
	msg := reserveBuffer(bet)
	msg = serializeString(bet.Name, msg)
	msg = serializeString(bet.LastName, msg)
	msg = serializeUint32(bet.Document, msg)
	msg = serializeUint16(bet.Year, msg)
	msg = append(msg, bet.Month)
	msg = append(msg, bet.Day)
	msg = serializeUint16(bet.Number, msg)
	return msg
}
