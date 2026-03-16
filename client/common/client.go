package common

import (
	"net"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config      ClientConfig
	keepWorking bool
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config:      config,
		keepWorking: true,
	}
	return client
}

func (c *Client) createClientSocket() (net.Conn, error) {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	return conn, nil
}

func (c *Client) Run() {
	conn, err := c.createClientSocket()
	if err != nil {
		log.Errorf("action: create_client_socket | result: fail | client_id: %v | error: %v", c.config.ID, err)
		return
	}
	protocol := NewClientProtocol(conn)
	bet := &Bet{
		Name:     "John",
		LastName: "Doe",
		Document: uint32(12345678),
		Year:     uint16(1990),
		Month:    uint8(1),
		Day:      uint8(1),
		Number:   uint16(1000),
	}
	err = protocol.SendMessage(bet)
	if err != nil {
		log.Errorf("action: apuesta_enviada | result: fail | dni: %v | error: %v",
			bet.Document,
			err,
		)
		return
	}
	isConfirmed, err := protocol.ReceiveConfirmation()
	if err != nil || !isConfirmed {
		log.Errorf("action: apuesta_enviada | result: fail | dni: %v | error: %v",
			bet.Document,
			err,
		)
		return
	}
	log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v", bet.Document, bet.Number)

	protocol.Shutdown()
}
