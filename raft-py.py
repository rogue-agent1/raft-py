#!/usr/bin/env python3
"""Simplified Raft consensus protocol simulation."""
import sys,random
from enum import Enum

class Role(Enum):FOLLOWER=0;CANDIDATE=1;LEADER=2

class Node:
    def __init__(self,nid,peers):
        self.id=nid;self.peers=peers;self.role=Role.FOLLOWER
        self.term=0;self.voted_for=None;self.log=[];self.commit_idx=-1
        self.votes=set();self.leader=None
    def request_vote(self,candidate_term,candidate_id):
        if candidate_term>self.term:
            self.term=candidate_term;self.role=Role.FOLLOWER;self.voted_for=None
        if candidate_term>=self.term and self.voted_for in(None,candidate_id):
            self.voted_for=candidate_id;return True
        return False
    def start_election(self):
        self.term+=1;self.role=Role.CANDIDATE;self.voted_for=self.id;self.votes={self.id}
    def become_leader(self):self.role=Role.LEADER;self.leader=self.id
    def append_entry(self,entry):
        if self.role==Role.LEADER:self.log.append((self.term,entry));return True
        return False
    def replicate(self,term,entry):
        if term>=self.term:self.log.append((term,entry));self.term=term;return True
        return False

def simulate(n=5,seed=42):
    rng=random.Random(seed)
    nodes=[Node(i,list(range(n))) for i in range(n)]
    # Election: node 0 starts
    nodes[0].start_election()
    for i in range(1,n):
        if nodes[i].request_vote(nodes[0].term,0):nodes[0].votes.add(i)
    if len(nodes[0].votes)>n//2:
        nodes[0].become_leader()
        for node in nodes:node.leader=0
    return nodes

def main():
    if len(sys.argv)>1 and sys.argv[1]=="--test":
        nodes=simulate(5)
        assert nodes[0].role==Role.LEADER
        assert len(nodes[0].votes)>=3
        assert all(n.leader==0 for n in nodes)
        # Append + replicate
        assert nodes[0].append_entry("x=1")
        for i in range(1,5):assert nodes[i].replicate(nodes[0].term,"x=1")
        assert all(len(n.log)==1 for n in nodes)
        # New election with higher term
        nodes[2].start_election()
        votes=1
        for i in [1,3,4]:
            if nodes[i].request_vote(nodes[2].term,2):votes+=1
        assert votes>=3  # wins
        print("All tests passed!")
    else:
        nodes=simulate();print(f"Leader: node {nodes[0].id}, term {nodes[0].term}")
if __name__=="__main__":main()
