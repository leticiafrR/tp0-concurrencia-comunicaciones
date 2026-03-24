package common

import (
	"io"
	"net"
	"strconv"
)

const (
	U8_SIZE             = 1
	U16_SIZE            = 2
	END_OF_TRANSMISSION = 0
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

func (b *ClientProtocol) MeetServer() error {
	agencyID := []byte{b.agencyID}
	err := b.sendBytes(agencyID)
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

func (b *ClientProtocol) SendLastBatch(batchBuilder *BatchSerializer) {
	err := b.sendBatchAndConfirm(batchBuilder)
	if err != nil {
		return
	}
	if b.sendEndOfBetTransmission() != nil {
		log.Errorf("action: stop_transmission | result: fail | client_id: %v", b.agencyID)
		return
	}
}

func (b *ClientProtocol) ReceiveWinners() ([]string, error) {
	buff := make([]byte, U8_SIZE)
	err := b.receiveBytes(buff)
	if err != nil {
		return nil, err
	}
	winnersAmount := uint8(buff[0])
	winners := make([]string, 0, winnersAmount)
	for i := 0; i < int(winnersAmount); i++ {
		winner, err := b.receiveString()
		if err != nil {
			log.Errorf("action: receive_winners | result: fail | client_id: %v | error: %v", b.agencyID, err)
			return nil, err
		}
		winners = append(winners, winner)
	}
	return winners, nil
}

func (b *ClientProtocol) sendBytes(msg []byte) error {
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

func (b *ClientProtocol) receiveString() (string, error) {
	stringSize, err := b.receiveU16()
	if err != nil {
		return "", err
	}
	buf := make([]byte, stringSize)
	err = b.receiveBytes(buf)
	return string(buf), err
}

func (b *ClientProtocol) receiveU16() (uint16, error) {
	buf := make([]byte, U16_SIZE)
	err := b.receiveBytes(buf)
	return deserializeUint16(buf), err

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

func (b *ClientProtocol) sendBatchAndConfirm(batchBuilder *BatchSerializer) error {
	batch := batchBuilder.BuildBatch()
	err := b.sendBytes(batch)
	if err != nil {
		log.Errorf("action: send_batch | result: fail | client_id: %v | error: %v", b.agencyID, err)
		return err
	}
	codeError, err := b.ReceiveConfirmation()
	if (err != nil && err != io.EOF) || !codeError {
		log.Errorf("action: receive_confirmation | result: fail | client_id: %v | confirmation: %v | error: %v", b.agencyID, codeError, err)

	}
	return err
}

func (b *ClientProtocol) sendEndOfBetTransmission() error {
	return b.sendBytes([]byte{END_OF_TRANSMISSION})
}
