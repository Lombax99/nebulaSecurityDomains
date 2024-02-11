##### Security issues?
Is there a way to inject modification or other forms of attacks?
- Posso dare per scontato che il canale di trasferimento dei file sia sicuro?
- Posso sicuramente modificiare il file in un nodo manualmente...
- [x] domani provo a chiede al prof

##### Problems with lighthouse as relay
*nebula traffic is peer-to-peer encrypted, and relays don't interfere with that. So, no relay can sniff plaintext packets.*

*Nebula's designed to drop untrusted traffic as quickly / efficiently as possible, so running a lighthouse as a relay doesn't add any extra DoS security risk there*

*in small networks, lighthouse as relay is what I would do  
in large networks, I would deploy dedicated relays close (in terms of network hops/capacity) to the peers the relay is serving, and I would not use the lighthouse as a relay*
##### Interesting possible flaw in security
*Nebula's initial handshake includes the certificate of the peer initiating the connection, and that initial handshake packet is unencrypted. To encrypt the initial handshake packet would require more round trips per handshake, or a pre-shared key, neither of which Nebula supports today.*