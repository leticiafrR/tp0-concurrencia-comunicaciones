package common

import (
	"net"
	"strconv"
)

type ClientProtocol struct {
	conn     net.Conn
	agencyID uint8
}

func NewClientProtocol(conn net.Conn, strAgencyID string) *ClientProtocol {
	agencyID, err := strconv.Atoi(strAgencyID)
	if err != nil {
		log.Error("action: parse_agency_id | result: failure | error: " + err.Error())
		agencyID = 0
	}
	return &ClientProtocol{conn, uint8(agencyID)}

}

func (b *ClientProtocol) MeetClient() error {
	agencyID := []byte{b.agencyID}
	err := b.SendBytes(agencyID)
	if err != nil {
		log.Error("action: send_agency_id | result: failure | error: " + err.Error())
		return err
	}
	return nil
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
