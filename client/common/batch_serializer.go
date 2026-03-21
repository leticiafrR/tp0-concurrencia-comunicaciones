package common

const (
	MAX_BATCH_BYTES = 8000
)

type BatchSerializer struct {
	batchBuffer     []byte
	maxBytesByBatch int
	cantBets        int
	maxBetsByBatch  int
}

func NewBatchSerializer(maxBytesByBatch int) *BatchSerializer {
	buffer := reserveBatchBuffer(MAX_BATCH_BYTES)
	buffer[0] = 0 //initialize buffer with 0s
	buffer[1] = 0
	return &BatchSerializer{batchBuffer: buffer, maxBytesByBatch: MAX_BATCH_BYTES, cantBets: 0, maxBetsByBatch: maxBytesByBatch}
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
	bytesSizeTmp := make([]byte, 0, TWO_BYTES)
	bytesSizeTmp = SerializeUint16(uint16(b.cantBets), bytesSizeTmp)
	b.batchBuffer[0] = bytesSizeTmp[0]
	b.batchBuffer[1] = bytesSizeTmp[1]
	return b.batchBuffer
}

func (b *BatchSerializer) canAddBet(betSize int) bool {
	return (b.cantBets < b.maxBetsByBatch) && (len(b.batchBuffer)+betSize <= b.maxBytesByBatch)
}

func reserveBatchBuffer(maxBatchSize int) []byte {
	return make([]byte, TWO_BYTES, maxBatchSize)
}

func (b *BatchSerializer) Reset() {
	b.batchBuffer = reserveBatchBuffer(b.maxBytesByBatch)
	b.cantBets = 0
}
func (b *BatchSerializer) IsEmpty() bool {
	return b.cantBets == 0
}
