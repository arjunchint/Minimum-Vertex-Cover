'''This file implements the Local Search method implementing NumVC to find the minimum vertex cover for a given input graph.

Author: Arjun Chintapalli, Team 25

Instructions: The folder structure is as follows: Project Directory contains [Code,Data,Output]. 

Language: Python 3
Executable: python Code/ls1.py  -inst Data/karate.graph -alg ls1 -time 600 -seed 1045

The seed value will be used for the Local Search implementaiton.

The output will be two files: *.sol and *.trace created in the project Output folder
*.sol --- record the size of optimum vertex cover and the nodes in it.
*.trace --- record all the optimum solution found 
            during the search and the time it was found


This local search implementation iteratively takes an initial solution, removes a node and again iteratively swaps 
			till the solution is a vertex cover again. Performance has been improved by implementing taboo methods (conf_check).             
'''

import networkx as nx
import time
import sys
import random
import math
import os
from os import path
import networkx as nx
from networkx.algorithms.approximation import vertex_cover
import time
import sys
import random
from os import listdir
from os.path import isfile, join
import argparse


class RunExperiments:
	# Read in file to networkx graph structure
	def read_graph(filename):
		G = nx.Graph()
		with open(filename, 'r') as vertices:
			V, E, Temp = vertices.readline().split()
			i=1
			for line in vertices:
				vertex_data = list(map(lambda x: int(x), line.split()))
				for v in vertex_data:
					G.add_edge(i,v)
				i=i+1
		return G, int(V), int(E)


	# Heurestic solution found by iteration from max to min degree nodes and removing node if still vertex cover after
	def initial_solution(G, start_time, cutoff, randSeed, input_file, trace_output):
		temp_G = G.nodes()
		VC = sorted(list(zip(list(G.degree(temp_G).values()), temp_G)))
		VC_sol = temp_G
		i=0
		uncov_edges=[]
		optvc_len = len(VC_sol)
		while(i < len(VC) and (time.time() - start_time) < cutoff):
			flag=True
			for x in G.neighbors(VC[i][1]):
				if x not in temp_G:
					flag = False
			if flag:	
				temp_G.remove(VC[i][1])
			i=i+1
		print('Heurestic Solution:' + str(len(VC_sol)))
		return VC_sol, trace_output		
	
	# Helper method to do steps of adding a vertex: covering uncovered edges, changing taboo state, computing cost function changes
	def addVert(G, VertCover, conf_check, dscores, edge_weights, uncov_edges, add):
		dscores[add] = -dscores[add]
		for x in G.neighbors(add):
			if x not in VertCover:
				uncov_edges.remove((add,x))
				uncov_edges.remove((x,add))
				conf_check[x] = 1
				dscores[x] -= edge_weights[add][x]
			else:
				dscores[x] += edge_weights[add][x]

	# Helper method to do steps of removing a vertex: uncovering covered edges, changing taboo state, computing cost function changes
	def removeVert(G, VertCover, conf_check, dscores, edge_weights, uncov_edges, removed):
		dscores[removed] = -dscores[removed]
		conf_check[removed] = 0
		for x in G.neighbors(removed):
			if x not in VertCover:
				uncov_edges.append((removed,x))
				uncov_edges.append((x,removed))
				conf_check[x] = 1
				dscores[x] += edge_weights[removed][x]
			else:
				dscores[x] -= edge_weights[removed][x]

	# Local Search implementation
	def hillClimb(G, V, E, VertCover, start_time, cutoff, randSeed, input_file, trace_output):
		# Initialization
		random.seed(randSeed)

		threshold = .5*V
		reduction_factor = .3

		edge_weights = nx.convert.to_dict_of_dicts(G, edge_data=1)

		conf_check = [1]*(V+1)
		dscores = [0]*(V+1)
		uncov_edges=[]

		VC_sol = VertCover.copy()
		optvc_len = len(VertCover)
		avg_weight = 0
		delta_weight = 0

		while((time.time() - start_time) < cutoff):	

			# If a vertex cover: remove max cost node		
			while not uncov_edges:
				if (optvc_len > len(VertCover)):
					trace_output.append((optvc_len,time.time()-start_time))					
					VC_sol = VertCover.copy()	
					optvc_len = len(VertCover)
				max_improv = -float('inf')
				for x in VertCover:
					if dscores[x] > max_improv:
						max_improv = dscores[x]
						opt_rem = x
				VertCover.remove(opt_rem)
				RunExperiments.removeVert(G, VertCover, conf_check, dscores, edge_weights, uncov_edges, opt_rem)


			# 1st step of swap is to remove max cost node from solution
			max_improv = -float('inf')
			for x in VertCover:
				if dscores[x] > max_improv:
					max_improv = dscores[x]
					opt_rem = x
			VertCover.remove(opt_rem)
			RunExperiments.removeVert(G, VertCover, conf_check, dscores, edge_weights, uncov_edges, opt_rem)



			# 2nd step of swap is to find node from random uncovered edge to add
			randEdge = random.choice(uncov_edges)
			if conf_check[randEdge[0]] == 0 and randEdge[1] not in VertCover: 
				better_add = randEdge[1]
			elif conf_check[randEdge[1]] == 0 and randEdge[0] not in VertCover:
				better_add = randEdge[0]
			else:
				if dscores[randEdge[0]] > dscores[randEdge[1]]:
					better_add = randEdge[0]
				else:
					better_add = randEdge[1]
			VertCover.append(better_add)
			RunExperiments.addVert(G, VertCover, conf_check, dscores, edge_weights, uncov_edges, better_add)
	
			# Update Edge Weights and score functions
			for x in uncov_edges:
				edge_weights[x[1]][x[0]] += 1				
				dscores[x[0]] += 1
			delta_weight += len(uncov_edges)/2

			# If average edge weights of graph above threshold then partially forget prior weighting decisions
			if delta_weight >= E:
				avg_weight +=1
				delta_weight -= E
			if avg_weight > threshold:
				dscores = [0]*(V+1)
				new_tot =0
				uncov_edges = []
				for x in G.edges():
					edge_weights[x[0]][x[1]] = int(reduction_factor*edge_weights[x[0]][x[1]])
					edge_weights[x[1]][x[0]] = int(reduction_factor*edge_weights[x[1]][x[0]])					
					new_tot += edge_weights[x[0]][x[1]]
					if not (x[0] in VertCover or x[1] in VertCover):
						uncov_edges.append((x[1],x[0]))
						uncov_edges.append((x[0],x[1]))		
						dscores[x[0]] += edge_weights[x[0]][x[1]]
						dscores[x[1]] += edge_weights[x[0]][x[1]]
					elif not (x[0] in VertCover and x[1] in VertCover):
						if x[0] in VertCover:
							dscores[x[0]] -= edge_weights[x[0]][x[1]]
						else:
							dscores[x[1]] -= edge_weights[x[0]][x[1]]
				avg_weight = new_tot/E
			VertCover = sorted(set(VertCover))		


		print('LS Solution for ' + str(input_file) + ' ' + str(len(VC_sol)))
		return VC_sol, trace_output


# Setup function to initialize graph and run vertex cover and output files
def main(graph_file, output_dir, cutoff, randSeed):

	G, V, E = RunExperiments.read_graph(graph_file)

	trace_output=[]
	start_time = time.time() #time in seconds

	initial_VC, trace_output = RunExperiments.initial_solution(G, start_time, cutoff, randSeed, graph_file, trace_output)

	final_VC, trace_output = RunExperiments.hillClimb(G, V, E, initial_VC, start_time, cutoff, randSeed, graph_file, trace_output)

	total_time = (time.time() - start_time) #to convert to milliseconds
	print('LS Runtime (s): ' + str(total_time))

	os.makedirs(os.path.dirname(output_dir), exist_ok=True)

	with open(join(os.path.dirname(output_dir), graph_file.split('/')[1].split('.')[0] + '_LS1_600_' + str(randSeed)+'.sol'), 'w') as f:
		f.write(str(int(len(final_VC))) +"\n")
		f.write(','.join([str(x) for x in sorted(final_VC)]))

	with open(join(os.path.dirname(output_dir), graph_file.split('/')[1].split('.')[0] + '_LS1_600_' + str(randSeed)+'.trace'), 'w') as f:
		for t in trace_output:
			f.write('%.2f, %i\n' % ((t[1]),t[0]))


# Parser to run file directly instead of through wrapper
if __name__ == '__main__':
	#create parser; example: python Code/ls1.py -datafile Data/karate.graph -time 200 -seed 10
	parser=argparse.ArgumentParser(description='Input parser for LS1')
	parser.add_argument('-inst',action='store',type=str,required=True,help='Input graph datafile')
	parser.add_argument('-alg',action='store',default='LS1',type=str,required=False,help='Name of algorithm: LS1')
	parser.add_argument('-time',action='store',default=600,type=float,required=False,help='Cutoff running time for algorithm')
	parser.add_argument('-seed',action='store',default=1000,type=int,required=False,help='Random Seed for algorithm')		
	args=parser.parse_args()

	graph_file = args.inst
	output_dir = 'Output/'
	cutoff = args.time
	randSeed = args.seed

	# run the experiments
	main(graph_file, output_dir, cutoff, randSeed)
