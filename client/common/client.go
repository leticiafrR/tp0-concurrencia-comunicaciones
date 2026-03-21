package common

import (
	"encoding/csv"
	"fmt"
	"io"
	"net"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

const (
	DATA_PATH = ".data/agency-%d.csv"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID              string
	ServerAddress   string
	LoopAmount      int
	LoopPeriod      time.Duration
	CantBetsByBatch int
}

// Client Entity that encapsulates how
type Client struct {
	config         ClientConfig
	bet            *Bet
	shutdownChan   chan struct{}
	protocol       *ClientProtocol
	sourceFile     *os.File
	keepProcessing bool
	batchBuilder   *BatchBuilder
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config:         config,
		shutdownChan:   make(chan struct{}),
		protocol:       nil,
		sourceFile:     nil,
		keepProcessing: true,
		batchBuilder:   NewBatchBuilder(config.CantBetsByBatch),
	}
	return client
}

func (c *Client) reserveResources() error {
	agency_id, _ := strconv.Atoi(c.config.ID)
	f, err := os.Open(fmt.Sprintf(DATA_PATH, agency_id))
	if err != nil {
		log.Fatal(err)
		return err
	}
	c.sourceFile = f

	conn, err := c.createClientSocket()
	if err != nil {
		log.Errorf("action: create_client_socket | result: fail | client_id: %v | error: %v", c.config.ID, err)
		return err
	}
	c.protocol = NewClientProtocol(conn, c.config.ID)
	return nil
}

func (c *Client) releaseResources() error {
	if c.sourceFile != nil {
		c.sourceFile.Close()
		c.sourceFile = nil
	}

	if c.protocol != nil {
		c.protocol.Shutdown()
	}
	return nil
}

func (c *Client) Run() {
	if err := c.reserveResources(); err != nil {
		log.Errorf("action: reserve_resources | result: fail | client_id: %v | error: %v", c.config.ID, err)
		c.releaseResources()
		return
	}
	c.registerSignalHandler()
	reader := csv.NewReader(c.sourceFile)
	c.protocol.MeetClient()
	c.clientLoop(reader)
	c.releaseResources()
}

func (c *Client) clientLoop(reader *csv.Reader) {
	for c.keepProcessing {
		record, err := reader.Read()
		if err == io.EOF {
			c.keepProcessing = false
			if !c.batchBuilder.IsEmpty() {
				c.sendBatchAndConfirm()
			}
			continue
		}

		bet, err := NewBetFromRecord(record, log)

		if err != nil {
			log.Errorf("action: invalid_record | result: fail | client_id: %v | record: %v", c.config.ID, record)
			break
		}

		if !c.batchBuilder.AddBet(bet) {
			if c.sendBatchAndConfirm() != nil {
				break
			}
			c.batchBuilder.Reset()
			c.batchBuilder.AddBet(bet)

		}
	}
}

func (c *Client) sendBatchAndConfirm() error {
	batch := c.batchBuilder.Build()
	err := c.protocol.SendBytes(batch)
	if err != nil {
		log.Errorf("action: send_batch | result: fail | client_id: %v | error: %v", c.config.ID, err)
		return err
	}
	log.Infof("action: send_batch | result: success | client_id: %v", c.config.ID)
	codeError, err := c.protocol.ReceiveConfirmation()
	if (err != nil && err != io.EOF) || !codeError {
		log.Errorf("action: receive_confirmation | result: fail | client_id: %v | confirmation: %v | error: %v", c.config.ID, codeError, err)

	}
	return err
}

func (c *Client) registerSignalHandler() {
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGTERM)
	go func() {
		<-sigChan
		c.Stop()
	}()
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
	close(c.shutdownChan)
	c.releaseResources()
	log.Infof("action: shutdown | result: success | client_id: %v", c.config.ID)
}
