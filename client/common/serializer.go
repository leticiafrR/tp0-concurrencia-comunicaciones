package common

import (
	"encoding/binary"
	"fmt"
	"os"
)

func serializeString(str string, msg []byte) []byte {
	str_size := uint16(len(str))
	msg = serializeUint16(str_size, msg)
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
	fmt.Fprintf(os.Stdout, "action: reserve_buffer | result: success | estimated_size: %v\n", estimatedSize)
	return make([]byte, 0, estimatedSize)
}

func Serialize(bet *Bet) []byte {
	msg := reserveBuffer(bet)
	fmt.Fprintf(os.Stdout, "action: serialize_bet | result: success | name: %v | last_name: %v | dni: %v | year: %v | month: %v | day: %v | number: %v", bet.Name, bet.LastName, bet.Document, bet.Year, bet.Month, bet.Day, bet.Number)
	msg = serializeString(bet.Name, msg)
	fmt.Fprintf(os.Stdout, "\nbuffer after serialize name: %v\n with len: %d", msg, len(msg))
	msg = serializeString(bet.LastName, msg)
	fmt.Fprintf(os.Stdout, "\nbuffer after serialize last name: %v\n with len: %d", msg, len(msg))
	msg = serializeUint32(bet.Document, msg)
	fmt.Fprintf(os.Stdout, "\nbuffer after serialize dni (4 bytes): %v\n with len: %d", msg, len(msg))
	msg = serializeUint16(bet.Year, msg)
	fmt.Fprintf(os.Stdout, "\nbuffer after serialize year (2 bytes): %v\n with len: %d", msg, len(msg))
	msg = append(msg, bet.Month)
	fmt.Fprintf(os.Stdout, "\nbuffer after serialize month (1 byte): %v\n with len: %d", msg, len(msg))
	msg = append(msg, bet.Day)
	fmt.Fprintf(os.Stdout, "\nbuffer after serialize day (1 byte): %v\n with len: %d", msg, len(msg))
	msg = serializeUint16(bet.Number, msg)
	fmt.Fprintf(os.Stdout, "\nbuffer after serialize number (2 bytes): %v\n with len: %d", msg, len(msg))

	return msg
}
