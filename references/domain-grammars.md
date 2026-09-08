# Domain Visual Grammars

Choose the smallest grammar that makes the important relationships visible. Combine grammars only when the subject actually combines them.

## Code execution

Model:

- functions or modules as machines with typed ports;
- calls as directed control edges;
- arguments and return values as data edges distinct from call edges;
- stack frames as nested or time-bounded enclosures;
- branches as gates with mutually exclusive activation;
- loops as directional return paths with an iteration counter;
- async tasks as parallel lanes with explicit join or cancellation points;
- mutation as a visible before/after state change.

Do not confuse lexical containment with runtime calling. Do not animate a return value along the call edge unless direction is visibly reversed.

## Software and distributed architecture

Model:

- services as bounded components with public ports;
- synchronous request/response as paired directional edges;
- queues as owned buffers with enqueue and dequeue sides;
- databases as state stores with distinct reads and writes;
- replicas as repeated instances, not one enlarged service;
- load balancers as routers, not splitters;
- retries, timeouts, and circuit breakers as stateful control paths;
- trust, network, or deployment boundaries as enclosures rather than data pipes.

Use actual protocols, schemas, ownership, and cardinalities when known. Latency or throughput should only control length, speed, or lane count when a declared scale exists.

## Agent architecture

Model:

- user intent and task state separately;
- planner, executor, critic, router, memory, tools, and policies as distinct roles only when the real system has them;
- messages as typed events with sender, receiver, and payload;
- tool calls as request/result pairs;
- short-term context, durable memory, and external state as different stores;
- delegation as creation of a child task with explicit ownership and completion return;
- approval gates as blocked control transitions, not ordinary data nodes;
- retries and reflection as bounded feedback loops with stopping conditions.

Avoid anthropomorphic motion that implies capabilities, autonomy, memory, or communication the agent does not possess.

## Mathematical and tensor pipelines

Model:

- axes before values: identify batch, sequence, feature, head, channel, spatial, or time axes;
- shape-preserving operators as gates that retain cross-section;
- partitioning along an axis as exact lane subdivision;
- branching as two full copies feeding parallel operators, not a doubled output dimension;
- concatenation as ordered physical adjacency along the named axis;
- elementwise operations as aligned lane-to-lane combination;
- reductions as disappearance of a named axis;
- broadcast as one axis being reused across compatible positions;
- dense transforms as global mixing chambers;
- sparse or grouped transforms as visible restricted connectivity;
- masks as unavailable cells or edges, not deleted inputs;
- cache as stored historical state, separate from current computation.

Example: for `SiLU(g) ⊙ u`, show two equal-shape branches, apply SiLU only at the end of the gate branch, combine corresponding channels, retain that shape, then apply the down projection. Never show the two branches as concatenated unless the formula concatenates them.

## Algorithms and state machines

Model:

- states as stable regions;
- transitions as labeled directed edges;
- guards at the transition boundary;
- events as triggers distinct from payload;
- mutable collections as containers whose contents visibly change;
- invariants as persistent rails, boundaries, or badges;
- search frontier, visited set, and current node as different visual roles;
- complexity metrics only through labeled scales.

Do not animate impossible transitions for visual continuity.

## Hybrid subjects

For a model that combines domains, establish a dominant grammar and use secondary grammar inside bounded components. For example, show a distributed agent system as a service topology, then use an agent workflow grammar only inside the agent-service enclosure.
