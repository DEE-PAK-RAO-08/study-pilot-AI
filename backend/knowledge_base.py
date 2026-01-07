"""
Study Pilot AI - Extended Knowledge Base
Comprehensive offline knowledge for supported courses.
"""

KNOWLEDGE_BASE = {
    # ==========================================
    # DATA STRUCTURES & ALGORITHMS (DSA)
    # ==========================================
    
    # --- Complexity Analysis ---
    'time complexity': "Time Complexity (Big O) quantifies runtime vs input size (n).\n• O(1): Constant (hash map lookup)\n• O(log n): Logarithmic (binary search)\n• O(n): Linear (iteration)\n• O(n log n): Linearithmic (efficient sorts)\n• O(n²): Quadratic (nested loops)\n• O(2ⁿ): Exponential (recursion)\n• O(n!): Factorial (permutations).",
    'space complexity': "Space Complexity measures memory usage relative to input size. Includes auxiliary space (temp) + input space. Optimization trade-off: O(1) space often requires O(n²) time (e.g., in-place vs merge sort).",
    'amortized analysis': "Amortized Analysis averages the cost of operations over a sequence. Example: Dynamic Array resizing takes O(n) occasionally, but O(1) amortized.",
    'master theorem': "Master Theorem analyzes divide-and-conquer recurrences T(n) = aT(n/b) + f(n). Compares f(n) with n^(log_b a) to determine complexity.",

    # --- Linear Structures ---
    'array': "Arrays: Contiguous memory blocks. O(1) access by index. Fixed size (C/Java) or Dynamic (Python List). Insert/Delete is O(n) due to shifting.",
    'linked list': "Linked List: Nodes with data + pointers. \n• Singly: Next ptr\n• Doubly: Prev + Next\n• Circular: Last->First\nPros: Dynamic size, O(1) insert/delete at known pos. Cons: O(n) access/search, extra pointer memory.",
    'stack': "Stack: LIFO (Last-In First-Out). Ops: Push, Pop, Peek (all O(1)). Uses: Recursion stack, Undo/Redo, Expression parsing (infix->postfix), DFS.",
    'queue': "Queue: FIFO (First-In First-Out). Ops: Enqueue, Dequeue (O(1)). Uses: Job scheduling, BFS, Printer spooling. Variants: Circular Queue, Priority Queue.",
    'hash table': "Hash Table: Key-Value store using hash function. O(1) avg insert/search. Collisions handled by:\n1. Chaining (Linked Lists)\n2. Open Addressing (Probing).",

    # --- Trees & Heaps ---
    'binary tree': "Binary Tree: Node has ≤2 children. Types: Full (0/2 children), Complete (filled left-to-right), Perfect (all leaf same depth).",
    'bst': "Binary Search Tree (BST): Left < Root < Right logic for all nodes. Search/Insert O(log n) if balanced, O(n) if skewed.",
    'avl tree': "AVL Tree: Self-balancing BST. Height diff (balance factor) of left/right subtrees ≤ 1. Uses Rotations (LL, RR, LR, RL) to maintain balance. Guaranteed O(log n).",
    'red black tree': "Red-Black Tree: Self-balancing BST using color bits. Rules ensure longest path ≤ 2 * shortest. Used in Java TreeMap, C++ std::map.",
    'heap': "Heap: Complete Binary Tree. \n• Max-Heap: Parent ≥ Child (Root=Max)\n• Min-Heap: Parent ≤ Child (Root=Min)\nOperations: Insert O(log n), Extract-Root O(log n). Array implementation used for Priority Queues & Heap Sort.",
    'trie': "Trie (Prefix Tree): N-ary tree for strings. Nodes = characters. Efficient for dictionary search, autocomplete. Lookup O(L) where L=word length.",
    'segment tree': "Segment Tree: Used for range queries (sum, min, max) on arrays. Build O(n), Query/Update O(log n).",

    # --- Graphs ---
    'graph': "Graph: Vertices (V) + Edges (E). Types: Weighted/Unweighted, Directed/Undirected, Cyclic/DAG. Storage: Adjacency Matrix (O(V²)), Adjacency List (O(V+E)).",
    'bfs': "BFS (Breadth-First Search): Explores neighbors level-by-level using Queue. O(V+E). Best for: Shortest path in unweighted graphs.",
    'dfs': "DFS (Depth-First Search): Explores deep branches first using Stack/Recursion. O(V+E). Best for: Connectivity, Cycle detection, Topological sort.",
    'dijkstra': "Dijkstra's Algorithm: Finds shortest path from source to all nodes in weighted graph (no negative edges). Uses Min-Priority Queue. O(E log V). Greedy approach.",
    'bellman ford': "Bellman-Ford: Shortest path with negative edges allowed. Relax all edges V-1 times. O(VE). Can detect negative cycles.",
    'prim': "Prim's Algorithm: MST (Minimum Spanning Tree) builder. Grows tree from a node. Uses Priority Queue. O(E log V). Greedy.",
    'kruskal': "Kruskal's Algorithm: MST builder. Sorts edges by weight, adds if no cycle formed (using Union-Find). O(E log E). Greedy.",
    'topological sort': "Topological Sort: Linear ordering of vertices in DAG (Directed Acyclic Graph) where for every edge u->v, u comes before v. Uses DFS or Kahn's Algorithm (in-degree).",

    # --- Sorting ---
    'sorting algorithms': "Sorting overview:\n• O(n²): Bubble, Insertion, Selection (Small data)\n• O(n log n): Merge, Quick, Heap (Large data)\n• O(n): Radix, Counting (Integers/fixed range).",
    'bubble sort': "Bubble Sort: Swaps adjacent wrong-order pairs. O(n²). Adaptive (O(n) if sorted). Stable.",
    'insertion sort': "Insertion Sort: Builds sorted array one item at a time. O(n²). Very fast for small or nearly-sorted data. Stable.",
    'merge sort': "Merge Sort: Divide & Conquer. Split list, recurse, merge sorted halves. O(n log n) always. Stable. Uses O(n) space.",
    'quick sort': "Quick Sort: Partitioning around a Pivot. O(n log n) avg, O(n²) worst. In-place (O(log n) stack). Not stable. Often fastest in practice.",
    'heap sort': "Heap Sort: Build Max-Heap, repeatedly swap root with end & heapify. O(n log n). In-place, Not stable.",
    
    # --- Advanced Concepts ---
    'dynamic programming': "DP: Solves complex problems by breaking into overlapping subproblems + Memoization. Properties: Optimal Substructure. Ex: Knapsack, LCS, Matrix Chain.",
    'greedy': "Greedy Algorithm: Makes locally optimal choice at each step hoping for global optimum. Fast but not always correct. Works for: MST, Huffman Coding.",
    'recursion': "Recursion: Function calls itself. Needs Base Case to stop. Risks Stack Overflow. Tail Recursion can be optimized by compilers.",

    # ==========================================
    # SIGNALS & SYSTEMS
    # ==========================================

    # --- Core Concepts ---
    'signal properties': "Signals: Functions of time/space. Categories:\n• CT/DT: Continuous vs Discrete\n• Periodic/Aperiodic: Repeats every T\n• Causal/Non-causal: Depends on past/future\n• Energy/Power: Finite energy vs finite power.",
    'system properties': "LIT/LTI Systems defined by:\n• Linearity: Superposition (Additivity + Homogeneity)\n• Time-Invariance: Shift input -> Shift output\n• Causality: Output relies only on past/present\n• Stability: BIBO (Bounded Input -> Bounded Output).",
    'impulse response': "Impulse Response h(t): Output system when input is delta function δ(t). For LTI systems, Output y(t) = x(t) * h(t) (Convolution).",
    'convolution': "Convolution: Mathematical operation for LTI response. \nCT: ∫ x(τ)h(t-τ)dτ\nDT: Σ x[k]h[n-k]\nFlip and Slide method. Time multiplication <-> Frequency convolution.",
    
    # --- Transforms ---
    'fourier series': "Fourier Series (FS): Decomposes PERIODIC signals into sum of sines/cosines (harmonics). Used for steady-state analysis.",
    'fourier transform': "Fourier Transform (CTFT): Decomposes APERIODIC signals into continuous frequency spectrum X(ω). Duality: Time compression -> Frequency expansion.",
    'laplace transform': "Laplace Transform: Generalized Fourier for stability analysis. s = σ + jω. Converts differential eq -> algebraic eq. Key: ROC (Region of Convergence) dictates stability (poles in Left Half Plane).",
    'z transform': "Z-Transform: Discrete equivalent of Laplace. z = re^(jω). Converts difference eq -> algebraic eq. Stability: Poles must be inside Unit Circle |z|=1.",
    
    # --- Sampling & Filtering ---
    'sampling theorem': "Nyquist-Shannon: Reconstruct continuous signal exactly if Fs > 2*Fmax. If Fs < 2*Fmax, Aliasing (overlap) occurs.",
    'filter types': "Filters modify spectrum:\n• Low Pass (LPF): Allow low freq\n• High Pass (HPF): Allow high freq\n• Band Pass (BPF): Allow range\n• Band Stop (Notch): Block range.",
    'bode plot': "Bode Plot: Logarithmic plot of Transfer Function H(s). Needs Magnitude (dB vs log ω) and Phase (degrees vs log ω) plots. Margins determine stability.",

    # ==========================================
    # THERMODYNAMICS
    # ==========================================

    # --- Laws ---
    'zeroth law': "0th Law: Thermal Equilibrium. If Ta=Tb and Tb=Tc, then Ta=Tc. Defines Temperature concept.",
    'first law': "1st Law: Conservation of Energy. Q = ΔU + W (Heat added = Internal Energy change + Work done). Energy cannot be created/destroyed.",
    'second law': "2nd Law: Entropy (S) of isolated system never decreases. Heat flows Hot->Cold spontaneously. No engine is 100% efficient (Kelvin-Planck/Clausius).",
    'third law': "3rd Law: Entropy approaches constant minimum (zero for perfect crystal) at Absolute Zero (0 Kelvin). Implies 0K is unreachable.",

    # --- Properties & Processes ---
    'thermodynamic properties': "• Intensive: Independent of mass (P, T, density)\n• Extensive: Dependent on mass (V, U, H, S)\n• Path Functions: Q, W (depend on process)\n• State Functions: P, V, T, U, H, S (depend on end states).",
    'processes': "• Isobaric: Const P (W = PΔV)\n• Isochoric: Const V (W = 0)\n• Isothermal: Const T (ΔU=0 for ideal gas)\n• Adiabatic: No Heat (Q=0, PV^γ = C).",
    'gas laws': "Ideal Gas Law: PV = nRT.\nAssumes point particles, elastic collisions, no intermolecular forces. Valid at low P, high T. Van der Waals equation corrects for real gases.",
    'entropy': "Entropy (S): Measure of disorder or energy unavailability. dS = dQ_rev/T. Always increases in irreversible processes.",
    'enthalpy': "Enthalpy (H): H = U + PV. Heat content at constant pressure. ΔH is heat of reaction/transformation.",

    # --- Power Cycles ---
    'carnot cycle': "Carnot Cycle: Theoretical max efficiency. 2 Isotherms + 2 Adiabats. Efficiency η = 1 - T_cold/T_hot. Independent of working substance.",
    'otto cycle': "Otto Cycle: Petrol/Spark-Ignition engine. 2 Isochoric + 2 Adiabatic. Efficiency depends on compression ratio r.",
    'diesel cycle': "Diesel Cycle: Compression-Ignition. Constant Pressure heat addition (Isobaric) + Constant Volume rejection.",
    'rankine cycle': "Rankine Cycle: Steam power plants. Pump -> Boiler (Isobaric Heat In) -> Turbine (Work Out) -> Condenser (Isobaric Heat Out). Phase change involved.",
    'brayton cycle': "Brayton Cycle: Gas Turbines/Jet Engines. 2 Isobaric + 2 Adiabatic processes.",

    # ==========================================
    # DIGITAL SIGNAL PROCESSING (DSP)
    # ==========================================

    'discrete concepts': "• Sampling: CT -> DT (Time discretization)\n• Quantization: Continuous Val -> Discrete Val (Amplitude discretization, adds 'Quantization Noise').",
    'dft': "DFT (Discrete Fourier Transform): Frequency analysis for finite DT signals. Complexity O(N²). Basis for digital spectral analysis.",
    'fft': "FFT (Fast Fourier Transform): Efficient algorithm (Cooley-Tukey) to compute DFT. Complexity O(N log N). Revolutionized DSP.",
    'convolution types': "• Linear Convolution: Standard system output.\n• Circular Convolution: Periodic result from DFT multiplication. \nTo evaluate Linear using FFT, zero-pad signals to length L+M-1.",
    'fir filter': "FIR (Finite Impulse Response): No feedback. Always stable. Can have Linear Phase. requires higher order (more taps) for sharp cutoff. Design: Windowing, Parks-McClellan.",
    'iir filter': "IIR (Infinite Impulse Response): Uses feedback. Matches analog filter characteristics (Butterworth, Chebyshev). Efficient (lower order) but phase is non-linear and can be Unstable.",
    'windowing': "Windows: Reduce spectral leakage in DFT of finite signal. \n• Rectangular: Narrow main lobe, high side lobes (leakage)\n• Hamming/Hanning: Wider main lobe, lower side lobes (better).",
    'z transform roc': "ROC (Region of Convergence) for Z-transform:\n• Causal: |z| > r\n• Anti-causal: |z| < r\n• Stable: Unit circle (|z|=1) included in ROC.",

    # ==========================================
    # COMPUTER SCIENCE FOUNDATIONS
    # ==========================================
    
    'operating system': "OS: Interface between hardware/user. Functions: Process Mgmt, Memory Mgmt, File Systems, I/O. Kernel is core.",
    'process vs thread': "• Process: Program in execution. Isolated memory. Heavyweight.\n• Thread: LWP within process. Shared memory space. Lightweight context switch.",
    'deadlock': "Deadlock: 4 conditions (Coffman): Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait. Prevention: Break one condition.",
    'osi model': "OSI Layers (7): Physical -> Data Link -> Network (IP) -> Transport (TCP/UDP) -> Session -> Presentation -> Application (HTTP).",
    'tcp vs udp': "• TCP: Connection-oriented, Reliable, Ordered, Slower (Handshakes, ACKs). Web/Email.\n• UDP: Connectionless, Unreliable, Unordered, Faster. Streaming/Gaming.",
    'database': "DBMS: SQL (Relational, ACID, Tables) vs NoSQL (Document, Key-Value, CAP Theorem). Normalization reduces redundancy.",
    'oop': "OOP Pillars:\n1. Encapsulation (Data hiding)\n2. Inheritance (Reusability)\n3. Polymorphism (Overloading/Overriding)\n4. Abstraction (Interface/Abstract Class)."
}

def get_smart_answer(query: str) -> dict:
    """
    Enhanced search with fuzzy matching and keyword scoring.
    """
    query_lower = query.lower()
    
    # Direct match check
    if query_lower in KNOWLEDGE_BASE:
        return _format_answer(query_lower, KNOWLEDGE_BASE[query_lower])
        
    # Keyword scoring approach
    best_key = None
    best_score = 0
    words = query_lower.split()
    
    for topic, content in KNOWLEDGE_BASE.items():
        topic_words = topic.split()
        
        # Calculate match score
        score = 0
        
        # Full phrase match gets huge bonus
        if topic in query_lower:
            score += 50
            
        # Partial phrase match
        for word in words:
            if len(word) > 3 and word in topic: # Skip small words
                score += 10
                
        # Update best match if threshold met
        if score > best_score and score > 15:
            best_score = score
            best_key = topic
            
    if best_key:
        return _format_answer(best_key, KNOWLEDGE_BASE[best_key])
        
    return None

def _format_answer(topic: str, content: str) -> dict:
    return {
        'answer': content,
        'citations': [{
            'index': 1,
            'citation': f'Study Pilot Knowledge Base: {topic.title()}',
            'score': 1.0
        }],
        'confidence': 0.95,
        'sources': ['Study Pilot AI Core Knowledge']
    }
