
Instructions for Branch and Bound Implementation
Language: Python 3
Filename: BnB.py
Team: 25
Author: Sangy Hanuamsagar (shanumasagar3, gtid: 902825462)

Execution: To run BnB.py, by itself, it be accessed using the following executable from command line after ensuring the folder structure described below: python Code/BnB.py -inst Data/karate.graph -alg BnB -time 600 -seed 100 

Folder Structure: The project root directory must contain the folders: Code, Data, OutputThe file must be located in folder 'Code' in project root directory. 


"""The algorithm is summarized as follows:

Every vertex is considered as having one of two states: 1 or 0
State 1---> Vertex is a part of Vertex Cover (VC) 
State 0---> Vertex is not a part of Vertex Cover (VC) whihc means all its neighbors HAVE to be in VC

Frontier Set: contains the set of candiadate vertices for a subproblem. Each entry is a tuple list comprising of (vertex ID, state, parent in searching tree) 

CurG: subproblem of current graph after removing explored nodes 
CurVC: Current VC found in particular instance of search
OptVC: Best (i.e. minimum) value of |CurVC| at any given point form start

Bounds to Solutions:
Upper Bound: Initially set to number of nodes and updated to size of current solution (i.e. size of minimum vertex cover found in search)

Lower bound: |Current VC| + LB(CurG)
LB(CurG)=sum of edges in CurG / maximum node degree in CurG

Stages of Implementation:
1) Choose candidate node (vi)
	Each search is started from the node with highest degree in CurG, as it represents the most promising node to be included in the VC. This node is stored in the last index of Frontier set, and accessed using Frontier.pop().

	Appened (vi,1) and (vi,0) to CurVC as a tuple= (vertex,state)


2)  If State==1: Remove from CurG 
	This removes the node and its edges from CurG
	
	If state==0, Add all neighbors of vi to CurVC and remove vi from CurG

3) Consider CurG
	If No more edges in CurG-->Candidate solution is found (CurVC accounts for all edges). 
		Check to see if |CurVC| lesser than |OptVC| (and update OptVC if true, otherwise backtrack to find new path) 
	Else Update Lower bound and prune as necessary.
		If Lowerbound<Upperbound, solution is possible
			Append next highest degree node in CurG to Frontier set 
		Else, there is no better solution in this search sapce, so can be pruned from CurG. Backtrack to find new path.

4) Backtracking
	After reaching the end of a path, we need to backtrack to consider a new path. To do this, we have to undo the changes made to CurG and CurVC, which is where the parent item of each tuple in Frontier is handy.
	
	If the parent node is in the VC, then 
		we remove the last few elements from CurVC that were added after teh parent node was discovered and add the corresponing nodes+edges back to CurG. This basically 'undoes the mistakes' to CurG...
	Else then the parent must be (-1,-1) i.e. start of the graph or root node
		Reset CurG to G and CurVC to empty 

When Frontier Set==empty, the whole graph and all possible solutions have been examined.G

End