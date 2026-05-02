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
Pickle Library

3. How to Run the Program
- Clone the repo
- Setup Python enviroment
- Run main.py to use the path finder
- Run benchmark.py to test the speed of each algorithms

4. Advanced features
- Preprocess ALT landmark upon first time loading
- Edit Sample_queries to run benchmark tests

5. Demonstration Video Link
https://rmiteduau.sharepoint.com/sites/Alogrithm/_layouts/15/stream.aspx?id=%2Fsites%2FAlogrithm%2FShared%20Documents%2FGeneral%2FRecordings%2FMeeting%20in%20General-20260501_234910-Meeting%20Recording%2Emp4&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0=&ga=1 
