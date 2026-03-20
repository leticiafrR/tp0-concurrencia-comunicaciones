package common

import (
	"fmt"
	"strconv"
	"time"

	"github.com/op/go-logging"
)

const (
	NAME_IDX               = 0
	LASTNAME_IDX           = 1
	DOCUMENT_IDX           = 2
	DATE_IDX               = 3
	NUMBER_IDX             = 4
	GO_DATE_FORMAT_EXAMPLE = "2006-01-02"
)

type Bet struct {
	Name     string
	LastName string
	Document string //uint32
	Date     string //uint16
	Number   string //uint16
}

func NewBetFromRecord(record []string, log *logging.Logger) (*Bet, error) {
	if len(record) < 5 {
		log.Errorf("action: invalid_record | result: fail | reason: not enough fields (%d < 5)", len(record))
		return nil, fmt.Errorf("invalid record length: got %d, expected at least 5", len(record))
	}

	if _, err := time.Parse(GO_DATE_FORMAT_EXAMPLE, record[DATE_IDX]); err != nil {
		log.Errorf("action: invalid_record | result: fail | reason: invalid date format (YYYY-MM-DD but received %q)", record[DATE_IDX])
		return nil, fmt.Errorf("invalid date %q: expected format YYYY-MM-DD", record[DATE_IDX])
	}

	document, err := strconv.Atoi(record[DOCUMENT_IDX])
	if err != nil || document < 0 {
		log.Errorf("action: invalid_record | result: fail | reason: invalid document format (must be a positive number)", record[DOCUMENT_IDX])
		return nil, fmt.Errorf("invalid document %q: must be a positive number", record[DOCUMENT_IDX])
	}

	number, err := strconv.Atoi(record[NUMBER_IDX])
	if err != nil || number < 0 {
		log.Errorf("action: invalid_record | result: fail | reason: invalid number format (must be a positive number greater than zero)", record[NUMBER_IDX])
		return nil, fmt.Errorf("invalid number %q: must be a positive number greater than zero", record[NUMBER_IDX])
	}

	bet := &Bet{
		Name:     record[NAME_IDX],
		LastName: record[LASTNAME_IDX],
		Document: record[DOCUMENT_IDX],
		Date:     record[DATE_IDX],
		Number:   record[NUMBER_IDX],
	}
	log.Infof("action: parse_record | result: success | bet: %v", bet)
	return bet, nil
}

func (b Bet) Len() int {
	return 2 + len(b.Name) + 2 + len(b.LastName) + 2 + len(b.Document) + 2 + len(b.Date) + 2 + len(b.Number)
}
