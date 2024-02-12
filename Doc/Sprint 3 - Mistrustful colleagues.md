### Goal
Analyze and solve the edge case "Mistrustful colleagues"

### Requirements
[[Nebula security domains#Requisiti|requirements' link]]

### Problem analysis
##### The problem - Mistrustful colleagues
We slightly modify the previous case by adding the requirement that laptops cannot connect to each other. 
In this case removing "laptopSD" would not be sufficient, laptop1 and laptop2 would still be able to communicate by both being part of "serverAccessSD".

The way we have defined SecDoms so far we would be forced to define a SecDom for each laptop that wants to connect with the server in which only the server and the laptop itself are present.

The solution is not only not convenient to define but would be extremely unscalable and unmaintainable.

Therefore, we need to extend the system by introducing a new concept: **Roles**.
I define three possible roles into which a host can fall: **SenderOnly**, **ReceiverOnly**, **Both**.
##### How are roles implemented?
Roles can be implemented in nebula in the following ways:
- Sender only: block the receiving from the SubDom even though it's part of it, just don't implement the inbound allow rule
- Receiver only: should allow to send to everything excluded a specific group, to do that i would need to manually define a rule to let out the connection for every group that this host is part of and it's at least a sender plus the lighthouse (NOTE: this node will not talk to anyone that is not in a SecDom unless manually configured to do so...)
- Both: as defined in the previous sprint
##### Redefining outbound rules
Being a ReceiverOnly host in a SecDom means changing completely the way outbound rules are defined, changing from a default allow to a default deny + other rules.
To implement this there are two options:
1) Identify ReceiverOnly in advance and treat them differently
2) Change the way outbound rules are defined for all the hosts
In this sprint we will follow the second option. Implementing roles is just an idea and could very well be discarded in the future so there is no reason to make development too complicated.

### Test
[[Vagrant/vagrant_esempio3_nebula/Vagrantfile|Vagrantfile]]
In this second case we will have 6 machines including 3 laptops, 2 servers in a SecDom, and the lighthouse. The three laptops must be able to connect with one of the servers but should not be able to connect to each other.
For a more complete example we will define server1 as a "ReceiverOnly" node and all the laptops as "SenderOnly" nodes.

### Design
The configuration file ([[NebulaAppV3/securityDomains.json|securityDomains]]) changes as follows:
```
[
    {
        "name": "serverSD",
        "hosts": [
            {
                "name": "server1",
                "role": ""
            },
            {
                "name": "server2",
                "role": ""
            }
        ]
    },
    
    {
        "name": "serverAccessSD",
        "hosts": [
            {
                "name": "server1",
                "role": "receiver"
            },
            {
                "name": "laptop1",
                "role": "sender"
            },
            {
                "name": "laptop2",
                "role": "sender"
            },
            {
                "name": "laptop3",
                "role": "sender"
            }
        ]
    }
]
```

