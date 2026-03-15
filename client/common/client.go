package common

import (
	"bufio"
	"fmt"
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
	conn        net.Conn
	keepWorking bool
}

func (c *Client) Shutdown() {
	c.keepWorking = false //for avoiding reserve new connections when there is a shutdown signal.
	//  This is executed by spawned goroutine so this may cause a race contidion but this is not
	//  a problem because the worst case scenario is that one more connection is created after the
	//  shutdown signal, but this connection will be closed inmediatly after being used and no more
	//  connections will be created after that.
	if c.conn != nil { // for avoiding close a closed coneection after tbeing replaced with the next one
		fmt.Printf("Gracefull shutdown: Closing connection.\n")
		c.conn.Close()
		log.Info("action: close_connection | result: success")
	} else {
		fmt.Printf("Gracefull shutdown: No connection to close, this was already closed\n")
	}

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

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount && c.keepWorking; msgID++ {
		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()

		// TODO: Modify the send to avoid short-write
		fmt.Fprintf(
			c.conn,
			"[CLIENT %v] Message N°%v\n",
			c.config.ID,
			msgID,
		)
		msg, err := bufio.NewReader(c.conn).ReadString('\n')
		if c.conn != nil {
			c.conn.Close()
			log.Info("action: close_connection | result: success")
		}

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
			c.config.ID,
			msg,
		)

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
