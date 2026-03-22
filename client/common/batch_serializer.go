package common

const (
	MAX_BATCH_BYTES   = 8000
	IDX_BETS_IN_BATCH = 1
	IDX_TYPE_MSG      = 0
	TYPE_NOT_BATCH    = 0
	TYPE_BATCH        = 1
)

type BatchSerializer struct {
	batchBuffer     []byte
	maxBytesByBatch int
	cantBets        int
	maxBetsByBatch  int
}

func NewBatchSerializer(maxBytesByBatch int) *BatchSerializer {
	return &BatchSerializer{
		batchBuffer:     reserveBatchBuffer(MAX_BATCH_BYTES),
		maxBytesByBatch: MAX_BATCH_BYTES,
		cantBets:        0,
		maxBetsByBatch:  maxBytesByBatch,
	}
}

func (b *BatchSerializer) AddBet(bet *Bet) bool {
	if !b.canAddBet(bet.Len()) {
		return false
	}
	b.batchBuffer = SerializeOneBet(b.batchBuffer, bet)
	b.cantBets++
	return true
}

func (b *BatchSerializer) BuildBatch() []byte {
	b.batchBuffer[IDX_BETS_IN_BATCH] = uint8(b.cantBets)
	return b.batchBuffer
}

func (b *BatchSerializer) Reset() {
	b.batchBuffer = reserveBatchBuffer(b.maxBytesByBatch)
	b.cantBets = 0
}

func (b *BatchSerializer) IsEmpty() bool {
	return b.cantBets == 0
}

func (b *BatchSerializer) canAddBet(betSize int) bool {
	return (b.cantBets < b.maxBetsByBatch) && (len(b.batchBuffer)+betSize <= b.maxBytesByBatch)
}

func reserveBatchBuffer(maxBatchSize int) []byte {
	buff := make([]byte, U16_SIZE, maxBatchSize)
	buff[IDX_TYPE_MSG] = TYPE_BATCH
	return buff
}
