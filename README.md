# AODV_Python_Implementation

Introduction
Ad Hoc distance vector routing protocol is one of the routing protocols in MANET (Mobile Ad hoc network) and is the descendent of the DSDV protocol. 
It does not have a fixed topology in a network and is used for wireless reactive communications of nodes where links are created on demand/as needed. Sequence numbers are used for each need to check if routing tables are up to date. 
Techniques and Methodologies
Our implementation of AODV is done in Python on Linux system. It covers the following functionalities of AODV is specified by the project manual:
  •	Route discovery and path setup using RREQ and RREP messages
    o	Route discovery starts by checking if starting node has that required route to the goal in its routing table. Since initial state of routing table is empty, it will start with route discovery algorithm.
    o	Broadcasting is done via flooding. 
    o	In route discovery, starting node first broadcasts RREQ packet to all of its neighbors. Each packet has:	
      	Source node’s IP address
      	Source node’s current sequence number
      	Destination IP address
      	Destination node’s current sequence number
    o	Each packet is uniquely identified by <Source IP address, Broadcast ID>. This broadcast ID is incremented by the sending node for each RREQ that it sends to avoid duplicate RREQ.  Each node stores this RREQ unique pair of information for all recent requests received.  
                      
  •	Routing table management  (Both forward and reverse routes)
    o	Each node that received that RREQ packet, does a reverse route entry in its route table from source S. This entry stores source IP, current sequence number and hop count from the source node. 
    o	Lifetime of routing table entries is supposed to be infinite. 
    o	Each node that received broadcast packet, unicasts packet to next node. E.g. Gul initiated the RREQ and broadcasts to both Ahmed and Faryal. Ahmed and Faryal then individually forwards the packet to their next nodes, Bilal and Emma respectively. 
    o	If a node finds a route to the goal, it creates the reply packet, RREP. It contains:
      	Destination’s IP address
      	Destination current sequence number
      	Source’s IP address
      	Hop count to destination
    o	This intermediate node then unicasts the RREP directly to the source. A forward route entry is then made into source node containing:
      	Destination
      	Hop count
      	Next hop (the intermediate node)

  •	Maintenance of active route 
  •	Path repair using RERR messages
    o	If a link node breaks/deleted, the route link breaks. This is where path repair is needed. 
    o	Routing tables are updated for the link failures. 
    o	All active neighbors are informed via RRER messages. 
 
Problems faced:
The implementation has a generic code for all nodes and any kind of nodes can be made upon which all main features were implemented. However, few problems were faced:
  •	At initiation, it asks each node to select to be a sender or a receiver node instead of using multithreading. 
  •	Serialization of routing table for persistency. 
  •	Could not implement an improvement to the current AODV protocol system. 
  •	Problems faced in path repair. 
  
Possible Improvements
Upon research and analysis of AODV protocol, we found out that an implementation of AODV with reliable delivery techniques could be used as validated by the research paper - An Improvement of AODV Protocol Based on Reliable Delivery in Mobile Ad hoc Networks by LIU Jian & LI Fang-min (2009 Fifth International Conference on Information Assurance and Security). 
We can use TCP instead UDP to make the delivery of packets reliable.
