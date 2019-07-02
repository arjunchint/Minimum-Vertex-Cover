'''This file implements the Approximation Heurestic method to find the minimum vertex cover for a given input graph.

Author: Arjun Chintapalli, Team 25

Instructions: The folder structure is as follows: Project Directory contains   [Code,Data,Output].
Language: Python 3
Executable: python Code/Approx.py  -inst Data/karate.graph -alg Approx -time 600 -seed 1045

The seed value will not be used for the Approximation implementaiton.

The output will be two files: *.sol and *.trace created in the project Output folder
*.sol --- record the size of optimum vertex cover and the nodes in it.
*.trace --- record all the optimum solution found 
            during the search and the time it was found
'''
import networkx as nx
import time
import sys
import random
import math
import os
from os import path
import networkx as nx
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
		return G
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
				trace_output.append((len(temp_G),time.time()-start_time))
				temp_G.remove(VC[i][1])
			i=i+1
		print('Heurestic Solution:' + str(len(VC_sol)))
		return VC_sol, trace_output

# Setup function to initialize graph and run vertex cover and output files
def main(graph_file, output_dir, cutoff, randSeed):

	G = RunExperiments.read_graph(graph_file)
	trace_output=[]
	start_time = time.time() 

	final_VC, trace_output = RunExperiments.initial_solution(G, start_time, cutoff, randSeed, graph_file, trace_output)

	total_time = (time.time() - start_time) 
	print('Huerestic Runtime (s): ' + str(total_time))

	os.makedirs(os.path.dirname(output_dir), exist_ok=True)

	with open(join(os.path.dirname(output_dir), graph_file.split('/')[1].split('.')[0] + '_Approx_600.sol'), 'w') as f:
		f.write(str(int(len(final_VC))) +"\n")
		f.write(','.join([str(x) for x in sorted(final_VC)]))

	with open(join(os.path.dirname(output_dir), graph_file.split('/')[1].split('.')[0] + '_Approx_600.trace'), 'w') as f:
		for t in trace_output:
			f.write('%.2f, %i\n' % ((t[1]),t[0]))

# Parser to run file directly instead of through wrapper		
if __name__ == '__main__':
	#create parser; example: python Code/Approx.py  -inst Data/karate.graph -alg Approx -time 600 -seed 1045
	parser=argparse.ArgumentParser(description='Input parser for Approx')
	parser.add_argument('-inst',action='store',type=str,required=True,help='Inputgraph datafile')
	parser.add_argument('-alg',action='store',default='Approx',type=str,required=False,help='Name of algorithm: Approx')
	parser.add_argument('-time',action='store',default=600,type=float,required=False,help='Cutoff running time for algorithm')
	parser.add_argument('-seed',action='store',default=1000,type=int,required=False,help='Random Seed for algorithm')		
	args=parser.parse_args()

	graph_file = args.inst
	output_dir = 'Output/'
	cutoff = args.time
	randSeed = args.seed

	# run the experiments
	main(graph_file, output_dir, cutoff, randSeed)
