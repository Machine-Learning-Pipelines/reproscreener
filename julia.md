![](assets_j/img-0147.jpg)

![](assets_j/img-0148.jpg)

Contents lists available at [ScienceDirect](http://www.ScienceDirect.com/) Journal of Computational Physics

### www.elsevier.com/locate/jcp

A fast marching algorithm for the factored eikonal equation Eran Treister a,∗ Eldad Haber a,b  
a *Department of Earth and Ocean Sciences, The University of British Columbia, Vancouver, BC, Canada*  
b *Department of Mathematics, The University of British Columbia, Vancouver, BC, Canada*

![](assets_j/img-0149.jpg)

### a r t i c l e i n f o

*Article history:*  
Received 14 April 2016  
Received in revised form 5 August 2016 Accepted 8 August 2016  
Available online 12 August 2016 *Keywords:*  
Eikonal equation  
Factored eikonal equation  
Fast Marching  
First arrival  
Travel time tomography  
Gauss–Newton  
Seismic imaging

##### 1. Introduction

a b s t r a c t

The eikonal equation is instrumental in many applications in several ﬁelds ranging from computer vision to geoscience. This equation can be eﬃciently solved using the iterative Fast Sweeping (FS) methods and the direct Fast Marching (FM) methods. However, when used for a point source, the original eikonal equation is known to yield inaccurate numerical solutions, because of a singularity at the source. In this case, the factored eikonal equation is often preferred, and is known to yield a more accurate numerical solution. One application that requires the solution of the eikonal equation for point sources is travel time tomography. This inverse problem may be formulated using the eikonal equation as a forward problem. While this problem has been solved using FS in the past, the more recent choice for applying it involves FM methods because of the eﬃciency in which sensitivities can be obtained using them. However, while several FS methods are available for solving the factored equation, the FM method is available only for the original eikonal equation. In this paper we develop a Fast Marching algorithm for the factored eikonal equation, using both ﬁrst and second order ﬁnite-difference schemes. Our algorithm follows the same lines as the original FM algorithm and requires the same computational effort. In addition, we show how to obtain sensitivities using this FM method and apply travel time tomography, formulated as an inverse factored eikonal equation. Numerical results in two and three dimensions show that our algorithm solves the factored eikonal equation eﬃciently, and demonstrate the achieved accuracy for computing the travel time. We also demonstrate a recovery of a 2D and 3D heterogeneous medium by travel time tomography using the eikonal equation for forward modeling and inversion by Gauss–Newton.  
© 2016 Elsevier Inc. All rights reserved.

The eikonal equation appears in many ﬁelds, ranging from computer vision [30,31,33,11], where it is used to track evolution of interfaces, to geoscience [19,12,22,14,24] where it describes the propagation of the ﬁrst arrival of a wave in a medium. The equation has the form

# |∇ τ | 2 = κ( ? x) 2 ,

################# (1.1)

where \| ·\| is the Euclidean norm. In the case of wave propagation, τ is the travel time of the wave and κ( ? *x)* is the slowness (inverse velocity) of the medium. The value of τ is usually given at some sub-region. For example, in this work we assume the wave propagates from a point source at location ? *x0,* for which the travel time is 0, and hence τ( ? *x0)* = 0.

\* Corresponding author.  
*E-mail addresses:* [erantreister@gmail.com](mailto:erantreister@gmail.com) (E. Treister), [haber@math.ubc.ca](mailto:haber@math.ubc.ca) (E. Haber). [http://dx.doi.org/10.1016/j.jcp.2016.08.012](http://dx.doi.org/10.1016/j.jcp.2016.08.012)  
0021-9991/© 2016 Elsevier Inc. All rights reserved.

---

![](assets_j/img-0637.jpg)

**Fig. 1.** The *l2* norm of the approximation error \|∇τ0 − *Dτ0* \| around a source point at [0.5,0.5], where τ0 is the distance function and *D* is a central difference gradient operator on a mesh with *hx* = *hy* = 0.01.

Equation (1.1) is nonlinear, and as such may have multiple branches in its solution. One of these branches, which is the one of interest in the applications mentioned earlier, corresponds to the “ﬁrst-arrival” viscosity solution, and can be calculated eﬃciently [5,25]. One of the ways to compute it is by using the Fast Marching (FM) methods [36,30,31], which solve it directly using ﬁrst or second order schemes in O(n logn) operations. These methods are based on the monotonicity of the solution along the characteristics. Alternatively, (1.1) can be solved iteratively by Fast Sweeping (FS) methods, which may be seen as Gauss–Seidel method for (1.1). First order accurate solutions of (1.1) can be obtained very eﬃciently in 2 *d* Gauss–Seidel sweeps in O(n) operations, where *d* is the dimension of the problem [35,38]. An alternative for the mentioned approaches is to use FS to solve a Lax–Friedrichs approximation for (1.1), which involves adding artiﬁcial viscosity to the original equation [10]. This approach was suggested for general Hamilton–Jacobi equations, and is simple to implement. In [23], such Lax–Friedrichs approximation is obtained using FS up to third order accuracy using the weighted essentially non-oscillatory (WENO) approximations to the derivatives. For a performance comparison between some of the mentioned solvers see [7].  
In some cases, the eikonal equation (1.1) is used to get a geometrical-optics ansatz of the solution of the Helmholtz equation in the high frequency regime [12,15,19,17]. This is done using the Rytov decomposition of the Helmholtz solution: *u(* ? *x)* = *a(* ? *x)* exp(iωτ( ? x)), where *a(* ? *x)* is the amplitude and τ( ? *x)* is the travel time. This approach involves solving (1.1) for the travel-time and solving the transport equation

### ∇ τ ·∇a + 1 a?τ = 1 (∇ τ ·∇a +∇ · (a∇ τ)) = 0

################# (1.2)

2  
2  
for the amplitude [15,19]. The resulting approximation includes only the ﬁrst arrival information of the wave propagation. Somewhat similarly, the work of [9] suggests using the eikonal solution to get a multigrid preconditioner for solving linear systems arising from discretization of the Helmholtz equation.  
In many cases in seismic imaging, the eikonal equation is used for modeling the migration of seismic waves from a point source at some point ? *x0.* In this case, when solving (1.1) numerically by standard ﬁnite differences methods, the obtained solution has a strong singularity at the location of the source, which leads to large numerical errors [22,6]. Fig. 1 illustrates this phenomenon by showing the approximation error for the gradient of the distance function, which is the solution of (1.1) for κ = 1. It is clear that the largest approximation error for the gradient is located around the source point, and that its magnitude is rather large. In addition, it is observed that although τ may have more singularities in other places, the singularity at the source is more damaging and polluting for the numerical solution [22,6].  
A rather easy treatment to the described phenomenon is suggested in [21,6], and achieved using a factored version of (1.1). That is, we deﬁne  
τ = τ0τ1, (1.3) where τ0 is the distance function, τ0 = ?? *x* − ? *x0* ? 2, from the point source—the analytical solution for (1.1) in the case where κ( ? *x)* = 1 is a constant. Indeed, at the location of the source, the function τ0 is non-smooth. However, the computed factor τ1 is expected to be very smooth at the surrounding of the source, and can be approximated up to high order of accuracy [18]. Plugging (1.3) into (1.1) and applying the chain rule yields the *factored eikonal equation*

# τ 2 |∇ τ1 | 2 + 2τ0τ1 ∇ τ0 ·∇ τ1 + τ 2 = κ( ? x) 2 .

################# (1.4)

0  
1  
Similarly to it original version, Equation (1.4) can be solved by fast sweeping methods in ﬁrst order accuracy [6,16,18], or by a Lax–Friedrichs scheme up to third order of accuracy [19,15,18]. The recent works [18,20] suggest hybrid schemes where the factored eikonal is solved at the neighborhood of the source and the standard eikonal, which is computationally easier, is solved in the rest of the domain.  
One geophysical tool that ﬁts the scenario described earlier is travel time tomography. One way to formulate it is by using the eikonal equation as a forward problem inside an inverse problem [29]. To solve the inverse problem, one should be able to solve (1.1) accurately for a point source, and to compute its sensitivities eﬃciently. The works of [13,34] computes

---

the tomography by FS, and require an FS iterative solution for computing the sensitivities. The more recent [14] uses the FM algorithm for forward modeling using the non-factored eikonal equation, because this way the sensitivities are obtained more eﬃciently by a simple solution of a lower triangular linear system. [3] suggests to use FS for forward modeling using the factored equation, but also eﬃciently obtain the sensitivities by approximating them using FM with the non-factored eikonal equation.  
In this paper, we develop a Fast Marching algorithm for the factored eikonal equation (1.4), based on [30,31]. As in [31], our algorithm is able to solve (1.4) using ﬁrst order or second order schemes, in guaranteed O(n logn) running time. When using our method for forward modeling in travel time tomography, one achieves both worlds: (1) have an accurate forward modeling based on the factored eikonal equation, and (2) obtain the sensitivities of the (factored) forward modeling eﬃciently, by solving lower triangular linear systems in O(n) operations. Computationally, this is one of the most attractive ways to solve the inverse problem, since the cost of the inverse problem can be governed by the cost of applying the sensitivities.

Our paper is organized as follows. In the next section we brieﬂy review the FM method in [30,31], including some of its implementation details. Next, we show our extension to the FM method for the factored eikonal equation—in both ﬁrst and second order of accuracy—and provide some theoretical properties. Following that, we discuss the derivation of sensitivities using FM and brieﬂy present the travel time tomography problem. Last, we show some numerical results that demonstrate the effectiveness of the method in two and three dimensions, for both the forward and inverse problems.

##### 2. The Fast Marching algorithm

We now review the FM algorithm of [30,31] in two dimensions. The extension to higher dimensions is straightforward. The FM algorithm is based on the Godunov upwind discretization [25] of (1.1). In two dimensions, this discretization is given by  
?  
?  
\|∇ τ \| 2 ≈ max\{D −x τ,−D +x τ,0\} 2 + max\{D −y τ,−D +y τ,0\} 2 = κ( ? *xij)* 2 , ? *xij* ∈ ?h,

################# (2.5)

*ij ij ij ij*

where in the simplest form *D* −x τ = *τi,j −τi−1,j* and *D* +x τ = *τi+1,j −τi,j* are the backward and forward ﬁrst derivative operators, *ij h ij h*  
respectively. In principal, one can replace these operators with ones of higher order of accuracy.  
The FM algorithm solves (2.5) in a sophisticated way, exploiting the fact that the upwind difference structure of (2.5) imposes a unique direction in which the information propagates—from smaller values of τ to larger values. Hence, the FM algorithm rests on solving (2.5) by building the solution outwards from the smallest τ value. It assumes that some initial value of τ is given at some region of ?h (or a point ? *x0)* and it propagates outwards from this initial region, by updating the next smallest value of τ at each step.  
To apply the rule above, let us deﬁne three disjoint sets of variables: the knownvariables, the frontvariables (which are sometimes called the *trial* variables) and the unknownvariables. These three sets together contain all the grid points in the problem. For simplicity, let us assume that we solve (2.5) for a point source. That is, a source is located at point ? *x0,* for which τ( ? *x0)* = 0. Initially, knownis chosen as an empty set, frontis set to contain only ? *x0,* and unknownhas the rest of the variables for which τ is set to inﬁnity. At each step we choose the point ? *xij* in frontwith minimal value of τ( ? *xij)* and move it to known. Next, we move all of its neighbors which are in unknown to front, and solve (2.5) for all neighbors which are not in known. This way, we set all variables to be in known in *n* steps, and the algorithm ﬁnishes. A precise description of the algorithm is given in Algorithm 1.

### Algorithm 1: Fast Marching

Initialize:  
*τij* = ∞ for all *?xij* ∈ ?h, τ(?x0) = 0, known← ∅, front← \{?x0 \}.  
**while** front? = ∅ **do**

1. Find the minimal entry in front: *ximin,jmin* = argmin?xij *\{τij* : *?xij* ∈front\}
2. Add *?ximin,jmin* to knownand take it out of front: front←front\\\{?ximin,jmin \} ; known←known∪\{?ximin,jmin \}.
3. Add the unknown neighborhood of *?ximin,jmin* to front:  
N = *\{?ximin−1,jmin, ?ximin+1,jmin, ?ximin,jmin−1, ?ximin,jmin+1* \}\\known *min*  
front←front∪ N *min.*
4. **Foreach** *?xij* ∈ N *min*  
Update *τij* by solving the quadratic (2.5), using only entries in known.

- *ximin,jmin* = argmin?xij *\{τij* : *?xij* ∈front\}  
Add *?ximin,jmin* to knownand take it out of front: front←front\\\{?ximin,jmin \} ; known←known∪\{?ximin,jmin \}.  
Add the unknown neighborhood of *?ximin,jmin* to front:  
N = *\{?ximin−1,jmin, ?ximin+1,jmin, ?ximin,jmin−1, ?ximin,jmin+1* \}\\known  
*min*  
front←front∪ N *min.*  
**Foreach** *?xij* ∈ N *min*  
Update *τij* by solving the quadratic (2.5), using only entries in known.

### End

### end

---

![](assets_j/img-0669.jpg)

**Fig. 2.** A minimum heap and its implementation using array.

In [30] it was proved that Algorithm 1 produces a viable viscosity solution to (2.5) when using ﬁrst order approximations for the ﬁrst derivatives. Furthermore, it is proved that the values of τ in the order of which the points are set to knownin Step 2 are monotonically increasing.

*2.1. Eﬃcient implementation using minimum heap*

Algorithm 1 has two main computational bottlenecks in Steps 1 and 4, which are repeated *n* times. For a d-dimensional problem, the set front contains a d-1 dimensional manifold of points, of size O(n *d−1* ). To ﬁnd the minimum of front *d*

eﬃciently, a minimum heap data structure is used [30,31]. A minimum heap is a binary tree with a property that a value at any node is less than or equal to the values at its two children. Consequently, the root of the tree holds the minimal value. The simplest implementation of such a tree is done by a sequential array of nodes, using the rule that if a node is located at entry *k,* then its two children are located at entries 2k and 2k + 1 (the ﬁrst element of the array is indexed by 1, and is the root of the tree). Equivalently, the parent of a node at entry *k* is located at entry ?k/2?. Fig. 2 shows an example of a minimum heap and its implementation using array. Generally, each element in the array can hold many properties, and one of these has to be deﬁned as a comparable “key”, which is used in the heap for sorting. In our case, each node holds a point ? *x* in the mesh, and its value τ( ? *x)* as a key.  
In its simplest form, the minimum heap structure supports two basic operations: insert(element,key) and get- Min(). For example, this is the case in the C++ standard library implementation of the minimum heap structure. To apply getMin(), we remove the ﬁrst element in the array, and take the last element in the array and push it in the ﬁrst place. Then, to maintain the property of the heap, we repeatedly replace this value with its smaller child (the smaller of the two) until it reaches down in the tree to the point where it is smaller than its two children or it has no children. The insert(element,key) operation ﬁrst places a new element at the next empty space of the array. Then, it propagates this element upwards, each time replacing it with its parent until it reaches a point where the element is either the root or its key is larger than its parent’s key. Both of the described operations are performed in O(logm) complexity where *m* is the number of elements in the heap.  
In Algorithm 1, the set frontis implemented using a min-heap. Steps 1–2 are trivially implemented using getMin(), and insert(element,key) is used in Step 3. However, Step 4 of Algorithm 1 requires updating values which are inside the heap but are not at the root. This operation is not supported in the standard deﬁnition of either priority queue or minimum heap. Indeed, the papers [30,31] use a variant of a priority queue, which includes back-links from points ? *xij* to their corresponding locations inside the heap, and a more “software-engineering friendly” implementation of this idea is suggested in [2], where those back-links are incorporated within the heap implementation, without any relation to the mesh. However, although this way an update of a key inside the heap can still be implemented in O(logm), it requires a specialized implementation of the heap, and encumbers the operations described earlier to maintain these back-links. In our implementation, we bypass this need for back-links, and implement Step 4 by reinserting elements to the heap if they are indeed smaller than their value in the heap. In Step 1, we simply ignore entries which are in known already. If the algorithm is indeed monotone, like the ﬁrst order version in [30], this implementation detail will not change the result of the algorithm. The downside of this change is that it enables frontto grow more than in the back-linked version. However, even if it grows four times compared to the back-linked version, then the heap tree is just two nodes higher, making the difference in running time insigniﬁcant.

*2.2. Second order Fast Marching*

Solving the eikonal equation based on a ﬁrst order discretization in (2.5) provides guaranteed monotonicity and stability. However, it also provides a less accurate solution because of the added viscosity that is associated with the ﬁrst order approximation. To get a more accurate FM method, [31] suggests to use a second order upwind approximation in (2.5), e.g.

---

# D − τ = 3τi − 4τi−1 + τi−2 D + τ = −3τi + 4τi+1 − τi+2 .

################# (2.6)

*i* 2h *i* 2h  
However, in some cases, the scheme may revert to ﬁrst order approximations from certain directions. The obvious case for that is when there are not enough knownpoints for the high order stencil. This case occurs for example when the given initial region contains only one point. Another condition for using second order operators is given in [31]:

##### τi−1 ≥ τi−2 or τi+1 >τi+2,

################# (2.7)

where the left condition is used for backward operators and the right one for forward operators. If (2.7) is not satisﬁed, the algorithm reverts to ﬁrst order operators. Later we show that this condition guarantees the monotonicity of the non-factored FM solution using second order scheme.

##### 3. Fast Marching for the factored eikonal equation

Let us rewrite the factored eikonal equation (1.4) in a squared form, which is closer (1.1):

# | τ0 ∇ τ1 + τ1 ∇ τ0 | 2 = κ( ? x) 2 .

################# (3.8)

This writing is the key for deriving the FM algorithm for (1.4). Similarly to the Godunov upwind scheme in (2.5), we discretize (3.8) for τ1 using a derivative operator *D* ˆ instead of *D*  
?  
?

### max{ D ˆ −x τ1,− D ˆ +x τ1,0} 2 + max{ D ˆ −y τ1,− D ˆ +y τ1,0} 2 = κ( ? xij) 2 , ? xij ∈ ?h.

################# (3.9)

*ij ij ij ij*

For example, the backward ﬁrst order factored derivative operator is given by

###### D ˆ −x τ1 = (τ0)ij (τ1)i,j −(τ1)i−1,j +(p0)ij(τ1)ij,

################# (3.10)

*ij*  
*h*  
where τ0 and *p0* = ∂τ0 are known. From this point we apply the Algorithm 1 as it is. We hold the values of τ0τ1 in front, and in Step 4 we update ∂x  
(τ1)ij with the solution of (3.9).  
**Initialization:** For the non-factored equation, Algorithm 1 is initialized by τ( ? *x0)* = 0 at the point source. In the factored equation, this is trivially fulﬁlled by deﬁnition, because at the source τ0( ? *x0)* = 0. Still, τ1( ? *x0)* should not be chosen arbitrarily since its value is used in the ﬁnite difference approximations when evaluating its neighbors. Examining (3.8) at the source yields τ1( ? *x0)* 2\|∇ τ0 \|2 = τ1( ? *x0)* 2 = κ( ? *x0)* 2 , since we choose τ0 such that \|∇ τ0 \|2 = 1, independently of κ. In some cases in the literature, i.e., [6], the value κ( ? *x0)* is absorbed in τ0, such that \|∇ τ0 \|2 = κ( ? *x0)* 2 . Then τ1( ? *x0)* should be chosen as 1. This is obviously equivalent for computing τ, however, it is much more convenient to choose τ0 independently of κ if one wants to obtain the sensitivities of the FM algorithm (for more details, see Section 4).  
**Second order discretization:** Similarly to the non-factored equation, the second order upwind approximations (2.6) can be used in (3.9)–(3.10) for τ1. Again, we revert to the ﬁrst order approximation in cases where the additional point needed for the second order approximation is not in known. We note that unlike the non-factored case, the solution τ1 is in most cases very smooth at the source (expected to be close to constant or linear). So, when we initialize the algorithm with the value of τ1 at the point source and revert to a ﬁrst order approximation for the neighbors, we do not introduce large discretization errors. In the non-factored case, the second derivative of τ is singular at the source, so using ﬁrst order approximation there signiﬁcantly pollutes the rest of the solution.

*3.1. Solution of the piecewise quadratic equation*

We now describe how to solve both the non-factored and factored piecewise quadratic equations (2.5) and (3.9) respec- tively. This is required in Step 4 of Algorithm 1. Solving such an equation consists of the following four steps:

1. Determine the order of approximation for each derivative in (2.5)/(3.9) (only required for high order schemes).
2. Determine which directions to choose (backward or forward) for each dimension (x, *y* or z).
3. Solve the quadratic equation in (2.5)/(3.9), assuming all terms are positive.
4. Make sure that the solution is valid, such that all max terms in (2.5)/(3.9) are indeed held with positive values. If not, some terms should be dropped, and the quadratic problem with the remaining terms is solved again.

Let us ﬁrst consider solving the non-factored ﬁrst order (2.5), for which the Step 1 is not relevant. In this case, Step 2 is simple: for each max\{D − τ, −D + τ, 0\} term, the smaller of the two values of τ from both sides (forward or backward) is *i j i j*  
guaranteed to give a higher ﬁnite difference derivative. Furthermore, in Step 4, if some of the terms turn out negative after Step 3, then we can drop terms from (2.5) in decreasing order of the τ values, until a valid solution is reached. The same is true for a ﬁrst order factored version in (3.9).  
However, using second order schemes (selectively) imposes additional complications on the solution of the piecewise quadratic equations (2.5) and (3.9). There are many options for order of accuracy vs directions in Steps 1–2, and in addition

---

it is not clear in which order to drop terms in Step 4 if negative terms are detected. Obviously, one can check all possibilities, but such an option may be costly in high dimensions. To simplify this we follow [31], and in Step 1 we use the second order approximation if the extra point is available in knownand fulﬁlls the condition (2.7), and revert to ﬁrst order approximation if not. Then, in Step 2 we determine the choice of directions considering the non-factored ﬁrst order approximation (2.5). That is, if (τ0τ1)i−1 < (τ0τ1)i+1, then we choose the backward upwind direction; otherwise we choose the forward direction. That is done correspondingly for each dimension.  
Once Steps 1–2 are done, (3.9) reduces to a piecewise quadratic equation of the form  
?  
max\{ *αk(τij* −βk),0\} 2 = κ( ? *xij)* 2 ,

################# (3.11)

*k*  
where αk ≥ 0, βk ≥ 0 are non-negative constants that are coming from the ﬁnite difference approximations. For exam- ple, assuming that *k* = 1 corresponds to the *x* coordinate, then (3.10) would correspond to α1 = (τ0)i,j + (p0)i,j and *h*  
β1 = (τ0)i,j(τ1)i−1,j . In Step 3 we simply ignore the max\{·, 0\} function and solve the equation assuming all terms are positive. *hα1*  
We solve a simple quadratic function and choose the larger one of its two solutions for *τij.* If all chosen derivative terms are positive, the solution is valid; otherwise, we reduce the terms in (3.11) in decreasing order of βk, each time solving (3.11) with the remaining terms until a valid solution is reached. In three dimensions for example, this involves at most three quadratic solves. Algorithm 2 summarizes the solution of the piecewise quadratic equation.

**Algorithm 2: Solution of the piecewise quadratic equation**  
**for** *each dimension x,y,...* **do**  
*% Choosing direction, forward or backward.*  
**if** *both forward and backward neighboring points are in* knownthen Choose the direction with smaller neighboring τ.

### else

Otherwise, choose the direction in known.

### end

*% Choosing order of approximation, 1st or 2nd.* **if** *next neighboring point is in* knownthen Use second order approximation.

### else

Use ﬁrst order approximation.

### end

### end

*% Now all coeﬃcients of* αk *and* βk *of Equation* (3.11) *are known.*  
Calculate (τ1)i,j by solving Equation (3.11).  
**while** *the solution* (τ1)i,j *is not valid* **do**  
Remove the term with largest βk from the remaining terms in (3.11). Calculate (τ1)i,j by solving (3.11) with the remaining terms.

### end

*3.2. The monotonicity of the obtained solution*

It is known that the solution of (1.1) is monotone in the direction of the characteristics. We now show how to enforce the monotonicity of our solution using the FM method for the factored eikonal equation. To set the stage, we ﬁrst consider the FM method for the original non-factored equation.  
In [30] the non-factored ﬁrst order discretization (2.5) is considered. In this case, each newly calculated value *τij* is guaranteed to be larger than its knownneighbors at the time of the calculation. To show this clearly, consider for example that the backward derivative is chosen in the *x* direction. Then,  
*τi−1,j* = *τi,j* −h *τi,j* − *τi−1,j* = *τi,j −hD* −x τ,

################# (3.12)

*h*

*i,j*  
so since *D* −x τ ≥ 0 in the solution of (2.5), we have that *τi,j* ≥ *τi−1,j.* This means that *τi,j* is greater or equal to its known *i,j*  
neighbors. This property insures the monotonicity of the solution. The proof for this appears in [30], but here we can simplify it because unlike [30], we only calculate entries using knownvalues. We state the following lemma:

**Lemma 1.** *Let* τ *be the result of Algorithm 1, for solving the (non-factored) ﬁrst order equation* (2.5). *Then the values of* τ *are mono- tonically non-decreasing in the order in which they are set to* known.

**Proof.** Denote by ? *xk* an element that is set to knownat Step 2 of the k-th iteration of Algorithm 1. Assume by contradiction that there exists two elements ? *xp* and ? *xk,* such that τ( ? *xp)* > τ( ? *xk)* and *p* < *k.* Without loss of generality, assume that *k* is

---

the earliest iteration that this condition is fulﬁlled. Let *k* ¯ < *k* be the iteration in which the value of τ( ? *xk)* is updated in the last time and it is entered to front. We know that ? *x¯* is a neighbor of ? *xk.* By the algorithm, we know that at the k-th ¯ iteration ? *xp* is already set to known, otherwise ? *xk* would *k* have been chosen to knownat the p-th iteration instead of ? *xp.* By the assumption, we know that τ( ? *xp)* ≤ τ( ? *x¯* ), because otherwise ? *xk* would not have been the earliest element to violate the monotonicity. By the property in (3.12), we *k* know that τ( ? *x¯* ) ≤ τ( ? *xk),* and hence we reach τ( ? *xp)* ≤ τ( ? *xk),* which contradicts *k*  
our assumption. ?

Furthermore, the lemma above can be extended for a Fast Marching solution of *any* equation (2.5) such that the dis- cretization operator *D* satisﬁes a monotonicity condition:

# D −x τ ≥ 0 ⇒ τij ≥ τi−1,j and − D +x τ ≥ 0⇒ τij ≥ τi+1,j.

################# (3.13)

*ij*  ij*

The next corollary can be proved using the same arguments as in Lemma 1:

**Corollary 1.** *Let* τ *be the result of Algorithm 1, for solving the Godunov upwind equation* (2.5) *using operators D which satisfy* (3.13). *Then the values of* τ *are monotonically non-decreasing in the order in which they are set to* known.

The condition (3.13) and the corollary above is violated when the second order operators (2.6) are used in (2.5). However, if we look at a single violation, then it is of order *h* 2 . To show this, we examine the backward difference derivative using Taylor expansion:

### ? ?

*τi−1,j* = *τi,j* −h ∂τ + *O(h* 2 ) = *τi,j −hD* −x τ + *O(h* 2 ),

################# (3.14)

∂x *i,j i,j*  
−x  
where *D i,j* is given in (2.6) (the same arguments can be derived for the forward difference derivative). Assuming again that *D* −x τ > 0, this means that each newly calculated *τi,j* is generally greater than its knownneighbors, but may violate that up *i,j*  
to magnitude *O(h* 2 ). Note that if *D* −x τ is suﬃciently bounded away from zero and the second derivative ∂ 2 τ is bounded in [xi−1, ], *i,j* ∂x 2 *xi* then *τi,j >τi−1,j* will be satisﬁed.  
To correct this and obtain a monotone solution using (2.6), one may impose the condition (2.7) for using the second order scheme. If it is not satisﬁed, the scheme reverts to the ﬁrst order scheme, which satisﬁes (3.13). If (2.7) is satisﬁed, then (2.6) does satisfy (3.13), because

*2hD* −x τ = *3τij* − *4τi−1,j* + *τi−2,j* < *3τij* − *3τi−1,j.*

################# (3.15)

*ij*

Note that the condition (2.7) is suggested in [31] but the monotonicity guarantee of the second order scheme is not exam- ined.  
We now examine the monotonicity of the obtained factored solution τ0τ1 when using ﬁrst order operators in (3.9). Suppose that we are calculating (τ1)ij using the backward operator (3.10) in the *x* direction in (3.9). We again start with a Taylor expansion

### ? ? ? ?? ? ? ?

### (τ0τ1)i−1,j = (τ0)ij −h ∂τ0 + O(h 2 ) (τ1)ij −h ∂τ1 + O(h 2 )

∂x ? *i,j* ?

- ? ∂x *i,j*

### = (τ0τ1)ij −h(τ0)ij ∂τ1 −h(τ1)ij ∂τ0 + O(h 2 )

################# (3.16)

∂x *i,j* ∂x *i,j*

# = (τ0τ1)ij −h D ˆ −x τ1 + O(h 2 ),

*ij*

### ? ?

where the last equality is obtained by placing ∂τ1

= (τ1)i,j −(τ1)i−1,j *+O(h).* This expansion shows that if the monotonicity ∂x *i,j h*  
is not obtained, i.e., (τ0τ1)i,j −(τ0τ1)i−1,j < 0, then the non-factored derivative is negative, *D* −x (τ0τ1) < 0, while the factored *ij*  
derivative is non-negative *D* ˆ −x τ1 ≥ 0 (otherwise it is not chosen in (3.9)). This means that the monotonicity may be violated *ij*  
only up to an error of *O(h* 2 ). This holds for both ﬁrst and second order upwind approximations. In fact, (3.16) shows that this is a result of using the chain rule rather than the order of discretization of the operators *D,* ˆ since the monotonicity condition involves the value (τ0)i−1,j, while it does not appear in the discretization scheme. In any case, the magnitude of the error in the monotonicity violation is either of the same or of higher order as the error in τ1, using ﬁrst or second order schemes. Again, if *D* −x τ1 is suﬃciently bounded away from zero and ∂ 2 τ1 is bounded in [xi−1, *xi* ], then the monotonicity *i,j* ∂x 2  
(τ0τ1)i,j > (τ0τ1)i−1,j will be satisﬁed.  
Nevertheless, in our algorithm we may enforce the monotonicity of the obtained solution by reverting to the non-factored operators in cases where the monotonicity is not satisﬁed, or, the factored and non-factored schemes do not agree in sign, for example: *D* ˆ −x τ1 ≥ 0, but *D* −x (τ0τ1) < 0. Note that in this case the numerical derivative is approximately zero, hence the *ij*  
*ij*  
direction of the characteristic is almost parallel to the *y* direction. We apply this change using the same order of derivative which the algorithm chooses to use. That is, if the algorithm chooses a ﬁrst or second order factored stencil, we revert to a

---

standard ﬁrst or second order stencil, respectively. Following Corollary 1, this guarantees the monotonicity of the solution, because we enforce the condition (3.13) at all stages of the algorithm. We note that experimentally, this small correction does not inﬂuence the accuracy of the solution obtained with our algorithm in both ﬁrst and second order schemes in two and three dimensions.

##### 4. Calculation of sensitivities and travel time tomography

Travel time tomography is a useful tool in some Geophysical applications. One way to obtain it is by using the eikonal equation as a forward problem inside an inverse problem [29]. To solve the inverse problem, one should be able to solve (1.1) accurately, and to compute its sensitivities. The works of [13,34] computes the tomography by FS, and require an FS iterative solution for computing the sensitivities. When using the FM algorithm for forward modeling, those are obtained more eﬃciently by a simple solution of a lower triangular linear system [14,3]. More explicitly, let us denote by boldface all the discretized values of the mentioned functions on a grid, and suppose that we set **m** to be the vector of the values of κ( ? *x)* 2 on this grid. By solving (3.9), we get a function τ1(m) for the values of τ1 on the grid. We wish to get a linearization for τ1(m), such that we can predict its change following a small change in **m.** That is, we wish to be able to apply an approximation

τ1(m+δm) ≈ τ1(m)+ **Jδm,** (4.17) where **J** is the sensitivity matrix (or Jacobian) deﬁned by

*Jij* = (∇ *mτ1)ij* = ∂(τ1)i .

################# (4.18) ∂mj

To obtain the sensitivity we ﬁrst rewrite (3.9) in implicit form

f(m,τ1) = ( **D** ˆ *x* τ1) 2 +( **D** ˆ *y* τ1) 2 − **m** = 0,

################# (4.19)

where **D** ˆ *x* = diag(τ0)D *x* + diag(p0) and **D** ˆ *y* = diag(τ0) · **D** *y* + diag(q0) are the matrices that apply the ﬁnite difference derivatives that are chosen by the FM algorithm when applied for **m. p0** and **q0** are the analytical derivatives of τ0 with respect to *x* and *y* on the grid respectively, and diag(x) denotes a diagonal matrix whose diagonal elements are those of the vector **x.** We note that in the points where no derivative is chosen in the solution of (3.9), a zero row is set in the corresponding operator **D.** ˆ Also, at the row of the point source, we set each of **D** ˆ *x* and **D** ˆ *y* to have only one diagonal non-zero element, which equals to the values of **p0** and **q0** at the source. This way, (4.19) is exactly fulﬁlled for **D** ˆ *x* and **D** ˆ *y* and τ1.  
To obtain the sensitivity, we apply the gradient operator to both sides of (4.19), yielding (∇ τ1f)(∇ **mτ1)** + ∇ **mf** = 0, and deﬁne [8]:

### J(m) = ∇ mτ1 = −(∇ τ1f) −1 (∇ mf). (4.20)

This results in  
**J** = (diag(2 **D** ˆ *x* τ1) **D** ˆ *x* + diag(2 **D** ˆ *y* τ1) **D** ˆ *y* ) −1 ,

################# (4.21)

following ∇ **mf** = −I, and since the operators **D** ˆ do not depend on **m** (we deﬁned τ0 and its derivatives so it does not depend on κ).  
The matrix (4.21) can be multiplied with any vector eﬃciently given the order of variables (i, *j)* in which the FM algorithm set their values as known. To apply **J** on an arbitrary vector **x,** i.e. calculate **e** = **Jx,** a linear system **Ae** = **x** can be solved with **A** = **J** −1 (note that **A** is a sparse matrix). The equations of this linear system, which correspond to the rows of **A,** can be approached and solved sequentially in the FM order of variables. Since the FM algorithm uses only known variables for determining each new variable, then when looking at each row *i* of **A,** the non-zero entries in that row (except *i)* correspond to variables that where in knownwhen τ *i* was determined during the FM run. Therefore, if all those variables are known except *i,* then the i-th equation has only one unknown (ei) and can be trivially solved. In other words, if we permute **A** according to the FM order, we get a sparse lower triangular matrix, and the corresponding system can be solved eﬃciently in one forward substitution sweep in *O(n)* operations. For the non-factored equation one may use (4.21) with non-factored operators **D** *x* and **D** *y* instead of the factored ones [14].

*4.1. Travel time tomography using Gauss–Newton*

Assume that we have several sources and receivers set on an open surface, and for each source we have traveltime data **d** *i*  
given in the location of the receivers. Based on these observations we wish to compute the unknown slowness model obs  
of the ground underneath. The inverse problem for this process, called travel time tomography, may be given by  
?

?

### ? ns

min φ(m) = min ?P ? τ *i* (m)− **d** *i* ? 2 + αR(m)

################# (4.22)

*mL<m<mH mL<m<mH* obs *i=1*

---

where

# |∇ τ i | 2 = m( ? x) τ i ( ? xi) = 0 i = 1,...,ns

################# (4.23)

Here τ *i* is the travel time from the point source ? *xi,* and **m(** ? *x)* = κ( ? *x)* 2 is the squared slowness model as in (1.1), only now it is unknown. The operator **P** ? is a projection to the set of receivers that gather the wave information. Here we assume that the information from all sources is available on all the receivers, i.e., the projection operator **P** does not change between sources. R(m) is a regularization term and α > 0 is its balancing parameter. The parameters *mL* and *mH* are positive lower and upper bounds needed for keeping the slowness of the medium physical. We note that the observations **d** *i* can be obs obtained manually from recorded seismic data or by automatic time picking—for more information see [28] and references therein.  
Without the regularization term R(m), the problem (4.22) is ill-posed, i.e., many solutions **m** may ﬁt the predicted travel time to the measured data [37,32]. For this reason, in most cases we cannot expect to exactly recover the true model, but wish to recover a reasonable model by adding prior information using the regularization term R(m). This term aims to promote physical or meaningful solutions that we may expect to see in the recovered model. For example, in seismic exploration, one may expect to recover a layered model of the earth subsurface, hence may choose *R* to promote smooth or piecewise-smooth functions like the total variation regularization term [26].  
There are several ways to solve (4.22), and most of them are gradient-based. Here we focus on Gauss–Newton. This method is computationally favorable here, since its cost is governed by the application of sensitivities, which are easy to obtain using FM. Given an approximation **m** (k) at the k-th iteration, we place (4.17) into (4.22) and get

### 1 ? ns ? ? ?

###### min ?P diag(τ i ) τ i (m (k) )+ J i δm − d i ? 2 + αR(m (k) +δm),

################# (4.24)

δm 2 0 1 obs *i=1*

where **J** *i* is the sensitivity of τ *i* at **m** (k) . Minimizing this approximation for δm leads to computing the gradient 1

- *ns* ? ?

###### ∇ mφ(m (k) ) = (J i ) ? diag(τ i )P P ? diag(τ i )τ i − d i + α ∇ mR(m (k) ).

################# (4.25)

0 0 1 obs *i=1*

We then approximately solve the linear system

**Hδm** = −∇ mφ(m (k) ) where

### ? n

#### H =

###### (J i ) ? diag(τ i )PP ? diag(τ i )J i + α?mR(m (k) ).

0  
0 *i* =1

The linear system is solved using the conjugate gradient method where only matrix vector products are computed. Finally, the model is updated, **m** ← **m** + μδm where μ ≤ 1 is a line search parameter that is chosen such that the objective function is decreased at each iteration.

##### 5. Numerical results: solving the eikonal equation

In this section we demonstrate the FM algorithm using ﬁrst or second order upwind discretization for solving the fac- tored eikonal equation (1.4). We demonstrate both the accuracy of the obtained solution, and the computational cost of calculating it using the FM algorithm. The accuracy of the algorithm is demonstrated by two error norms: one in the maxi- mum norm *l∞,* and one is the mean *l2* norm deﬁned by the standard *l2* norm of the error divided by the square root of the total number of variables. Similarly to [31], we show these two measures to demonstrate the accuracy of the second order scheme. Showing the *l∞* norm of the error for this scheme may result in only ﬁrst order accuracy, because at some points our second order FM algorithm reverts to ﬁrst order operators, which may be picked by the *l∞* norm.  
To demonstrate the eﬃciency of the computation, we measure the time in which the algorithm solves each test. We also show this timing in terms of work-units, where each work unit is deﬁned by the time that it takes to evaluate the equation (1.1) using given central difference gradient stencils (without memory allocation time). We note that the more reliable timings appear for the large scale examples.  
We use analytical examples for media where there is a known analytical solution for a point source located at ? *x0.* The ﬁrst two appear in [6]. We show results for two and three dimensions. Our code is written in Julia language [4] version 0.4.5, and all our tests were calculated on a laptop machine using Windows 10 64 bit OS, with Intel core-i7 2.8 GHz CPU with 32 GB of RAM. Our code is publicly available in [https :/ /github .com /JuliaInv /FactoredEikonalFastMarching](https://github.com/JuliaInv/FactoredEikonalFastMarching.jl) .jl. We do not enforce the monotonicity in the results below, but those can be enforced in our package. The three test cases are listed below.

---

![](assets_j/img-0785.jpg)

**Fig. 3.** The 2D slowness model κ(?x) of the three test cases and the corresponding contours of the 2D solutions.

*Test case 1: constant gradient of squared slowness*

### κ 2 ( ? x) = s 2 + 2a e1 ? ·( ? x−? x0),

0

In this test case we set:

################# (5.26)

where *e1* ? = (1, 0) is a unit vector, and · is the standard dot product. The parameters *a, s0,* the domain and the source location are chosen differently in 2D and 3D. The corresponding exact solution is given by  
*τexact(* ? *x)* = *S* ¯ 2 σ − 1 *a* 2 (σ 3 ),

################# (5.27)

6 where

### S ¯ 2 ( ? x) = s 2 +a e1 ? ·( ? x−? x0)

################# (5.28)

- 0 ? ? −1

### σ 2 ( ? x) = S ¯ 2 + S ¯ 4 −a 2?? x− x0 ? ?2 2?? x− x0 ? ? 2 .

################# (5.29)

Figs. 3(a) and 3(d) show the model κ for this test case with the chosen parameters for 2D.

*Test case 2: constant gradient of velocity*  
In this test case we set:

### ? ? −1

### κ( ? x) = 1 +a e1 ? ·( ? x−? x0)

################# (5.30)

### s 0

where again *e1* ? = (1, 0), · is the dot product, and the parameters *a, s0,* the domain and the source location are chosen differently in 2D and 3D. The exact solution is given by  
?  
?  
*τexact(* ? *x)* = 1 acosh 1+ 1 *s0a* 2 κ( ? x)?? x−? *x0* ? 2 .

################# (5.31)

*a*  
2  
Figs. 3(b) and 3(e) show the model κ for this test case with the chosen parameters for 2D.  
*Test case 3: Gaussian factor* In this test case we choose a function for τ *exact* and multiply it by τ0 to get *τexact.* We choose τ1 as a Gaussian function centered around a point *x1:* ?

1 ?

?

# τ exact ( ? x) = 1 exp −( ? x−? x1) T ?( ? x−? x1) + 1

################# (5.32)

1 2 2  
where ? is a 2 × 2 or 3 × 3 positive diagonal matrix. As before, the parameters ? *x1* and ?, the domain and the source location *x0* ? are chosen differently in 2D and 3D. Here κ( ? *x)* is deﬁned by (3.8), with τ0 being the distance function. Figs. 3(c) and 3(f) show the model κ for this test with the chosen parameters for 2D.

*5.1. Two dimensional tests*

Now we show results for the two dimensional versions of the tests mentioned above. For all tests in 2D we choose the domain to be [0, 4] ×[0, 8], while *h* = *hx* = *hy* varies from large to small.

---

### Table 1

Results for 2D constant gradient of squared slowness (test case 1). The error measures are in the [l∞, mean *l2* ] norms.

*h n* 1 *st* order

error in τ

2 *nd* order

time (work) error in τ  
time (work)

1/40 161× 321  
[3.71e−03, 9.42e−04] 0.05 s (217) [9.33e−05, 9.26e−06] 0.05 s (202) 1/80 321× 641  
[1.85e−03, 4.69e−04] 0.19 s (199) [3.30e−05, 2.21e−06] 0.20 s (209) 1/160 641× 1281 [9.22e−04, 2.34e−04] 0.85 s (217) [1.14e−05, 5.32e−07] 0.85 s (218) 1/320 1281× 2561 [4.60e−04, 1.17e−04] 3.89 s (266) [4.06e−06, 1.28e−07] 3.84 s (262) 1/640 2561× 5121 [2.30e−04, 5.83e−05] 16.4 s (278) [1.47e−06, 3.12e−08] 17.1 s (289) 1/1280 5121× 10241 [1.15e−04, 2.92e−05] 76.6 s (316) [5.18e−07, 7.64e−09] 77.5 s (320)

### Table 2

Results for the 2D constant gradient of velocity (test case 2). The error measures are in the [l∞, mean *l2* ] norms.

*h n* 1 *st* order

error in τ

2 *nd* order

time (work) error in τ  
time (work)

1/40 161× 321  
[2.66e−02, 1.01e−02] 0.05 s (205) [4.86e−04, 2.90e−04] 0.05 s (236) 1/80 321× 641  
[1.32e−02, 5.05e−03] 0.21 s (221) [1.67e−04, 7.38e−05]  
0.20 s (206) 1/160 641× 1281 [6.59e−03, 2.52e−03] 0.87 s (223) [5.18e−05, 1.85e−05] 0.86 s (221) 1/320 1281× 2561 [3.29e−03, 1.26e−03] 3.80 s (259) [1.90e−05, 4.61e−06] 3.88 s (265) 1/640 2561× 5121 [1.65e−03, 6.28e−04] 16.2 s (274) [6.58e−06, 1.15e−06] 16.6 s (280) 1/1280 5121× 10241 [8.22e−04, 3.14e−04] 73.8 s (304) [2.28e−06, 2.86e−07] 74.6 s (307)

### Table 3

Results for the 2D Gaussian factor test case (test case 3). The error measures are in the [l∞, mean *l2* ] norms.

*h n* 1 *st* order

error in τ

2 *nd* order

time (work) error in τ  
time (work)

1/40 161× 321  
[6.15e−03, 3.86e−03] 0.05 s (205) [1.60e−04, 5.94e−05] 0.05 s (236) 1/80 321× 641  
[3.07e−03, 1.93e−03]  
0.21 s (221) [3.85e−05, 1.56e−05] 0.20 s (206) 1/160 641× 1281 [1.54e−03, 9.67e−04] 0.87 s (223) [1.08e−05, 4.03e−06] 0.86 s (221) 1/320 1281× 2561 [7.68e−04, 4.83e−04] 3.80 s (259) [3.18e−06, 1.04e−06] 3.88 s (265) 1/640 2561× 5121 [3.84e−04, 2.42e−04] 16.2 s (275) [9.59e−07, 2.66e−07] 16.6 s (280) 1/1280 5121× 10241 [1.92e−04, 1.21e−04] 73.8 s (304) [2.99e−07, 6.88e−08] 74.6 s (307)

*Test case 1: constant gradient of squared slowness* For this 2D setting, we use the parameters *a* = −0.4, *s0* = 2.0, and the source location is ? *x0* = (0, 4). Table 1 summarizes the results for this test. On the ﬁrst order section we see a typical ﬁrst order convergence rate in both error norms. As the mesh size increases by two in each direction, the errors drop by a factor of two. In the second order section we see the typical behavior of the FM algorithm. At some points, ﬁrst order operators are used, and hence the error at those locations dominates the *l∞* norm. Still, we observe much better convergence compared to the ﬁrst order *l∞,* only it is not of second order. In the mean *l2* norm we see typical second order convergence—as the mesh size increases by two in each direction, the errors drop by a factor of four. In any case, the errors in the second order columns are much smaller than those in the ﬁrst order columns.  
In terms of computational cost, the 2D FM algorithm exhibits favorable timings and work counts. Except the small cases, the cost of the algorithm is comparable to 200–300 function evaluations using standard difference stencils. This is maintained for all the considered mesh sizes. The difference in the computational cost between using ﬁrst and second order schemes is only about 10% of execution time.

*Test case 2: constant gradient of velocity* For this 2D setting, we use the parameters *a* = 1.0, *s0* = 2.0, and the location of the source is again at ? *x0* = (0, 4). Table 2 summarizes the results for this test. The results here are almost identical to the previous test case. The ﬁrst order columns show typical ﬁrst order convergence in both error norms. The second order columns show better convergence and exhibits second order convergence in the mean *l2* norm column. The computational costs columns show timings which are almost identical to the previous test case.

*Test case 3: Gaussian factor* For this setting, we use the parameters ? = diag(0.1, 0.4), ? *x1* = (4/3, 2) (ﬂoored to the closest grid point), and the source is located in the point ? *x0* = (1, 2). Table 3 summarizes the results for this test. Again we see ﬁrst order convergence at the ﬁrst order columns in both norms. On the second order columns we again see faster convergence, and in the mean *l2* norm column we see convergence rate that is close to second order—the error decreases by a factor of about 3.9 when the mesh size increases by a factor of 2 in each dimension. Again we see similar behavior in the computational cost columns.  
We now wish to better illustrate the difference between the accuracy of the ﬁrst order scheme and the second order scheme. First, Fig. 4 shows contours of the exact and approximate solutions in certain regions of the domain for the second and third test cases. It is clear that the ﬁrst order approximation is less accurate than the second order one. Next, Fig. 5

---

![](assets_j/img-0478.jpg)

**Fig. 4.** Contours of small regions in the exact, ﬁrst order accurate and second order accurate travel times τ using *h* = 0.1. The exact solution appears in black line. The ﬁrst order approximation appears in dotted red line and the second order approximation appears in a dashed blue line mostly right with the exact solution. (For interpretation of the references to color in this ﬁgure legend, the reader is referred to the web version of this article.)

![](assets_j/img-0479.jpg)

**Fig. 5.** The accuracy of the FM approximations in logarithmic scales for the 2D cases. Red plots are used for ﬁrst order approximations, blue plots for second order approximations; dotted lines for *l∞* error norm and solid for mean *l2* norm. Black circles denote a reference for exact second order convergence rate. (For interpretation of the references to color in this ﬁgure legend, the reader is referred to the web version of this article.)

shows plots of the errors in Tables 1–3 in logarithmic scales for both *h* and the error norms, where the order of conver- gence determines the slope of the lines. It is clear that in all cases, using the second order scheme we get second order convergence in mean *l2* norm, and a bit more than ﬁrst order convergence in the *l∞* norm.

*5.2. Three dimensional tests*

We now show results for the same type of tests in three dimensions. For all the 3D tests we choose the domain to be [0, 0.8] ×[0, 1.6] ×[0, 1.6], and *h* = *hx* = *hy* = *hz* varies.

*Test case 1: constant gradient of squared slowness* For the 3D version of this test case we use the parameters *a* = −1.65, and *s0* = 2.0, and the source is located at (0, 0.8, 0.8). Table 4 summarizes the results for this test case. Again, like in two dimensions, the ﬁrst order version of FM yields ﬁrst order convergence rate in both error norms. When using the second order scheme we get a super-linear convergence rate in the *l∞* column, and second order convergence in the mean *l2* column. We note that in 3D the FM algorithm reverts to ﬁrst order scheme on 2D manifolds, where the derivative in each dimension switches sign, and not on 1D curves as in 2D.  
In terms of computational cost, it is obvious that the 3D problem is much more expensive than the 2D one. The compu- tational cost in seconds per grid-point in 3D is about 3 times higher than the corresponding cost in 2D. That is because the treatment of each grid point is more expensive (more neighbors and more derivative directions), and the number of grid points that are processed inside the heap is much larger (a 2D manifold of points compared to a 1D curve). As a result, when we normalize the timing by the cost of a 3D “work-unit” (evaluation of (1.1) in 3D), the cost grows a little when the mesh-size grows. Still, solving the problem requires 200–500 work units. Again, using the ﬁrst and second order schemes requires similar computational effort in our 3D implementation of the FM algorithm.

*Test case 2: constant gradient of velocity*

For the 3D version of this test case we use the parameters *a* = 1.0, and *s0* = 2.0, and the source is located at (0, 0.8, 0.8). Table 5 summarizes the results for this test case. As in the previous case, we get ﬁrst order convergence when using the ﬁrst order scheme, in both error norms. Again, when using the second order scheme we get a super-linear convergence rate in the *l∞* column, and second order convergence in the mean *l2* column.

*Test case 3: Gaussian factor* For this 3D test case we use the parameters ? = diag(0.2, 0.4, 0.1), ? *x1* = (0.4, 1.6 , 0.4) (ﬂoored to the closest grid point), and the source is located in the point ? *x0* = (0.2, 0.4, 0.4). Table 6 summarizes the 3 results for this

---

### Table 4

Results for the 3D constant gradient of squared slowness test case (test case 1). The error measures are in the [l∞, mean *l2* ] norms. *h n* 1 *st* order  
error in τ

2 *nd* order  
time (work) error in τ  
time (work) 1/20 17× 33× 33  
[5.41e−03, 1.46e−03] 0.04 s (236) [5.63e−4, 1.49e−04]  
0.04 s (234) 1/40 33× 65× 65  
[2.64e−03, 7.05e−04] 0.30 s (230) [2.00e−04, 3.52e−05] 0.32 s (235) 1/80 65× 129× 129 [1.30e−03, 3.46e−04] 2.88 s (332) [6.99e−05, 7.82e−06] 2.90 s (334) 1/160 129× 257× 257 [6.41e−04, 1.72e−04] 28.7 s (427) [2.51e−05, 1.68e−06] 29.0 s (432) 1/320 257× 513× 513 [3.19e−04, 8.55e−05] 264 s (481) [8.78e−06, 3.53e−07] 272 s (497)

### Table 5

Results for the 3D constant gradient of velocity test case (test case 2). The error measures are in the [l∞, mean *l2* ] norms. *h n* 1 *st* order  
error in τ  
1/20 17× 33× 33  
[1.35e−02, 5.04e−03]

2 *nd* order  
time (work) error in τ  
time (work) 0.04 s (237) [2.34e−03, 9.36e−04] 0.04 s (255) 1/40 33× 65× 65  
[6.24e−03, 2.44e−03] 0.31 s (234) [5.12e−04, 1.72e−04]  
0.32 s (236) 1/80 65× 129× 129 [3.00e−03, 1.20e−03] 2.86 s (330) [1.70e−04, 3.82e−05] 2.89 s (334) 1/160 129× 257× 257 [1.47e−03, 5.99e−04] 27.6 s (411) [5.42e−05, 9.33e−06] 28.9 s (430) 1/320 257× 513× 513 [7.30e−04, 2.99e−04] 263 s (481) [1.95e−05, 2.29e−06] 271 s (496)

### Table 6

Results for the 3D Gaussian factor test case (test case 3). The error measures are in the [l∞, mean *l2* ] norms. *h n* 1 *st* order  
error in τ

2 *nd* order  
time (work) error in τ  
time (work) 1/20 17× 33× 33  
[7.53e−03, 3.26e−03] 0.04 s (230) [3.65e−04, 1.27e−04]  
0.04 s (229) 1/40 33× 65× 65  
[3.69e−03, 1.56e−03] 0.33 s (245) [9.95e−05, 2.85e−05] 0.34 s (253) 1/80 65× 129× 129 [1.83e−03, 7.62e−04] 2.77 s (319) [3.22e−05, 7.50e−06] 2.80 s (323) 1/160 129× 257× 257 [9.11e−04, 3.77e−04] 26.4 s (393) [1.06e−05, 2.06e−06] 27.2 s (405) 1/320 257× 513× 513 [4.54e−04, 1.87e−04] 267 s (487) [3.54e−06, 5.66e−07] 276 s (504)

![](assets_j/img-0468.jpg)

**Fig. 6.** The accuracy of the FM approximations in logarithmic scales for the 3D cases. Red and blue plots are used for ﬁrst and second order approximations, respectively; dotted lines for *l∞* error norm and solid for mean *l2* norm. Black circles denote an exact second order convergence rate. (For interpretation of the references to color in this ﬁgure legend, the reader is referred to the web version of this article.)

test case. The results are similar to the previous test case in both the convergence (ﬁrst/second order using *l∞/l2* norms) and computational costs in seconds and work units.  
Again we wish to demonstrate the order accuracy of the FM approximations using the ﬁrst and second order schemes. Fig. 6 shows the results in Tables 4–6 in logarithmic scales. Like in 2D, we observe second order convergence rate when the error is measure in mean *l2* norm. However, because the second order stencil reduces to ﬁrst order stencil in two dimensional manifolds, the error in *l∞* norm is higher in 3D than it is in 2D.

##### 6. Numerical results: travel time tomography

In this section we demonstrate a solution of travel time tomography using synthetic travel time data dobs for a 2D and SEG/EAGE salt model given in [1] and presented in Fig. 7(a), using a 256 ×128 grid that represents an area of approximately 13.5 km × 4.2 km. We choose 51 equally distanced sources locations on the open surface (that is, they are located every 5 pixels on the top row), and 256 receivers (located in every pixel on the top row). We note that to have a reasonable solution using the ﬁrst arrivals for the inverse problem under this setup, the velocity in the interior has to be larger than

---

![](assets_j/img-0459.jpg)

**Fig. 7.** 2D travel time tomography experiment, grid size 256× 128. Velocities are given in km/sec.

![](assets_j/img-0460.jpg)

**Fig. 8.** Initial and ﬁnal data and residuals in the source-receiver domain.

that on the surface. This is to guarantee that the ﬁrst arrival rays obtained on the surface actually come from the interior but not only travel along the surface. To dobs we add white Gaussian noise with standard deviation of 0.01 × mean(\|dobs \|). To ﬁt the model to the data, we minimize (4.22) using Gauss–Newton (we perform 10 iterations, where in each we apply 8 CG steps for the Gauss–Newton direction problem). We use the general-propose inversion package [27], which is freely available in [https :/ /github .com /JuliaInv /jInv.jl,](https://github.com/JuliaInv/jInv.jl) together with our FM package mentioned earlier. For that, we ﬁrst generate an initial slowness model **m** (0) = *mref* , whose velocity model shown in Fig. 7(b). This corresponds to a velocity ﬁeld with a constant gradient in the *y* direction, similarly to the model in Fig. 3(b). To bound **m** from above and from below throughout the minimization, we invert for an auxiliary variable **m** ? and use the following scalar bounded bijective mapping that prevents **m** from being below *mL* or above *mH:*

### ? ? ? ?

*mbound(m* ? ) = *mH* −mL · tanh  
2

### · m ? − mH +mL + 1 +mL.

2 *mH* −mL 2

That is, instead of minimizing (4.22) as is, we minimize ?

?

#### ? ns

### min φ(m ? ) = min ?P ? τ i (mbound(m ? ))− d i ? 2 + αR(m ? )

################# (6.33)

**m** ? **m** ? *i=1* obs

subject to the same constraints in (4.23). For the regularization *R* use a simple discrete central-differences Laplacian, and apply it for **m** ? ; that is

*R(m* ? ) = 1 (m ? − **m** ?

### ) ? ?h(m ? − m ? ),

2 *ref ref*  
where **m** ?  
is the model such that *mbound(m* ? ) = *mref* . For ?h we use Neumann boundary conditions, since those lead to *r ef ref*  
an effect of an automatic salt ﬂooding, which is a popular way to treat salt bodies. We set the regularization parameter to be α = 0.5. We note that other choices of *mref* and regularization terms may deﬁnitely be suitable here, but are beyond the scope of this paper. Fig. 7(c) shows the result model of the Gauss–Newton minimization, and Fig. 8 presents the initial and ﬁnal data and data residuals. In particular, Fig. 8(d) shows that the ﬁnal residual mostly contains the added Gaussian noise. Fig. 9 shows that the misﬁt was indeed reduced throughout the iterations, until the reduction stalls and the misﬁt reﬂect the noise level.  
To demonstrate our algorithm in 3D, we use a 3D version of the same SEG/EAGE model, presented in Fig. 10(a), using a 256 × 256 × 128 grid that represents a volume of 13.5 km × 13.5 km × 4.2 km. We choose 144 equally distanced sources locations on the open surface, located every 23 pixels on the top surface, and 256 ×256 receivers located on the top surface.

---

![](assets_j/img-0439.jpg)

**Fig. 9.** Convergence history of the inversion.

![](assets_j/img-0440.jpg)

**Fig. 10.** 3D travel time tomography experiment, grid size 256× 256× 128. Velocities are given in km/sec.

We use the same parameters as in the 2D experiment (bound function, regularization, initial 3D model, added noise to the data, number of iterations etc.). Fig. 10(b) shows the result of the inversion. Similarly to the 2D case, the top part of the model is recovered quite well, while a “salt ﬂooding” effect is evident in the bottom part of the model. We performed the inversion using a machine with two Intel(R) Xeon(R) E5-2670 v3 processors with 128 GB of RAM. Using 24 cores, we applied the inversion in approximately 15 hours, and the highest memory footprint of the algorithm reached around 30 GB.

##### 7. Conclusions

In this paper we developed a Fast Marching algorithm for the factored eikonal equation, which in many cases yields a more accurate solution of the travel time than the original equation. Similarly to the original FM algorithm, our version solves the factored problem by exploiting the monotonicity of the solution along the characteristics. Our algorithm is capable of solving the problem using both ﬁrst and second order schemes. The advantages of our algorithm are (1) its favorable guaranteed *O(n* logn) running time, and (2) the easily computed sensitivity matrices for solving the inverse (factored) eikonal equation.

##### Acknowledgements

The research leading to these results has received funding from the European Union’s – Seventh Framework Programme (FP7/2007-2013) under grant agreement no 623212 – MC Multiscale Inversion.

##### References

[1] [F. Aminzadeh, B. Jean, T. Kunz, 3-D Salt and Overthrust Models, Society of Exploration Geophysicists, 1997.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib616D696E7A616465683139393733s1)  
[2] [J.A. Bærentzen, On the implementation of fast marching methods for 3D lattices, Tech. Report IMM-TR-2001-13, Informatics and Mathematical Mod-  
elling, Technical University of Denmark, DTU, 2001, Richard Petersens Plads, Building 321, DK- 2800 Kgs. Lyngby.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib494D4D323030312D30383431s1)   
[3] [A. Benaichouche, M. Noble, A. Gesret, First arrival traveltime tomography using the fast marching method and the adjoint state technique, in: 77th  
EAGE Conference Proceedings, 2015.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib62656E616963686F75636865323031356669727374s1)   
[4] [J. Bezanzon, S. Karpinski, V. Shah, A. Edelman, Julia: a fast dynamic language for technical computing, in: Lang. NEXT, Apr. 2012.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib4A756C6961s1)  
[5] [M.G. Crandall, P.-L. Lions, Viscosity solutions of Hamilton–Jacobi equations, Trans. Am. Math. Soc. 277 (1983) 1–42.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6372616E64616C6C31393833766973636F73697479s1)  
[6] [S. Fomel, S. Luo, H. Zhao, Fast sweeping method for the factored eikonal equation, J. Comput. Phys. 228 (2009) 6440–6455.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib666F6D656C3230303966617374s1)  
[7] [P.A. Gremaud, C.M. Kuster, Computational study of fast methods for the eikonal equation, SIAM J. Sci. Comput. 27 (2006) 1803–1816.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6772656D61756432303036636F6D7075746174696F6E616Cs1)  
[8] [E. Haber, Computational Methods in Geophysical Electromagnetics, vol. 1, SIAM, 2014.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib686162657232303134636F6D7075746174696F6E616Cs1)  
[9] [E. Haber, S. MacLachlan, A fast method for the solution of the Helmholtz equation, J. Comput. Phys. 230 (2011) 4403–4418.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib68616265723230313166617374s1)  
[10] [C.Y. Kao, S. Osher, J. Qian, Lax–Friedrichs sweeping scheme for static Hamilton–Jacobi equations, J. Comput. Phys. 196 (2004) 367–391.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6B616F323030346C6178s1)

---

[11] [R. Kimmel, J.A. Sethian, Computing geodesic paths on manifolds, Proc. Natl. Acad. Sci. 95 (1998) 8431–8435.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6B696D6D656C31393938636F6D707574696E67s1)  
[12] [S. Leung, J. Qian, R. Burridge, Eulerian Gaussian beams for high-frequency wave propagation, Geophysics 72 (2007) SM61–SM76.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6C65756E673230303765756C657269616Es1)  
[13] [S. Leung, J. Qian, et al., An adjoint state method for three-dimensional transmission traveltime tomography using ﬁrst-arrivals, Commun. Math. Sci. 4  
(2006) 249–266.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6C65756E673230303661646A6F696E74s1)   
[14] [S. Li, A. Vladimirsky, S. Fomel, First-break traveltime tomography with the double-square-root eikonal equation, Geophysics 78 (2013) U89–U101.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6C69323031336669727374s1)  
[15] [S. Luo, J. Qian, Factored singularities and high-order Lax–Friedrichs sweeping schemes for point-source traveltimes and amplitudes, J. Comput. Phys.  
230 (2011) 4742–4755.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6C756F32303131666163746F726564s1)   
[16] [S. Luo, J. Qian, Fast sweeping methods for factored anisotropic eikonal equations: multiplicative and additive factors, J. Sci. Comput. 52 (2012) 360–382.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6C756F3230313266617374s1) [17] [S. Luo, J. Qian, R. Burridge, Fast Huygens sweeping methods for Helmholtz equations in inhomogeneous media in the high frequency regime, J. Comput.  
Phys. 270 (2014) 378–401.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6C756F3230313466617374s1)   
[18] [S. Luo, J. Qian, R. Burridge, High-order factorization based high-order hybrid fast sweeping methods for point-source eikonal equations, SIAM J. Numer.  
Anal. 52 (2014) 23–44.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib4C6F755169616E427572726964676532303134s1)   
[19] [S. Luo, J. Qian, H. Zhao, Higher-order schemes for 3d ﬁrst-arrival traveltimes and amplitudes, Geophysics 77 (2012) T47–T56.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6C756F32303132686967686572s1)  
[20] [M. Noble, A. Gesret, N. Belayouni, Accurate 3-d ﬁnite difference computation of traveltimes in strongly heterogeneous media, Geophys. J. Int. 199  
(2014) 1572–1585.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib6E6F626C65323031346163637572617465s1)   
[21] [A. Pica, et al., Fast and accurate ﬁnite-difference solutions of the 3d eikonal equation parametrized in celerity, in: 67th Ann. Internat. Mtg, Soc. of Expl.  
Geophys, 1997, pp. 1774–1777.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib706963613139393766617374s1)   
[22] [J. Qian, W.W. Symes, An adaptive ﬁnite-difference method for traveltimes and amplitudes, Geophysics 67 (2002) 167–176.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib7169616E323030326164617074697665s1)  
[23] [J. Qian, Y.-T. Zhang, H.-K. Zhao, A fast sweeping method for static convex Hamilton–Jacobi equations, J. Sci. Comput. 31 (2007) 237–271.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib7169616E3230303766617374s1)  
[24] [N. Rawlinson, M. Sambridge, Wave front evolution in strongly heterogeneous layered media using the fast marching method, Geophys. J. Int. 156 (2004)  
631–647.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib7261776C696E736F6E3230303477617665s1)   
[25] [E. Rouy, A. Tourin, A viscosity solutions approach to shape-from-shading, SIAM J. Numer. Anal. 29 (1992) 867–884.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib726F757931393932766973636F73697479s1)  
[26] [L.I. Rudin, S. Osher, E. Fatemi, Nonlinear total variation based noise removal algorithms, Physica D 60 (1992) 259–268.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib727564696E313939326E6F6E6C696E656172s1)  
[27] L. Ruthotto, E. Treister, E. Haber, jInv – a ﬂexible Julia package for PDE parameter estimation, 2016, submitted for publication.  
[28] [C. Saragiotis, T. Alkhalifah, S. Fomel, Automatic traveltime picking using instantaneous traveltime, Geophysics 78 (2013) T53–T58.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib7361726167696F746973323031336175746F6D61746963s1)  
[29] [A. Sei, W.W. Symes, et al., Gradient calculation of the traveltime cost function without ray tracing, in: 65th Ann. Internat. Mtg., Expanded Abstracts,  
Soc. Expl. Geophys, 1994, pp. 1351–1354.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib736569313939346772616469656E74s1)   
[30] [J.A. Sethian, A fast marching level set method for monotonically advancing fronts, Proc. Natl. Acad. Sci. 93 (1996) 1591–1595.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib7365746869616E3139393666617374s1)  
[31] [J.A. Sethian, Fast marching methods, SIAM Rev. 41 (1999) 199–235.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib7365746869616E3139393966617374s1)  
[32] [E. Somersalo, J. Kaipio, Statistical and Computational Inverse Problems, Appl. Math. Sci., vol. 160, 2004.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib736F6D657273616C6F32303034737461746973746963616Cs1)  
[33] [A. Spira, R. Kimmel, An eﬃcient solution to the eikonal equation on parametric manifolds, Interfaces Free Bound. 6 (2004) 315–328.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib737069726132303034656666696369656E74s1)  
[34] [C. Taillandier, M. Noble, H. Chauris, H. Calandra, First-arrival traveltime tomography based on the adjoint-state method, Geophysics 74 (2009) WCB1–  
WCB10.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib7461696C6C616E64696572323030396669727374s1)   
[35] [Y.-H.R. Tsai, L.-T. Cheng, S. Osher, H.-K. Zhao, Fast sweeping algorithms for a class of Hamilton–Jacobi equations, SIAM J. Numer. Anal. 41 (2003)  
673–694.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib747361693230303366617374s1)   
[36] [J.N. Tsitsiklis, Eﬃcient algorithms for globally optimal trajectories, IEEE Trans. Autom. Control 40 (1995) 1528–1538.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib7473697473696B6C697331393935656666696369656E74s1)  
[37] [C.R. Vogel, Computational Methods for Inverse Problems, Frontiers Appl. Math., vol. 23, SIAM, Philadelphia, 2002.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib766F67656C32303032636F6D7075746174696F6E616Cs1)  
[38] [H. Zhao, A fast sweeping method for eikonal equations, Math. Comput. 74 (2005) 603–627.](http://refhub.elsevier.com/S0021-9991 16 30355-2/bib7A68616F3230303566617374s1)

