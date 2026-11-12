# Nodes
- Client (C_id, C, M)
- Merchant (M)
- Trusted Third Party (C)

### Variables
- C: Client's secret token received by TTP, for example a Bank 
- C_id: Client's public ID
- M: Merchant's public ID
- b: Random bitstring chosen by TTP
- B: Random basis string chosen by TTP
- l: Length of bitstring b and basis string B
- P: Encoding of b according to B as a quantum state
- m: MAC(C, M)
- k: result of measuring P according to m

# Protocol steps

1. Client receives secret token C from TTP and merchant id M from Merchant.

2. TTP generates random bitstring b and basis string B, both of length l. TTP encodes j-th element of b in the basis determined by j-th element of B.  

3. TTP sends the encoded quantum state P to client.

4. Client calculates message authentication code m = MAC(C, M) and uses it to measure state P to obtain the result k. 

5. Client sends public id C_id and measurement result k to Merchant

6. Merchant sends {C_id, k, M} to TTP

7. TTP authorizes the transaction iff k_j = b_j when m_j = B_j


Reference: https://arxiv.org/pdf/2305.14504 