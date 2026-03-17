package common

import (
	"net"
	"os"
	"os/signal"
	"syscall"
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
	protocol    *ClientProtocol
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config:      config,
		keepWorking: true,
		protocol:    nil,
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
	return conn, err
}

func (c *Client) Stop() {
	c.keepWorking = false
	if c.protocol != nil {
		c.protocol.Shutdown()
	}
}

func (c *Client) runIteration() {
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

func (c *Client) RegisterSignalHandler() {
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGTERM)
	go func() {
		<-sigChan
		c.Stop()
	}()
}

func (c *Client) Run() {
	c.RegisterSignalHandler()
	for i := 0; i < c.config.LoopAmount && c.keepWorking; i++ {
		c.runIteration()
		time.Sleep(c.config.LoopPeriod)
	}
}
