import sys, json, pickle
from socket import *
import os.path
from threading import Timer
#------------------------------------------------------------------
# Global Variables
#------------------------------------------------------------------
nodeId = ""
nodeIP = ""
seq_no = 1
broadcast_no = 1
nodePort = 0
life_time = "infintite"
routingTable = []
neighbours = dict()
routeEntry = []
hop_count = 0
dest_id = ""
dest_seq = -1	
RREQ = []
RREP = []
RERR = []
timer = None
TIMEOUT = 5

#------------------------------------------------------------------
# Functions
#------------------------------------------------------------------
def checkRoutingTable(dest):
	all_dest = [x[0][0] for x in routingTable]
	if (dest in all_dest):
		return True
	return False

def showRoutingTable():
	print "-----------------------------------------------------------------------------------"
	print "|                                Routing Table                                    |"
	print "-----------------------------------------------------------------------------------"
	print "|  Destination  | Next Hop | Hop Count | Life Time | Destination Sequence | Valid |"
	print "-----------------------------------------------------------------------------------"
	for x in xrange(0,len(routingTable)):
		dest = routingTable[x][0][0]
		n_h = routingTable[x][1][0]
		h_c = routingTable[x][2]
		l_t = routingTable[x][3]
		dest_sequence = routingTable[x][4]
		valid = routingTable[x][5]

		row = "|  "+dest+"| ".rjust(15-len(dest))+n_h+"|   ".rjust(13-len(n_h))+str(h_c)+"| ".rjust(10-len(str(h_c)))+l_t+" | ".rjust(10-len(l_t))+"   "+str(dest_sequence)+"| ".rjust(20-len(str(dest_sequence)))+" "+str(valid)+"    |"
		print row
	print "-----------------------------------------------------------------------------------"

def getNodeName(port):
	for x in neighbours.items():
		if (x[1][2] == port):
			return x[1]

def getNextHop(dest):
	for x in routingTable:
		if (x[0][0] == dest):
			return x[1]

def getEntry(dest_id):
	for x in routingTable:
		if (x[0][0] == dest_id):
			return x

def sendRERR(destId, destSeq):
	source = [nodeId, nodeIP, nodePort]
	dest_count = 1
	destSeq = destSeq+1
	RERR = ["RERR", source, dest_count, destId, destSeq]
	#broadcasting RERR to neighbours
	for x in xrange(0,len(neighbours)):
		neighbour_node = neighbours.get(ns[x])
		RERR = json.dumps(RERR)
		sock.sendto(RERR, (neighbour_node[1], neighbour_node[2]))	
		print "[RERR]", nodeId,"->", ns[x]

def neighbour_timeout(neigh_id):
	i = 0
	
	for x in routingTable:
		next_hop_id = x[1][0]
		if (neigh_id == next_hop_id):
			routingTable[i][5] = 0
		i+=1
	entry = getEntry(neigh_id)
	#destination and dest seq no
	sendRERR(neigh_id, entry[4])
	print "Timeout triggered for", neigh_id
	showRoutingTable()

#------------------------------------------------------------------
# Main Program
#------------------------------------------------------------------
if (len(sys.argv) != 4):
	print "usage: python Node.py <node name> <ip addr> <port no>"
	exit(1)

nodeId = sys.argv[1]
nodeIP = sys.argv[2]
nodePort = int(sys.argv[3])

if (nodeId == "gul"):
	neighbours = {"faryal":["faryal","localhost",1338], "ahmed":["ahmed","localhost",1340]}
elif (nodeId == "faryal"):
	neighbours = {"emma":["emma","localhost",1339], "gul":["gul","localhost",1337]}
elif (nodeId == "emma"):
	neighbours = {"dawood":["dawood","localhost",1342], "faryal":["faryal","localhost",1338]}
elif (nodeId == "ahmed"):
	neighbours = {"gul":["gul","localhost",1337], "bilal":["bilal","localhost",1341]}
elif (nodeId == "dawood"):
	neighbours = {"emma":["emma","localhost",1339], "charlie":["charlie","localhost",1343]}
elif (nodeId == "charlie"):
	neighbours = {"dawood":["dawood","localhost",1342], "bilal":["bilal","localhost",1341]}
elif (nodeId == "bilal"):
	neighbours = {"charlie":["charlie","localhost",1343], "ahmed":["ahmed","localhost",1340]}

print "---------------------------"
print nodeId, "=>", nodeIP,":",nodePort
print "---------------------------"

print "-----------------------------------------"
print "Neighbours: ",neighbours.keys()
print "-----------------------------------------"

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((nodeIP, nodePort))

#flag = raw_input("Active(1) or Passive(2): ")
#sending mode
if (nodeId == "gul"):
	flag = "1"
else:
	flag = "2"

routingTableName = "table_"+nodeId+".pickle"
#if routing table files exist
if os.path.isfile(routingTableName):
	#open the serialized file and load it to routingTable
	with open(routingTableName, 'rb') as f:
		routingTable = pickle.load(f)
		#print routingTable

while(1):
	#sending mode
	if (flag == "1"):
		dest_id = "dawood"#raw_input("Name of destination node: ")
		dest_ip = "localhost"#raw_input("IP Address of destination: ")
		dest_port = raw_input("Port No of destination: ")
		#if it has destination route in its own table
		if (checkRoutingTable(dest_id)):
			print "[LOG] I have active route to destination"
			print "[DATA] Sending message..."
			sender = [nodeId, nodeIP, nodePort]
			receiver = dest_id
			message = "["+nodeId+"] Samosay OR Pakoray milen gy...?"
			data = json.dumps(["DATA",sender,receiver,message])
			#print sock.sendto(data, tuple(getNextHop(dest_id)[1:]))
			#sock.settimeout(3)
			# if (sock.sendto(data, tuple(getNextHop(dest_id)[1:])) < 0):
			# 	for entry in xrange(0, len(routingTable)):
			# 		print routingTable[entry][1], getNextHop(dest_id), routingTable[entry][5]
			# 		if (routingTable[entry][1] == getNextHop(dest_id)):
			# 			routingTable[entry][5] = 0

			timer = Timer(TIMEOUT, neighbour_timeout, [getNextHop(dest_id)[0]])
			timer.start()
			sock.sendto(data, tuple(getNextHop(dest_id)[1:]))
			showRoutingTable()
			flag = "2"
		else:
			print "[LOG] I don't have route to destination"
			print "[LOG] Let me discover the route."
			ns = neighbours.keys()
			#broadcasting RREQ to neighbours
			for x in xrange(0,len(neighbours)):
				neighbour_node = neighbours.get(ns[x])
				RREQ = ["RREQ",[nodeId,nodeIP, nodePort],seq_no, broadcast_no, [dest_id, dest_ip, dest_port], dest_seq, 0]
				RREQ = json.dumps(RREQ)
				sock.sendto(RREQ, (neighbour_node[1], neighbour_node[2]))	
				print "[RREQ]", nodeId,"->", ns[x]
				flag = "2"
				
	#receiving mode
	elif (flag == "2"):
		while 1:
			#["RREQ",[src_id, src_ip, src_port], src_seq, src_brdcst, [dest_id, dest_ip, dest_port], dest_seq, hops]
			msg,clientAddr = sock.recvfrom(4096)
			msg = json.loads(msg)
			#updateEntry = False
			#if it is RREQ packet
			showRoutingTable()
			if (msg[0] == "RREQ"):
				#print msg
				print "[RREQ]",nodeId, "<-", getNodeName(clientAddr[1])[0]
				#if originator of RREQ is already in routing table or originator is receiving RREQ back to itself
				if (getEntry(msg[1][0]) is not None or msg[1][0] == nodeId):
					print "[DUP] Discarded RREQ from",  getNodeName(clientAddr[1])[0]
				else:
					if (msg[1][0]!=nodeId):
						#add reverse entry in routing table
						routingTable.append([msg[1], getNodeName(clientAddr[1]), msg[6]+1, life_time,msg[5],1])
						#serialize the routing table
						
						#with open(routingTableName, 'wb') as f:
						#	pickle.dump(routingTable, f)
					
					#if node has destination route in routing table
					if (checkRoutingTable(msg[4][0])):
						print "[LOG] I have active route to destination"
						routeEntry = getEntry(msg[4][0])
						dest_seq = seq_no	#RFC3561: 6.6.2	
						RREP = ["RREP", routeEntry[0], dest_seq, msg[1], routeEntry[2], routeEntry[3]]
						RREP = json.dumps(RREP)
						
						sock.sendto(RREP, tuple(getNextHop(msg[1][0])[1:]))
						print "[RREP]", nodeId, "->", msg[1][0]
						#print "[RREP]",nodeId,"->",getNextHop(msg[1][0])[0]
						#if routing entry has has less hop counts to the destination than new RREQ, ignore RREQ
						#if(getEntry(msg[4][0])[2] < msg[6]):
						#	print "[DUP] Discarded RREQ"
						#else remove the entry from table
						#else:
						#	entry = getEntry(msg[4][0])
						#	routingTable.remove(routingTable.index(entry))
						#	updateEntry = True
					#if routing entry is to be updated
					else:
					#if (not checkRoutingTable(msg[4][0]) or updateEntry):
						#if originator of RREQ is not receiving RREQ back from it's neighbours
						destination = msg[4][0]		#destination_id
						#If RREQ is reached at destination
						if (nodeId == destination):
							print "[LOG] I'm the destination"
							dest_seq = msg[2]+1
							hop_count = 0
							RREP = ["RREP", [nodeId, nodeIP, nodePort], dest_seq, msg[1], hop_count, "infinite"]
							#serialize the RREP list into json
							RREP = json.dumps(RREP)
							#send data to Next_hop that leads to destination
							sock.sendto(RREP, tuple(getNextHop(msg[1][0])[1:]))
							print "[RREP]", nodeId, "->", getNextHop(msg[1][0])[0]
							#print "[RREP]",nodeId,"->",getNextHop(msg[1][0])[0]
						else:
							print "[LOG] I don't have route to destination"
							print "[LOG] Let me discover the route."
							#get node_ids of all neighbours
							ns = neighbours.keys()
							#increment hop count
							msg[6] = msg[6]+1
							#broadcasting RREQ to neighbours
							for x in xrange(0,len(neighbours)):
								#get neighbour node => [node_id, node_ip, node_port]
								neighbour_node = neighbours.get(ns[x])
								#serialize the RREQ list into json
								RREQ = json.dumps(msg)
								#send data to neighbours
								sock.sendto(RREQ, (neighbour_node[1], neighbour_node[2]))	
								print "[RREQ]", nodeId,"->", ns[x]

			#if it is RREP packet
			elif(msg[0] == "RREP"):
				#print msg
				print "[RREP]",nodeId, "<-", getNodeName(clientAddr[1])[0]
				#["RREP", [dest_id,dest_ip,dest_port], dest_seq, [src_id, src_ip, src_port], hop_count, life_time]
				if (checkRoutingTable(msg[1][0])):
					h_count = getEntry(msg[1][0])[2]
					if (h_count > msg[4]+1):
						routingTable.remove(getEntry(msg[1][0]))
						#print [msg[1], getNodeName(clientAddr[1]), msg[4]+1, life_time,msg[2],1]
						routingTable.append([msg[1], getNodeName(clientAddr[1]), msg[4]+1, life_time, msg[2],1])
				else:
					routingTable.append([msg[1], getNodeName(clientAddr[1]), msg[4]+1, life_time, msg[2],1])
				
				#serializing routing table
				#with open(routingTableName, 'wb') as f:
				#	pickle.dump(routingTable, f)
				
				#if RREP is reached at originator of RREQ: means route found.
				if (nodeId == msg[3][0]):
					print "[SUCCESS] Route found"
					print "[DATA] Sending message..."
					sender = [nodeId, nodeIP, nodePort]
					receiver = dest_id
					message = "["+nodeId+"] Samosay OR Pakoray milen gy...?"
					#serialize data list into json
					data = json.dumps(["DATA",sender,receiver,message])
					#send data to Next_hop that leads to destination
					# if (sock.sendto(data, tuple(getNextHop(dest_id)[1:])) < 0):
					# 	for entry in xrange(0, len(routingTable)):
					# 		if (routingTable[entry][1] == getNextHop(dest_id)):
					# 			routingTable[entry][5] = 0
					timer = Timer(TIMEOUT, neighbour_timeout, [getNextHop(dest_id)[0]])
					timer.start()
					sock.sendto(data, tuple(getNextHop(dest_id)[1:]))
					showRoutingTable()
				else:
					#hop count incrementing
					msg[4] = msg[4]+1		
					#serializing msg into json
					RREP = json.dumps(msg)
					#send data to Next_hop that leads to destination
					sock.sendto(RREP, tuple(getNextHop(msg[3][0])[1:]))
					print "[RREP]",nodeId,"->",getNextHop(msg[3][0])[0]
				
			#if it is DATA packet
			#data => ["DATA", [sender_id,sender_ip,sender_port], dest_id, message]
			elif (msg[0] == "DATA"):
				#if data packet is received at destination
				if (msg[2] == nodeId):
					#print msg
					print msg[3]
					source = [nodeId, nodeIP, nodePort]
					destination = msg[1][0]
					message = "["+nodeId+"] Bhool Jao Sim Sim!!"
					#create reply msg and serialize into json
					data = json.dumps(["REPLYDATA",source,destination,message])
					#send data to Next_hop that leads to originator of data msg
					sock.sendto(data, tuple(getNextHop(destination)[1:]))
				#if data packet is received at intermediate node (not at destination)
				else:
					if(checkRoutingTable(msg[2])):
						timer.cancel()
						timer = Timer(TIMEOUT, neighbour_timeout, [getNextHop(msg[2])[0]])
						timer.start()
						#print that forwarding message to next hop
					 	print "[LOG] forwarding message to", getNextHop(msg[2])[0]
					 	#serialize the same msg into jso
					 	data = json.dumps(msg)
					 	#send the same msg to next hop that leads to destination
					 	sock.sendto(data, tuple(getNextHop(msg[2])[1:]))
					else:
					 	sendRERR(msg[2], -1)
					 	
			#if it is REPLYDATA packet
			#[REPLYDATA] => ["REPLYDATA", [source_id,sourceIP, sourcePort], destination_id, message]
			elif (msg[0] == "REPLYDATA"):
				#if packet is received at destination
				destination_id = msg[2]
				if (destination_id == nodeId):
					timer.cancel()
					print msg[3]
				#if packet is at intermediate node, forward it to next hop
				else:
					timer.cancel()
					timer = Timer(TIMEOUT, neighbour_timeout, [getNextHop(destination_id)[0]])
					timer.start()
					print "[LOG] forwarding message to", getNextHop(destination_id)[0]
				 	data = json.dumps(msg)
				 	sock.sendto(data, tuple(getNextHop(destination_id)[1:]))

			#if it is RERR packet
			elif (msg[0] == "RERR"):
				#RERR => ["RERR", [source_id, source_ip, source_port], dest_count, dest_id, dest_seq]
				destination_id = msg[3]
				i = 0
				for x in routingTable:
					next_hop_id = x[1][0]
					if (destination_id == next_hop_id):
						routingTable[i][5] = 0
					i+=1
				#if routingTable doesn't have any entry that has infected next hop
				if (i == 0):
					pass
				else:
					entry = getEntry(destination_id)
					sendRERR(neigh_id, entry[4])	
				#entry = getEntry(neigh_id)
				#destination and dest seq no
				#sendRERR(neigh_id, entry[4])
		showRoutingTable()

	else:
		print "Invalid Input."


