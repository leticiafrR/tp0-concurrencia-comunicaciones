package common

type BatchBuilder struct {
	batchBuffer  []byte
	maxBatchSize int
	cantBets     int
}

func NewBatchBuilder(maxBatchSize int) *BatchBuilder {
	buffer := reserveBatchBuffer(maxBatchSize)
	buffer[0] = 0 //initialize buffer with 0s
	buffer[1] = 0
	return &BatchBuilder{batchBuffer: buffer, maxBatchSize: maxBatchSize, cantBets: 0}
}

func (b *BatchBuilder) AddBet(bet *Bet) bool {
	if !b.canAddBet(bet.Len()) {
		// fmt.Printf("\n\n\n total de bets: %d | cantidad de bytes: %d | cantidad maxima: %d", b.cantBets, len(b.batchBuffer), b.maxBatchSize)
		return false
	}
	b.batchBuffer = SerializeOneBet(b.batchBuffer, bet)
	b.cantBets++
	return true
}

func (b *BatchBuilder) Build() []byte {
	bytesSizeTmp := make([]byte, 0, TWO_BYTES)
	bytesSizeTmp = SerializeUint16(uint16(b.cantBets), bytesSizeTmp)
	b.batchBuffer[0] = bytesSizeTmp[0]
	b.batchBuffer[1] = bytesSizeTmp[1]
	return b.batchBuffer
}

func (b *BatchBuilder) canAddBet(betSize int) bool {
	return len(b.batchBuffer)+betSize <= cap(b.batchBuffer)
}

func reserveBatchBuffer(maxBatchSize int) []byte {
	return make([]byte, TWO_BYTES, maxBatchSize) //8kB must be configurable
}

func (b *BatchBuilder) Reset() {
	b.batchBuffer = reserveBatchBuffer(b.maxBatchSize)
	b.cantBets = 0
}
