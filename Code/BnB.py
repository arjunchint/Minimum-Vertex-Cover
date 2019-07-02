'''This file implements the Branch and Bound method to find minimum vertex cover for a given input graph.

Author: Sangy Hanuamsagar, Team 25

Instructions: The folder structure is as follows: Project Directory contains   [Code,Data,Output]. The code files must be pasted in Code folder.

Language: Python 3
Executable: python Code/BnB.py -inst Data/karate.graph -alg BnB -time 600 -seed 100 
The seed value will not be used for the BnB implementaiton.

The output will be two files: *.sol and *.trace created in the project Output folder
*.sol --- record the size of optimum vertex cover and the nodes in it.
*.trace --- record all the optimum solution found 
            during the search and the time it was found
'''

import argparse
import networkx as nx
import operator
import time
import os

# FUNCTION FOR PARSING INPUT FILES
def parse(datafile):
	adj_list = []
	with open(datafile) as f:
		num_vertices, num_edges, weighted = map(int, f.readline().split())
		for i in range(num_vertices):
			adj_list.append(map(int, f.readline().split()))
	return adj_list

# USE THE ADJACENCY LIST TO CREATE A GRAPH
def create_graph(adj_list):
	G = nx.Graph()
	for i in range(len(adj_list)):
		for j in adj_list[i]:
			G.add_edge(i + 1, j)
	return G

# BRANCH AND BOUND FUNCTION to find minimum VC of a graph
def BnB(G, T):
	#RECORD START TIME
	start_time=time.time()
	end_time=start_time
	delta_time=end_time-start_time
	times=[]    #list of times when solution is found, tuple=(VC size,delta_time)

	# INITIALIZE SOLUTION VC SETS AND FRONTIER SET TO EMPTY SET
	OptVC = []
	CurVC = []
	Frontier = []
	neighbor = []

	# ESTABLISH INITIAL UPPER BOUND
	UpperBound = G.number_of_nodes()
	print('Initial UpperBound:', UpperBound)

	CurG = G.copy()  # make a copy of G
	# sort dictionary of degree of nodes to find node with highest degree
	v = find_maxdeg(CurG)

	# APPEND (V,1,(parent,state)) and (V,0,(parent,state)) TO FRONTIER
	Frontier.append((v[0], 0, (-1, -1)))  # tuples of node,state,(parent vertex,parent vertex state)
	Frontier.append((v[0], 1, (-1, -1)))


	while Frontier!=[] and delta_time<T:
		(vi,state,parent)=Frontier.pop() #set current node to last element in Frontier
		
		backtrack = False
	
		if state == 0:  # if vi is not selected, state of all neighbors=1
			neighbor = CurG.neighbors(vi)  # store all neighbors of vi
			for node in list(neighbor):
				CurVC.append((node, 1))
				CurG.remove_node(node)  # node is in VC, remove neighbors from CurG
		elif state == 1:  # if vi is selected, state of all neighbors=0
			CurG.remove_node(vi)  # vi is in VC,remove node from G
		else:
			pass

		CurVC.append((vi, state))
		CurVC_size = VC_Size(CurVC)

		if CurG.number_of_edges() == 0:  # end of exploring, solution found

			if CurVC_size < UpperBound:
				OptVC = CurVC.copy()
				print('Current Opt VC size', CurVC_size)
				UpperBound = CurVC_size
				times.append((CurVC_size,time.time()-start_time))
			backtrack = True
				
		else:   #partial solution
			CurLB = Lowerbound(CurG) + CurVC_size

			if CurLB < UpperBound:  # worth exploring
				vj = find_maxdeg(CurG)
				Frontier.append((vj[0], 0, (vi, state)))#(vi,state) is parent of vj
				Frontier.append((vj[0], 1, (vi, state)))
			else:
				# end of path, will result in worse solution,backtrack to parent
				backtrack=True

		if backtrack==True:
			if Frontier != []:	#otherwise no more candidates to process
				nextnode_parent = Frontier[-1][2]	#parent of last element in Frontier (tuple of (vertex,state))

				# backtrack to the level of nextnode_parent
				if nextnode_parent in CurVC:
					
					id = CurVC.index(nextnode_parent) + 1
					while id < len(CurVC):	#undo changes from end of CurVC back up to parent node
						mynode, mystate = CurVC.pop()	#undo the addition to CurVC
						CurG.add_node(mynode)	#undo the deletion from CurG
						
						# find all the edges connected to vi in Graph G
						# or the edges that connected to the nodes that not in current VC set.
						
						curVC_nodes = list(map(lambda t:t[0], CurVC))
						for nd in G.neighbors(mynode):
							if (nd in CurG.nodes()) and (nd not in curVC_nodes):
								CurG.add_edge(nd, mynode)	#this adds edges of vi back to CurG that were possibly deleted

				elif nextnode_parent == (-1, -1):
					# backtrack to the root node
					CurVC.clear()
					CurG = G.copy()
				else:
					print('error in backtracking step')

		end_time=time.time()
		delta_time=end_time-start_time
		if delta_time>T:
			print('Cutoff time reached')

	return OptVC,times

#TO FIND THE VERTEX WITH MAXIMUM DEGREE IN REMAINING GRAPH
def find_maxdeg(g):
	deglist = g.degree()
	deglist_sorted = sorted(deglist.items(), reverse=True, key=operator.itemgetter(
		1))  # sort in descending order of node degree
	v = deglist_sorted[0]  # tuple - (node,degree)
	return v

#EXTIMATE LOWERBOUND
def Lowerbound(graph):
	lb=graph.number_of_edges() / find_maxdeg(graph)[1]
	lb=ceil(lb)
	return lb


def ceil(d):
    #return the minimum integer that is bigger than d 
    if d > int(d):
        return int(d) + 1
    else:
        return int(d)
    

#CALCULATE SIZE OF VERTEX COVER (NUMBER OF NODES WITH STATE=1)
def VC_Size(VC):
	# VC is a tuple list, where each tuple = (node_ID, state, (node_ID, state)) vc_size is the number of nodes which has state == 1

	vc_size = 0
	for element in VC:
		vc_size = vc_size + element[1]
	return vc_size

##################################################################
# MAIN BODY OF CODE

def main(inputfile, output_dir, cutoff, randSeed):
	#READ INPUT FILE INTO GRAPH
	adj_list = parse(inputfile)	
	g = create_graph(adj_list)

	Sol_VC,times = BnB(g, cutoff)

	#DELETE FALSE NODES (STATE=0) IN OBTAINED SoL_VC
	for element in Sol_VC:
		if element[1]==0:
			Sol_VC.remove(element)

	# WRITE SOLUTION AND TRACE FILES TO "*.SOL" AND '*.TRACE"  RESPECTIVELY
	inputdir, inputfile = os.path.split(inputfile)

	#WRITE SOL FILES
	with open('.\Output\\' + inputfile.split('.')[0] + '_BnB_'+str(cutoff)+'.sol', 'w') as f:
	    f.write('%i\n' % (len(Sol_VC)))
	    f.write(','.join([str(x[0]) for x in Sol_VC]))


	#WRITE TRACE FILES
	with open('.\Output\\' + inputfile.split('.')[0] + '_BnB_'+str(cutoff)+'.trace', 'w') as f:
	    for t in times:
	        f.write('%.2f,%i\n' % ((t[1]),t[0]))

if __name__ == '__main__':
	parser=argparse.ArgumentParser(description='Input parser for BnB')
	parser.add_argument('-inst',action='store',type=str,required=True,help='Inputgraph datafile')
	parser.add_argument('-alg',action='store',default=1000,type=str,required=True,help='Name of algorithm')
	parser.add_argument('-time',action='store',default=1000,type=int,required=True,help='Cutoff running time for algorithm')
	parser.add_argument('-seed',action='store',default=1000,type=int,required=False,help='random seed')
	args=parser.parse_args()

	algorithm = args.alg
	graph_file = args.inst
	output_dir = 'Output/'
	cutoff = args.time
	randSeed = args.seed
	main(graph_file, output_dir, cutoff, randSeed)