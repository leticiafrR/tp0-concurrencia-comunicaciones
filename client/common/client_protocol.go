package common

import (
	"net"
)

type ClientProtocol struct {
	conn net.Conn
}

func NewClientProtocol(conn net.Conn) *ClientProtocol {
	c := &ClientProtocol{conn}

	return c
}

func (b *ClientProtocol) ReceiveConfirmation() (bool, error) {
	buf := make([]byte, 1)
	err := b.receiveBytes(buf)
	if err != nil {
		return false, err
	}
	return buf[0] == 1, nil
}

func (b *ClientProtocol) Shutdown() {
	if b.conn != nil {
		b.conn.Close()
		log.Info("action: close_connection | result: success")
	}
}

func (b *ClientProtocol) SendBytes(msg []byte) error {
	msg_size := len(msg)
	bytesSent := 0
	for bytesSent < msg_size {
		cant_wrote, err := b.conn.Write(msg[bytesSent:])
		if err != nil {
			return err
		}
		bytesSent += cant_wrote
	}
	return nil
}

func (b *ClientProtocol) receiveBytes(buf []byte) error {
	totalRead := 0
	for totalRead < len(buf) {
		n, err := b.conn.Read(buf[totalRead:])
		if err != nil {
			return err
		}
		totalRead += n
	}
	return nil
}
