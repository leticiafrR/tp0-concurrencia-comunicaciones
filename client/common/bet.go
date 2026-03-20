package common

import (
	"fmt"
	"strconv"
	"time"
)

const (
	NAME_IDX     = 0
	LASTNAME_IDX = 1
	DOCUMENT_IDX = 2
	DATE_IDX     = 3
	NUMBER_IDX   = 4
)

type Bet struct {
	Name     string
	LastName string
	Document string //uint32
	Date     string //uint16
	Number   string //uint16
}

func NewBetFromRecord(record []string) (*Bet, error) {
	if len(record) < 5 {
		return nil, fmt.Errorf("invalid record length: got %d, expected at least 5", len(record))
	}

	if _, err := time.Parse("2006-12-28", record[DATE_IDX]); err != nil {
		return nil, fmt.Errorf("invalid date %q: expected format YYYY-MM-DD", record[DATE_IDX])
	}

	document, err := strconv.Atoi(record[DOCUMENT_IDX])
	if err != nil || document <= 0 {
		return nil, fmt.Errorf("invalid document %q: must be a positive number", record[DOCUMENT_IDX])
	}

	number, err := strconv.Atoi(record[NUMBER_IDX])
	if err != nil || number <= 0 {
		return nil, fmt.Errorf("invalid number %q: must be a positive number greater than zero", record[NUMBER_IDX])
	}

	return &Bet{
		Name:     record[NAME_IDX],
		LastName: record[LASTNAME_IDX],
		Document: record[DOCUMENT_IDX],
		Date:     record[DATE_IDX],
		Number:   record[NUMBER_IDX],
	}, nil
}

func (b Bet) Len() int {
	return 2 + len(b.Name) + 2 + len(b.LastName) + 2 + len(b.Document) + 2 + len(b.Date) + 2 + len(b.Number)
}
