import { useState, useEffect, useRef } from 'react';
import './AskPage.css';

// ============================================================================
// LOCAL AI KNOWLEDGE BASE - Works completely offline as MVP
// ============================================================================
const knowledgeBase = {
    // Data Structures
    'binary search tree': {
        answer: `A **Binary Search Tree (BST)** is a hierarchical data structure where each node has at most two children, with a special ordering property:

**Key Properties:**
• Left subtree contains nodes with keys **less than** the parent
• Right subtree contains nodes with keys **greater than** the parent
• Both subtrees are also BSTs (recursive property)

**Time Complexities:**
• Search: O(log n) average, O(n) worst case
• Insert: O(log n) average, O(n) worst case
• Delete: O(log n) average, O(n) worst case

**Example Structure:**
\`\`\`
       8
      / \\
     3   10
    / \\    \\
   1   6    14
\`\`\`

**Common Operations:**
• **Inorder traversal** gives sorted sequence
• **Search** - compare with root, go left if smaller, right if larger
• **Insert** - find correct position maintaining BST property`,
        confidence: 0.95,
        topic: 'Data Structures'
    },
    'quick sort': {
        answer: `**Quick Sort** is a highly efficient, divide-and-conquer sorting algorithm invented by Tony Hoare.

**How it works:**
1. **Choose a pivot** element from the array
2. **Partition**: Rearrange elements so smaller ones are left of pivot, larger ones are right
3. **Recursively** apply to left and right subarrays

**Time Complexity:**
• Best/Average: **O(n log n)**
• Worst case: **O(n²)** (when array is already sorted with bad pivot choice)

**Space Complexity:** O(log n) for the recursive call stack

**Code Example (Pseudocode):**
\`\`\`
function quickSort(arr, low, high):
    if low < high:
        pivotIndex = partition(arr, low, high)
        quickSort(arr, low, pivotIndex - 1)
        quickSort(arr, pivotIndex + 1, high)
\`\`\`

**Why it's popular:**
• Very fast in practice
• In-place sorting (low memory usage)
• Cache-friendly`,
        confidence: 0.94,
        topic: 'Algorithms'
    },
    'merge sort': {
        answer: `**Merge Sort** is a stable, divide-and-conquer sorting algorithm with guaranteed O(n log n) performance.

**Algorithm Steps:**
1. **Divide** the array into two halves
2. **Recursively** sort each half
3. **Merge** the sorted halves back together

**Time Complexity:** Always **O(n log n)** - consistent performance!

**Space Complexity:** O(n) - requires additional memory

**Key Advantages:**
• Guaranteed O(n log n) even in worst case
• Stable sort (preserves relative order of equal elements)
• Great for linked lists and external sorting

**Merge Process:**
\`\`\`
[3,7,2,5] → Split → [3,7] and [2,5]
[3,7] → Split → [3] and [7] → Merge → [3,7]
[2,5] → Split → [2] and [5] → Merge → [2,5]
[3,7] + [2,5] → Merge → [2,3,5,7]
\`\`\``,
        confidence: 0.93,
        topic: 'Algorithms'
    },
    'linked list': {
        answer: `A **Linked List** is a linear data structure where elements are stored in nodes, with each node pointing to the next.

**Types:**
• **Singly Linked List** - nodes point only forward
• **Doubly Linked List** - nodes point forward and backward
• **Circular Linked List** - last node points to first

**Structure:**
\`\`\`
[Data|Next] → [Data|Next] → [Data|Next] → NULL
   Head                          Tail
\`\`\`

**Time Complexities:**
• Access: O(n)
• Search: O(n)
• Insert at head: **O(1)**
• Insert at tail: O(n) or O(1) with tail pointer
• Delete: O(n)

**Advantages over Arrays:**
• Dynamic size - grows/shrinks easily
• Efficient insertion/deletion at known positions
• No memory waste from pre-allocation

**Disadvantages:**
• No random access (must traverse)
• Extra memory for pointers`,
        confidence: 0.92,
        topic: 'Data Structures'
    },
    'hash table': {
        answer: `A **Hash Table** (or Hash Map) is a data structure that maps keys to values using a hash function for ultra-fast lookups.

**How it works:**
1. **Hash Function** converts key → index
2. Store value at that index
3. Handle collisions when different keys hash to same index

**Time Complexity (Average):**
• Insert: **O(1)**
• Search: **O(1)**
• Delete: **O(1)**

**Collision Resolution Strategies:**
• **Chaining** - Each bucket holds a linked list
• **Open Addressing** - Find next empty slot (linear/quadratic probing)

**Load Factor = n/m** (items/buckets)
• Keep below 0.7 for good performance
• Rehash when too full

**Real-world uses:**
• Database indexing
• Caching
• Symbol tables in compilers
• JavaScript objects, Python dicts`,
        confidence: 0.94,
        topic: 'Data Structures'
    },
    'stack': {
        answer: `A **Stack** is a linear data structure following the **LIFO** principle (Last In, First Out).

**Think of it like:** A stack of plates - you can only add/remove from the top!

**Core Operations:**
• **push(x)** - Add element to top | O(1)
• **pop()** - Remove top element | O(1)
• **peek()/top()** - View top element | O(1)
• **isEmpty()** - Check if empty | O(1)

**Implementation:**
\`\`\`
Stack: [1, 2, 3, 4] ← TOP
push(5): [1, 2, 3, 4, 5]
pop(): returns 5, stack becomes [1, 2, 3, 4]
\`\`\`

**Real-world Applications:**
• Function call management (call stack)
• Undo/Redo operations
• Expression evaluation
• Backtracking algorithms
• Browser history (back button)`,
        confidence: 0.95,
        topic: 'Data Structures'
    },
    'queue': {
        answer: `A **Queue** is a linear data structure following the **FIFO** principle (First In, First Out).

**Think of it like:** A line at a store - first person in line gets served first!

**Core Operations:**
• **enqueue(x)** - Add element to rear | O(1)
• **dequeue()** - Remove front element | O(1)
• **front()** - View front element | O(1)
• **isEmpty()** - Check if empty | O(1)

**Types of Queues:**
• **Simple Queue** - Basic FIFO
• **Circular Queue** - Efficient use of space
• **Priority Queue** - Elements have priority levels
• **Deque** - Double-ended queue

**Applications:**
• Process scheduling (OS)
• Print job management
• Breadth-First Search (BFS)
• Request handling in web servers
• Message queues in distributed systems`,
        confidence: 0.94,
        topic: 'Data Structures'
    },
    'graph': {
        answer: `A **Graph** is a non-linear data structure consisting of **vertices (nodes)** and **edges (connections)**.

**Types:**
• **Directed** (edges have direction) vs **Undirected**
• **Weighted** (edges have values) vs **Unweighted**
• **Cyclic** vs **Acyclic**

**Representations:**
1. **Adjacency Matrix** - 2D array
   - Space: O(V²)
   - Edge lookup: O(1)

2. **Adjacency List** - Array of lists
   - Space: O(V + E)
   - Better for sparse graphs

**Common Algorithms:**
• **BFS** - Level-by-level traversal
• **DFS** - Deep exploration first
• **Dijkstra's** - Shortest path
• **Kruskal's/Prim's** - Minimum spanning tree

**Real-world Examples:**
• Social networks (friends as edges)
• Maps (cities as nodes, roads as edges)
• Web pages (hyperlinks)`,
        confidence: 0.93,
        topic: 'Data Structures'
    },
    'heap': {
        answer: `A **Heap** is a specialized tree-based data structure that satisfies the **heap property**.

**Types:**
• **Max Heap** - Parent ≥ Children (root is maximum)
• **Min Heap** - Parent ≤ Children (root is minimum)

**Properties:**
• Complete binary tree
• Efficiently implemented as an array
• Height: O(log n)

**Operations:**
• **Insert:** O(log n) - Add and bubble up
• **Extract Max/Min:** O(log n) - Remove root, heapify
• **Peek:** O(1) - View root
• **Build Heap:** O(n) - From unsorted array

**Array Representation:**
\`\`\`
For node at index i:
• Left child: 2i + 1
• Right child: 2i + 2
• Parent: (i-1) / 2
\`\`\`

**Applications:**
• Priority Queues
• Heap Sort
• Dijkstra's Algorithm
• Scheduling algorithms`,
        confidence: 0.92,
        topic: 'Data Structures'
    },

    // Thermodynamics
    'first law of thermodynamics': {
        answer: `The **First Law of Thermodynamics** is the law of **energy conservation** applied to thermodynamic systems.

**Statement:**
*"Energy cannot be created or destroyed, only transformed from one form to another."*

**Mathematical Form:**
**ΔU = Q - W**

Where:
• **ΔU** = Change in internal energy
• **Q** = Heat added to system (+) or removed (-)
• **W** = Work done BY the system

**Key Concepts:**
• Internal energy is a **state function** (path-independent)
• Heat and work are **path functions** (depend on process)
• Energy is always conserved in isolated systems

**Examples:**
• Heating water (Q → ΔU)
• Car engine (fuel's chemical energy → mechanical work)
• Refrigerator (work input → heat transfer)

**Sign Conventions:**
• Q > 0: Heat INTO system
• W > 0: Work done BY system`,
        confidence: 0.95,
        topic: 'Thermodynamics'
    },
    'second law of thermodynamics': {
        answer: `The **Second Law of Thermodynamics** governs the **direction of natural processes** and introduces **entropy**.

**Key Statements:**

1. **Clausius Statement:**
*"Heat cannot spontaneously flow from cold to hot."*

2. **Kelvin-Planck Statement:**
*"No heat engine can be 100% efficient."*

3. **Entropy Statement:**
*"The total entropy of an isolated system always increases."*

**Mathematical Form:**
**ΔS ≥ Q/T**

**Entropy (S):**
• Measure of disorder/randomness
• Always increases in spontaneous processes
• Universe's entropy is constantly increasing

**Implications:**
• Perfect efficiency is impossible
• Time has a direction (entropy arrow)
• Heat engines have maximum theoretical efficiency:
  **η = 1 - T_cold/T_hot** (Carnot efficiency)`,
        confidence: 0.94,
        topic: 'Thermodynamics'
    },
    'carnot cycle': {
        answer: `The **Carnot Cycle** is a theoretical thermodynamic cycle that represents the most efficient heat engine possible.

**Four Reversible Processes:**
1. **Isothermal Expansion** (A→B): Gas absorbs heat Q_H at T_H
2. **Adiabatic Expansion** (B→C): Gas expands without heat exchange
3. **Isothermal Compression** (C→D): Gas releases heat Q_C at T_C
4. **Adiabatic Compression** (D→A): Gas returns to initial state

**Carnot Efficiency:**
**η = 1 - T_C/T_H = (T_H - T_C)/T_H**

Where T is in Kelvin!

**Key Points:**
• No real engine can exceed Carnot efficiency
• Efficiency depends ONLY on temperatures
• Higher T_H or lower T_C → Better efficiency
• 100% efficiency only if T_C = 0K (impossible)

**Example:**
Steam engine with T_H = 500K, T_C = 300K:
η = 1 - 300/500 = 40% maximum efficiency`,
        confidence: 0.93,
        topic: 'Thermodynamics'
    },
    'entropy': {
        answer: `**Entropy (S)** is a fundamental thermodynamic property measuring the **disorder or randomness** of a system.

**Mathematical Definition:**
**dS = δQ_rev / T**

For reversible processes: ΔS = ∫(dQ/T)

**Key Properties:**
• State function (path-independent)
• SI Unit: J/K (Joules per Kelvin)
• Always increases in isolated systems

**Boltzmann's Statistical View:**
**S = k_B × ln(Ω)**
Where Ω = number of microstates

**Examples of Entropy Increase:**
• Ice melting (ordered solid → disordered liquid)
• Gas expanding into vacuum
• Mixing of two gases
• Heat flowing from hot to cold

**Important Equations:**
• Ideal gas: ΔS = nC_v ln(T₂/T₁) + nR ln(V₂/V₁)
• Phase change: ΔS = Q/T = mL/T`,
        confidence: 0.92,
        topic: 'Thermodynamics'
    },

    // Signal Processing
    'fourier transform': {
        answer: `The **Fourier Transform** converts a signal from **time domain to frequency domain**, revealing its frequency components.

**Mathematical Definition:**
**X(f) = ∫ x(t) × e^(-j2πft) dt**

**Key Concepts:**
• Any signal can be represented as sum of sinusoids
• Transform shows amplitude & phase at each frequency
• Inverse FT converts back to time domain

**Types:**
• **Continuous FT (CFT)** - For continuous signals
• **Discrete FT (DFT)** - For sampled signals
• **Fast FT (FFT)** - Efficient DFT algorithm, O(n log n)

**Properties:**
• Linearity: F{ax + by} = aF{x} + bF{y}
• Time shift → Phase shift in frequency
• Convolution in time → Multiplication in frequency

**Applications:**
• Audio/Image compression (MP3, JPEG)
• Signal filtering
• Spectrum analysis
• Communication systems`,
        confidence: 0.94,
        topic: 'Signal Processing'
    },
    'nyquist theorem': {
        answer: `The **Nyquist-Shannon Sampling Theorem** defines the minimum sampling rate needed to accurately capture a signal.

**Statement:**
*"To perfectly reconstruct a signal, sample at **at least twice** the highest frequency component."*

**Mathematical Form:**
**f_s ≥ 2 × f_max**

Where:
• **f_s** = Sampling frequency
• **f_max** = Highest frequency in signal (bandwidth)
• **f_s/2** = Nyquist frequency

**Aliasing:**
If sampling is too slow (f_s < 2×f_max):
• High frequencies appear as false low frequencies
• Information is lost and cannot be recovered
• Sounds distorted in audio; patterns in images (Moiré)

**Practical Example:**
Audio CD: f_max = 20 kHz (human hearing limit)
f_s = 44.1 kHz > 2 × 20 kHz ✓

**Anti-aliasing:**
• Use low-pass filter before sampling
• Remove frequencies above f_s/2`,
        confidence: 0.93,
        topic: 'Signal Processing'
    },
    'convolution': {
        answer: `**Convolution** is a mathematical operation that combines two signals to produce a third, showing how one signal modifies the other.

**Continuous Definition:**
**(f * g)(t) = ∫ f(τ) × g(t - τ) dτ**

**Discrete Definition:**
**(f * g)[n] = Σ f[k] × g[n - k]**

**Steps to Compute:**
1. Flip one signal (reverse it)
2. Slide it across the other
3. At each position, multiply and sum

**Key Properties:**
• Commutative: f * g = g * f
• Associative: (f * g) * h = f * (g * h)
• Distributive: f * (g + h) = f*g + f*h

**In Frequency Domain:**
Convolution in time = Multiplication in frequency
**F{f * g} = F{f} × F{g}**

**Applications:**
• Image blurring/sharpening
• Audio effects (reverb, echo)
• System response analysis
• Neural networks (CNNs)`,
        confidence: 0.92,
        topic: 'Signal Processing'
    },

    // Programming Concepts
    'recursion': {
        answer: `**Recursion** is a programming technique where a function calls itself to solve smaller instances of the same problem.

**Key Components:**
1. **Base Case** - Condition to stop recursion
2. **Recursive Case** - Function calls itself with simpler input

**Example - Factorial:**
\`\`\`javascript
function factorial(n) {
    if (n <= 1) return 1;        // Base case
    return n * factorial(n - 1); // Recursive case
}
// factorial(5) = 5 × 4 × 3 × 2 × 1 = 120
\`\`\`

**How it works (Call Stack):**
\`\`\`
factorial(4)
  → 4 × factorial(3)
    → 3 × factorial(2)
      → 2 × factorial(1)
        → returns 1
      → returns 2
    → returns 6
  → returns 24
\`\`\`

**Common Applications:**
• Tree/Graph traversal
• Divide and conquer algorithms
• Mathematical sequences (Fibonacci)
• Backtracking problems`,
        confidence: 0.95,
        topic: 'Programming'
    },
    'big o notation': {
        answer: `**Big O Notation** describes the **upper bound** of an algorithm's time or space complexity as input grows.

**Common Complexities (Best to Worst):**

| Notation | Name | Example |
|----------|------|---------|
| O(1) | Constant | Array access |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Simple loop |
| O(n log n) | Linearithmic | Merge sort |
| O(n²) | Quadratic | Nested loops |
| O(2ⁿ) | Exponential | Recursive Fibonacci |
| O(n!) | Factorial | Permutations |

**Rules:**
• Drop constants: O(2n) → O(n)
• Drop lower terms: O(n² + n) → O(n²)
• Consider worst case

**Analysis Tips:**
• Single loop over n items → O(n)
• Nested loops → O(n²)
• Halving each step → O(log n)
• Recursive with branching → Often exponential`,
        confidence: 0.94,
        topic: 'Algorithms'
    },
    'dynamic programming': {
        answer: `**Dynamic Programming (DP)** is an optimization technique that solves complex problems by breaking them into overlapping subproblems.

**Key Principles:**
1. **Optimal Substructure** - Optimal solution contains optimal solutions to subproblems
2. **Overlapping Subproblems** - Same subproblems are solved multiple times

**Approaches:**
• **Top-Down (Memoization)** - Recursive with caching
• **Bottom-Up (Tabulation)** - Iterative, building from smallest subproblems

**Example - Fibonacci:**
\`\`\`javascript
// Without DP: O(2ⁿ) - Exponential!
// With DP: O(n) - Linear!

function fibDP(n) {
    const dp = [0, 1];
    for (let i = 2; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2];
    }
    return dp[n];
}
\`\`\`

**Classic DP Problems:**
• Longest Common Subsequence
• 0/1 Knapsack
• Edit Distance
• Coin Change
• Matrix Chain Multiplication`,
        confidence: 0.93,
        topic: 'Algorithms'
    },

    // General patterns for common question types
    'what is': {
        answer: `I'd be happy to explain that concept! Could you be a bit more specific about what you'd like to learn about? 

For example, you could ask about:
• **Data Structures** - BST, Hash Tables, Graphs, Heaps
• **Algorithms** - Sorting, Searching, Dynamic Programming
• **Thermodynamics** - Laws, Entropy, Carnot Cycle
• **Signal Processing** - Fourier Transform, Convolution
• **Programming** - Recursion, Big O, OOP concepts

Just let me know what topic interests you! 🎯`,
        confidence: 0.7,
        topic: 'General'
    },
    'how does': {
        answer: `Great question! Understanding *how* things work is key to mastering any subject.

I can explain mechanisms and processes for topics like:
• **How sorting algorithms work** (Quick Sort, Merge Sort, etc.)
• **How data structures operate** (BST operations, hashing)
• **How thermodynamic cycles function** (Carnot, Otto, Diesel)
• **How signal processing transforms work** (FFT, Convolution)

Could you specify which concept you'd like me to break down step by step? 🔍`,
        confidence: 0.7,
        topic: 'General'
    },
    'explain': {
        answer: `I love explaining things! Teaching is one of my favorite things to do.

I can break down complex topics into simple, digestible explanations. Popular topics include:
• Core CS concepts (algorithms, data structures)
• Physics principles (thermodynamics, mechanics)
• Math fundamentals (calculus, linear algebra)
• Signal processing techniques

What would you like me to explain? I'll make sure to include examples and analogies to make it crystal clear! ✨`,
        confidence: 0.7,
        topic: 'General'
    },
    'help': {
        answer: `Of course! I'm here to help you succeed in your studies! 📚

**Here's what I can assist with:**

🎓 **Learning New Concepts**
Ask me to explain any topic from your courses

📝 **Problem Solving**
Walk through examples step by step

🧠 **Exam Preparation**
Review key concepts and common questions

💡 **Clarifying Doubts**
Get unstuck on confusing topics

**Try asking something like:**
• "What is a Binary Search Tree?"
• "Explain the First Law of Thermodynamics"
• "How does Quick Sort work?"

What would you like to learn today?`,
        confidence: 0.85,
        topic: 'General'
    }
};

// Enhanced intelligent response generator with advanced pattern matching
const generateAIResponse = (query, conversationHistory) => {
    const lowerQuery = query.toLowerCase().trim();
    const thinkingTime = 800 + Math.random() * 1200;

    return new Promise((resolve) => {
        setTimeout(() => {
            let response = null;
            let confidence = 0.85;
            let topic = 'General';

            // Advanced pattern matching with scoring
            let bestMatch = null;
            let bestScore = 0;

            for (const [key, value] of Object.entries(knowledgeBase)) {
                const keyWords = key.split(' ');
                let score = 0;

                if (lowerQuery.includes(key)) {
                    score = keyWords.length * 3;
                } else {
                    keyWords.forEach(word => {
                        if (lowerQuery.includes(word)) score += 1;
                    });
                }

                if (score > bestScore) {
                    bestScore = score;
                    bestMatch = value;
                }
            }

            if (bestScore >= 1 && bestMatch) {
                response = bestMatch.answer;
                confidence = bestMatch.confidence;
                topic = bestMatch.topic;
            }

            // Extended keyword detection
            if (!response) {
                const extendedTopics = {
                    'array': { text: `**Arrays** are fundamental data structures that store elements in contiguous memory.\n\n**Key Properties:**\n• Fixed size (in most languages)\n• O(1) random access via index\n• O(n) insertion/deletion\n\n**Operations:**\n• Access: arr[i] - O(1)\n• Search: O(n) linear, O(log n) if sorted\n• Insert/Delete: O(n) due to shifting`, conf: 0.9, top: 'Data Structures' },
                    'pointer': { text: `**Pointers** are variables that store memory addresses.\n\n**Key Concepts:**\n• Declaration: int *ptr;\n• Address-of operator: &variable\n• Dereference: *ptr\n\n**Common Uses:**\n• Dynamic memory allocation\n• Passing by reference\n• Data structures (linked lists, trees)`, conf: 0.88, top: 'Programming' },
                    'oop': { text: `**Object-Oriented Programming (OOP)** is a paradigm based on objects.\n\n**Four Pillars:**\n• **Encapsulation** - Bundling data with methods\n• **Inheritance** - Classes inherit from parents\n• **Polymorphism** - Same interface, different implementations\n• **Abstraction** - Hide complexity, show essentials`, conf: 0.92, top: 'Programming' },
                    'sql': { text: `**SQL (Structured Query Language)** manages relational databases.\n\n**Core Commands:**\n• SELECT - Query data\n• INSERT - Add records\n• UPDATE - Modify data\n• DELETE - Remove records\n• JOIN - Combine tables`, conf: 0.9, top: 'Databases' },
                    'complexity': { text: `**Time & Space Complexity** measure algorithm efficiency.\n\n**Time Complexity:** How runtime grows with input\n**Space Complexity:** Memory usage growth\n\n**Common Classes:**\nO(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ)`, conf: 0.91, top: 'Algorithms' },
                    'bfs': { text: `**Breadth-First Search (BFS)** explores graphs level by level.\n\n**Algorithm:**\n1. Start from source, add to queue\n2. Dequeue node, visit neighbors\n3. Add unvisited neighbors to queue\n4. Repeat until queue empty\n\n**Time: O(V+E) | Space: O(V)**\n**Uses:** Shortest path in unweighted graphs`, conf: 0.92, top: 'Algorithms' },
                    'dfs': { text: `**Depth-First Search (DFS)** explores as far as possible before backtracking.\n\n**Algorithm:**\n1. Start from source\n2. Visit node, mark visited\n3. Recursively visit unvisited neighbors\n4. Backtrack when stuck\n\n**Time: O(V+E) | Space: O(V)**\n**Uses:** Path finding, cycle detection, topological sort`, conf: 0.92, top: 'Algorithms' },
                    'binary search': { text: `**Binary Search** finds elements in sorted arrays efficiently.\n\n**Algorithm:**\n1. Compare target with middle element\n2. If equal, found!\n3. If target < middle, search left half\n4. If target > middle, search right half\n\n**Time: O(log n)** - Halves search space each step!`, conf: 0.94, top: 'Algorithms' },
                };

                for (const [kw, data] of Object.entries(extendedTopics)) {
                    if (lowerQuery.includes(kw)) {
                        response = data.text;
                        confidence = data.conf;
                        topic = data.top;
                        break;
                    }
                }
            }

            // Greetings
            if (/^(hi|hello|hey|good\s*(morning|afternoon|evening)|howdy|sup)\b/.test(lowerQuery)) {
                response = `Hey there! 👋 Great to see you!\n\nI'm Study Pilot AI, ready to help you master any topic!\n\n**Popular topics I can explain:**\n• 🌳 Data Structures & Algorithms\n• 🔥 Thermodynamics\n• 📊 Signal Processing\n• 💻 Programming Concepts\n\nWhat would you like to learn? 🚀`;
                confidence = 0.98;
                topic = 'General';
            }

            // Thanks
            if (/thank|thanks|thx|appreciate/.test(lowerQuery)) {
                response = `You're welcome! 😊 Happy to help!\n\nFeel free to ask more questions anytime. Keep crushing those studies! 📚✨`;
                confidence = 0.98;
                topic = 'General';
            }

            // Identity questions
            if (/who\s*(are|r)\s*you|what\s*(are|r)\s*you|your\s*name|about\s*you/.test(lowerQuery)) {
                response = `I'm **Study Pilot AI** 🤖 - your personal learning companion!\n\n**What I do:**\n• Explain complex topics simply\n• Help with CS, Physics, Math & more\n• Provide examples and code snippets\n• Make learning engaging!\n\n**Ask me anything** - I'm here 24/7! 🎓`;
                confidence = 0.98;
                topic = 'General';
            }

            // Smart fallback with context
            if (!response) {
                const suggestions = ['Binary Search Tree', 'Quick Sort', 'Thermodynamics', 'Fourier Transform', 'Dynamic Programming', 'Big O Notation'];
                const pick = suggestions[Math.floor(Math.random() * suggestions.length)];

                response = `Interesting question! 🤔\n\nI'm knowledgeable about:\n• **Data Structures** - Arrays, Trees, Graphs, Hash Tables\n• **Algorithms** - Sorting, Searching, DP\n• **Thermodynamics** - Laws, Entropy, Cycles\n• **Signal Processing** - FFT, Convolution\n• **Programming** - OOP, Recursion, Complexity\n\n**Try:** "${pick}"\n\nOr rephrase and I'll help! 💡`;
                confidence = 0.65;
            }

            resolve({ answer: response, confidence, topic, isLocal: true });
        }, thinkingTime);
    });
};

function AskPage() {
    const [query, setQuery] = useState('');
    const [courses, setCourses] = useState([
        { id: 1, name: 'Data Structures' },
        { id: 2, name: 'Algorithms' },
        { id: 3, name: 'Thermodynamics' },
        { id: 4, name: 'Signal Processing' }
    ]);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [loading, setLoading] = useState(false);
    const [messages, setMessages] = useState([]);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        // Welcome message
        setMessages([{
            type: 'ai',
            content: "Hey there! 👋 I'm **Study Pilot AI**, your friendly learning buddy!\n\nThink of me as that smart friend who's always ready to help you understand tricky concepts. I'm powered by a local knowledge base, so I work **completely offline** - no internet needed!\n\n**What I can help you with:**\n• Explain difficult topics in simple terms\n• Answer questions about Data Structures & Algorithms\n• Help with Thermodynamics concepts\n• Break down Signal Processing principles\n• Guide you through programming concepts\n\nJust type your question below and let's make learning fun! 🚀",
            timestamp: new Date()
        }]);
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        if (!query.trim() && uploadedFiles.length === 0) return;

        const userMessage = {
            type: 'user',
            content: query,
            files: uploadedFiles.map(f => f.name),
            timestamp: new Date()
        };

        const currentMessages = [...messages, userMessage];
        setMessages(currentMessages);
        setLoading(true);
        const savedQuery = query;
        setQuery('');
        setUploadedFiles([]);

        try {
            // Use local AI response generator
            const conversationHistory = currentMessages
                .filter(m => m.type === 'user' || m.type === 'ai')
                .slice(-10)
                .map(m => ({ type: m.type, content: m.content }));

            const data = await generateAIResponse(savedQuery, conversationHistory);

            // Add friendly response variations
            const friendlyPrefixes = [
                "Great question! ",
                "Ah, I see what you're asking! ",
                "Let me explain that for you. ",
                "That's an interesting topic! ",
                "Happy to help with this! "
            ];
            const friendlySuffixes = [
                "\n\nDoes that make sense? Feel free to ask follow-up questions! 😊",
                "\n\nLet me know if you'd like me to explain any part in more detail!",
                "\n\nHope that helps! What else would you like to know?",
                "\n\nAnything else you're curious about?"
            ];

            const prefix = friendlyPrefixes[Math.floor(Math.random() * friendlyPrefixes.length)];
            const suffix = friendlySuffixes[Math.floor(Math.random() * friendlySuffixes.length)];

            const aiMessage = {
                type: 'ai',
                content: prefix + data.answer + suffix,
                confidence: data.confidence,
                topic: data.topic,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (err) {
            console.error('Error:', err);
            setMessages(prev => [...prev, {
                type: 'ai',
                content: "Hmm, something unexpected happened! 😅 But don't worry, I'm running locally so let's try again. Could you rephrase your question?",
                isError: true,
                timestamp: new Date()
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = (e) => {
        const files = Array.from(e.target.files);
        const validFiles = files.filter(f =>
            f.type === 'application/pdf' ||
            f.type === 'application/vnd.openxmlformats-officedocument.presentationml.presentation' ||
            f.type === 'text/plain'
        );

        if (validFiles.length > 0) {
            setUploadedFiles(prev => [...prev, ...validFiles]);
            // Add file upload message
            setMessages(prev => [...prev, {
                type: 'system',
                content: `📎 Uploaded: ${validFiles.map(f => f.name).join(', ')}`,
                timestamp: new Date()
            }]);
        }
    };

    const removeFile = (index) => {
        setUploadedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const clearChat = () => {
        if (window.confirm("Are you sure you want to clear the entire conversation?")) {
            setMessages([{
                type: 'ai',
                content: "Chat cleared! 🧹 What would you like to learn about now? I'm ready for new questions!",
                timestamp: new Date()
            }]);
        }
    };

    const formatTime = (date) => {
        return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const renderMessageContent = (content) => {
        // Simple markdown-like rendering
        return content.split('\n').map((line, i) => {
            // Bold text
            line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            // Bullet points
            if (line.startsWith('• ')) {
                return <li key={i} dangerouslySetInnerHTML={{ __html: line.substring(2) }} />;
            }
            return <p key={i} dangerouslySetInnerHTML={{ __html: line || '&nbsp;' }} />;
        });
    };

    const handleQuickQuery = (text) => {
        setQuery(text);
        // We can't immediately submit because state updates are async, 
        // but the user can click send or we could handle it with a useEffect if needed.
        // For now, setting it is enough for them to see it.
    };

    return (
        <div className="ask-page">
            {/* Header */}
            <div className="ask-header">
                <div className="ai-identity">
                    <div className="ai-avatar">
                        <span>🤖</span>
                    </div>
                    <div className="ai-info">
                        <h1>Study Pilot AI</h1>
                        <span className="ai-status">
                            <span className="status-dot"></span>
                            Online • Here to help you learn!
                        </span>
                    </div>
                </div>

                <div className="header-actions">
                    <button className="clear-chat-btn" onClick={clearChat} title="Clear Conversation">
                        <span>🧹 Clear Chat</span>
                    </button>

                    <select
                        className="course-select"
                        value={selectedCourse || ''}
                        onChange={(e) => setSelectedCourse(e.target.value ? parseInt(e.target.value) : null)}
                    >
                        <option value="">All Courses</option>
                        {courses.map(course => (
                            <option key={course.id} value={course.id}>{course.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Chat Messages */}
            <div className="chat-container">
                <div className="messages">
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`message ${msg.type} ${msg.isError ? 'error' : ''}`}
                        >
                            {msg.type === 'ai' && (
                                <div className="message-avatar">🤖</div>
                            )}

                            <div className="message-content">
                                {msg.type === 'ai' && (
                                    <div className="message-header">
                                        <span className="sender-name">Study Pilot AI</span>
                                        <span className="message-time">{formatTime(msg.timestamp)}</span>
                                    </div>
                                )}

                                {msg.type === 'user' && (
                                    <div className="message-header">
                                        <span className="message-time">{formatTime(msg.timestamp)}</span>
                                        <span className="sender-name">You</span>
                                    </div>
                                )}

                                <div className="message-text">
                                    {msg.type === 'system' ? (
                                        <span className="system-text">{msg.content}</span>
                                    ) : (
                                        renderMessageContent(msg.content)
                                    )}
                                </div>

                                {msg.files && msg.files.length > 0 && (
                                    <div className="message-files">
                                        {msg.files.map((file, i) => (
                                            <span key={i} className="file-tag">📎 {file}</span>
                                        ))}
                                    </div>
                                )}

                                {msg.citations && msg.citations.length > 0 && (
                                    <div className="message-citations">
                                        <div className="citations-header">📚 Sources</div>
                                        {msg.citations.slice(0, 3).map((citation, i) => (
                                            <div key={i} className="citation-item">
                                                <span className="citation-num">[{citation.index}]</span>
                                                <span className="citation-text">{citation.citation}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {msg.confidence !== undefined && (
                                    <div className="message-confidence">
                                        <span className={`confidence-badge ${msg.confidence > 0.7 ? 'high' : msg.confidence > 0.4 ? 'medium' : 'low'}`}>
                                            {Math.round(msg.confidence * 100)}% confidence
                                        </span>
                                    </div>
                                )}
                            </div>

                            {msg.type === 'user' && (
                                <div className="message-avatar user">👤</div>
                            )}
                        </div>
                    ))}

                    {loading && (
                        <div className="message ai">
                            <div className="message-avatar">🤖</div>
                            <div className="message-content">
                                <div className="typing-indicator">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Uploaded Files Preview */}
            {uploadedFiles.length > 0 && (
                <div className="uploaded-files">
                    {uploadedFiles.map((file, index) => (
                        <div key={index} className="file-preview">
                            <span className="file-icon">
                                {file.type.includes('pdf') ? '📄' : '📊'}
                            </span>
                            <span className="file-name">{file.name}</span>
                            <button onClick={() => removeFile(index)} className="file-remove">×</button>
                        </div>
                    ))}
                </div>
            )}

            {/* Suggested Questions */}
            {messages.length < 3 && (
                <div className="suggested-questions">
                    <p className="suggestions-title">Try asking about:</p>
                    <div className="suggestions-grid">
                        <button onClick={() => handleQuickQuery("What is a Binary Search Tree?")} className="suggestion-chip">
                            🌳 Binary Search Tree
                        </button>
                        <button onClick={() => handleQuickQuery("Explain the First Law of Thermodynamics")} className="suggestion-chip">
                            🔥 First Law of Thermo
                        </button>
                        <button onClick={() => handleQuickQuery("How does Quick Sort work?")} className="suggestion-chip">
                            ⚡ Quick Sort
                        </button>
                        <button onClick={() => handleQuickQuery("What is Fourier Transform?")} className="suggestion-chip">
                            📈 Fourier Transform
                        </button>
                    </div>
                </div>
            )}

            {/* Input Area */}
            <div className="input-area">
                <form onSubmit={handleSubmit} className="input-form">
                    <button
                        type="button"
                        className="upload-btn"
                        onClick={() => fileInputRef.current?.click()}
                        title="Upload PDF or Slides"
                    >
                        📎
                    </button>

                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                        accept=".pdf,.pptx,.txt"
                        multiple
                        hidden
                    />

                    <input
                        type="text"
                        className="chat-input"
                        placeholder="Ask me anything... I'm here to help! 💬"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />

                    <button
                        type="submit"
                        className="send-btn"
                        disabled={loading || (!query.trim() && uploadedFiles.length === 0)}
                    >
                        {loading ? (
                            <span className="send-loading"></span>
                        ) : (
                            <span>➤</span>
                        )}
                    </button>
                </form>

                <p className="input-hint">
                    Study-Pilot AI can make mistakes.
                </p>
            </div>
        </div>
    );
}

export default AskPage;
