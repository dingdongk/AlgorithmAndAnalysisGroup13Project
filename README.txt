1. Project Overview

This project implements a Smart Path Finder system that computes optimal routes between locations in a road network.

The system models a map as a graph:

Nodes represent locations (streets/intersections)
Edges represent roads
Each edge contains:
A fixed distance
A list of 24 time values (one for each hour of the day)

The system supports:

Shortest distance path (Dijkstra / ALT)
Fastest time path (Dijkstra with time-dependent weights)
Avoiding nodes and edges
Dynamic updates of traffic (time list)

2. Environment Setup
Requirements:
Python 3.8 or higher
No external libraries required

3. How to Run the Program
- Clone the repo
- Setup Python enviroment
- Run main.py to use the path finder
- Run benchmark.py to test the speed of each algorithms

4. Advanced features
- Preprocess ALT landmark upon first time loading
- Edit Sample_queries to run benchmark tests
