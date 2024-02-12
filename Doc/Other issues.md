Some nebula problem that fall outside the scope of the project are collected in here.
##### Security issues?
Is there a way to inject modification or other forms of attacks?
- Can I assume that the file transfer channel is secure?
- I can definitely modify the file in a node manually, should be saved in /etc folder to require at least sudo permission.
##### Interesting possible flaw in security
Nebula's initial handshake includes the certificate of the peer initiating the connection, and that initial handshake packet is unencrypted. To encrypt the initial handshake packet would require more round trips per handshake, or a pre-shared key, neither of which Nebula supports today.

##### Problems with lighthouse as relay
nebula traffic is peer-to-peer encrypted, and relays don't interfere with that. So, no relay can sniff plaintext packets.

Nebula's designed to drop untrusted traffic as quickly / efficiently as possible, so running a lighthouse as a relay doesn't add any extra DoS security risk there.

In small networks, lighthouse as relay is what I would do  
in large networks, I would deploy dedicated relays close (in terms of network hops/capacity) to the peers the relay is serving, and I would not use the lighthouse as a relay.
